"""Same-origin JSON API. Every write is CSRF protected by Django middleware."""
import csv
import json
import re
from calendar import monthrange
from datetime import date
from decimal import Decimal, InvalidOperation
from functools import wraps

from django import forms
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models, transaction
from django.http import HttpResponse, JsonResponse
from django.middleware.csrf import get_token
from django.utils import timezone
from django.utils.text import slugify

from accounts.models import Profile
from .models import BudgetLimit, Category, RecurringOccurrence, RecurringPayment, SavingsGoal, Transaction, Wallet
from .services import category_spending, coach_reply, create_default_categories, current_month_bounds, q2, smart_plan, total_balance, totals_for


class APIError(Exception):
    def __init__(self, message, status=400, errors=None):
        self.message, self.status, self.errors = message, status, errors


def failure(message, status=400, errors=None):
    body = {'ok': False, 'error': message}
    if errors:
        body['errors'] = errors
    return JsonResponse(body, status=status)


def endpoint(methods, authenticated=True):
    def decorate(view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            if request.method not in methods:
                response = failure('Method not allowed.', 405)
                response['Allow'] = ', '.join(methods)
                return response
            if authenticated and not request.user.is_authenticated:
                return failure('Please sign in to continue.', 401)
            try:
                response = view(request, *args, **kwargs)
            except APIError as exc:
                response = failure(exc.message, exc.status, exc.errors)
            except ValidationError as exc:
                response = failure('Please check the highlighted fields.', errors=exc.message_dict if hasattr(exc, 'message_dict') else {'__all__': exc.messages})
            except IntegrityError:
                response = failure('This record conflicts with existing data. Refresh and try again.', 409)
            response['Cache-Control'] = 'no-store'
            return response
        return wrapped
    return decorate


def payload(request):
    if request.content_type != 'application/json':
        raise APIError('Send a JSON request body.', 415)
    try:
        data = json.loads(request.body or b'{}', parse_float=Decimal,
                          parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Non-finite number')))
    except (ValueError, UnicodeDecodeError, InvalidOperation):
        raise APIError('The request must contain valid JSON.')
    if not isinstance(data, dict):
        raise APIError('The request body must be an object.')
    return data


def only_fields(data, allowed):
    unknown = set(data) - set(allowed)
    if unknown:
        raise APIError('Unknown fields were supplied.', errors={key: ['This field cannot be changed.'] for key in sorted(unknown)})


def text_field(data, key, required=True, limit=150):
    value = data.get(key, '')
    if not isinstance(value, str):
        raise ValidationError({key: 'Enter text.'})
    value = value.strip()
    if (required and not value) or len(value) > limit:
        raise ValidationError({key: f'Enter between 1 and {limit} characters.'})
    return value


def email_field(data):
    try:
        return forms.EmailField(max_length=150).clean(text_field(data, 'email', limit=150)).lower()
    except ValidationError as exc:
        raise ValidationError({'email': exc.messages})


def user_data(user):
    return {'id': user.id, 'email': user.email or user.username, 'first_name': user.first_name}


def profile_data(profile):
    return {'currency': profile.currency, 'expected_monthly_income': str(q2(profile.expected_monthly_income))}


def month_bounds(value=None):
    if value is None:
        return current_month_bounds()
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}', value):
        raise ValidationError({'month': 'Use YYYY-MM.'})
    try:
        year, month = map(int, value.split('-'))
        # Keep six-month trend and PostgreSQL/Python date operations in a usable range.
        if not 1900 <= year <= 9998:
            raise ValueError
        start = date(year, month, 1)
        return start, date(year, month, monthrange(year, month)[1])
    except ValueError:
        raise ValidationError({'month': 'Choose a valid month between 1900 and 9998.'})


COLLECTIONS = {
    'wallets': (Wallet, ('name', 'wallet_type', 'opening_balance', 'is_active')),
    'categories': (Category, ('name', 'kind', 'icon', 'color')),
    'transactions': (Transaction, ('kind', 'title', 'amount', 'wallet', 'category', 'date', 'note')),
    'goals': (SavingsGoal, ('name', 'target_amount', 'saved_amount', 'target_date', 'icon')),
    'budgets': (BudgetLimit, ('category', 'monthly_limit')),
    'recurring': (RecurringPayment, ('title', 'amount', 'kind', 'wallet', 'category', 'day_of_month', 'is_active')),
}


def serialize(obj):
    if isinstance(obj, Wallet):
        return {'id': obj.id, 'name': obj.name, 'wallet_type': obj.wallet_type, 'opening_balance': str(q2(obj.opening_balance)), 'balance': str(q2(obj.current_balance())), 'is_active': obj.is_active}
    if isinstance(obj, Category):
        return {key: getattr(obj, key) for key in ('id', 'name', 'code', 'kind', 'icon', 'color')}
    if isinstance(obj, SavingsGoal):
        return {'id': obj.id, 'name': obj.name, 'target_amount': str(q2(obj.target_amount)), 'saved_amount': str(q2(obj.saved_amount)), 'target_date': obj.target_date.isoformat() if obj.target_date else None, 'icon': obj.icon, 'progress': obj.progress(), 'remaining': str(q2(obj.remaining()))}
    if isinstance(obj, BudgetLimit):
        return {'id': obj.id, 'category': obj.category_id, 'monthly_limit': str(q2(obj.monthly_limit))}
    data = {'id': obj.id, 'title': obj.title, 'amount': str(q2(obj.amount)), 'kind': obj.kind, 'wallet': obj.wallet_id, 'category': obj.category_id}
    if isinstance(obj, Transaction):
        data.update(date=obj.date.isoformat(), note=obj.note)
    else:
        data.update(day_of_month=obj.day_of_month, is_active=obj.is_active)
    return data


def clean_assignment(obj, data, allowed, user):
    only_fields(data, allowed)
    for name, raw in data.items():
        field = obj._meta.get_field(name)
        if isinstance(field, models.ForeignKey):
            if raw is None and field.null:
                setattr(obj, name, None)
                continue
            if not isinstance(raw, int) or isinstance(raw, bool) or raw < 1:
                raise ValidationError({name: 'Choose a valid record.'})
            related = field.remote_field.model.objects.filter(pk=raw, user=user).first()
            if related is None:
                raise ValidationError({name: 'Choose one of your own records.'})
            setattr(obj, name, related)
            continue
        if isinstance(field, models.BooleanField):
            valid_type = isinstance(raw, bool)
        elif isinstance(field, models.DecimalField):
            valid_type = isinstance(raw, (str, int, Decimal)) and not isinstance(raw, bool)
            if isinstance(raw, str):
                # Mobile decimal keyboards commonly enter a comma in European locales.
                raw = raw.strip().replace(',', '.')
        elif isinstance(field, models.IntegerField):
            valid_type = isinstance(raw, int) and not isinstance(raw, bool)
        elif isinstance(field, models.DateField):
            valid_type = (raw is None and field.null) or (isinstance(raw, str) and bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}', raw)))
        else:
            valid_type = isinstance(raw, str)
            if valid_type:
                raw = raw.strip()
        if not valid_type:
            raise ValidationError({name: 'Enter a valid value of the expected type.'})
        try:
            value = field.clean(raw, obj)
        except (ValidationError, ValueError, InvalidOperation, OverflowError) as exc:
            messages = exc.messages if isinstance(exc, ValidationError) else ['Enter a valid value.']
            raise ValidationError({name: messages})
        setattr(obj, name, value)


@endpoint(['GET'], authenticated=False)
def session(request):
    return JsonResponse({'authenticated': request.user.is_authenticated, 'user': user_data(request.user) if request.user.is_authenticated else None, 'csrfToken': get_token(request)})


@endpoint(['POST'], authenticated=False)
def register(request):
    data = payload(request)
    only_fields(data, ['email', 'first_name', 'password', 'password_confirm', 'currency'])
    email = email_field(data)
    first_name = text_field(data, 'first_name')
    password = data.get('password')
    if not isinstance(password, str) or not 1 <= len(password) <= 256:
        raise ValidationError({'password': 'Enter a password no longer than 256 characters.'})
    if 'password_confirm' in data and data['password_confirm'] != password:
        raise ValidationError({'password_confirm': 'Passwords do not match.'})
    if User.objects.filter(username__iexact=email).exists():
        raise ValidationError({'email': 'An account with this email already exists.'})
    user = User(username=email, email=email, first_name=first_name)
    try:
        validate_password(password, user)
    except ValidationError as exc:
        raise ValidationError({'password': exc.messages})
    profile = Profile(user=user, onboarding_complete=True)
    if 'currency' in data:
        clean_assignment(profile, {'currency': data['currency']}, ['currency'], user)
    with transaction.atomic():
        user.set_password(password)
        user.full_clean()
        user.save()
        profile.user = user
        profile.full_clean()
        profile.save()
        create_default_categories(user)
        Wallet.objects.create(user=user, name='Main account')
    auth_login(request, user)
    return JsonResponse({'ok': True, 'user': user_data(user), 'csrfToken': get_token(request)}, status=201)


@endpoint(['POST'], authenticated=False)
def login(request):
    data = payload(request)
    only_fields(data, ['email', 'password'])
    email = email_field(data)
    password = data.get('password')
    if not isinstance(password, str) or len(password) > 256:
        raise APIError('Email or password is incorrect.', 401)
    # Older accounts may have preserved the case of their email address.
    existing = User.objects.filter(username__iexact=email).only('username').first()
    user = authenticate(request, username=existing.username if existing else email, password=password)
    if user is None:
        raise APIError('Email or password is incorrect.', 401)
    Profile.objects.get_or_create(user=user)
    auth_login(request, user)
    return JsonResponse({'ok': True, 'user': user_data(user), 'csrfToken': get_token(request)})


@endpoint(['POST'])
def logout(request):
    auth_logout(request)
    return JsonResponse({'ok': True, 'csrfToken': get_token(request)})


@endpoint(['GET'])
def state(request):
    start, end = month_bounds(request.GET.get('month'))
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)
    income, expenses = totals_for(user, start, end)
    spending = category_spending(user, start, end)
    spent_by_category = {row['category_id']: row['amount'] for row in spending}
    budgets = []
    for item in user.budget_limits.all():
        spent = spent_by_category.get(item.category_id, Decimal(0))
        budgets.append({**serialize(item), 'spent': str(q2(spent)), 'remaining': str(q2(item.monthly_limit - spent)), 'percent': round(float(spent / item.monthly_limit * 100), 1) if item.monthly_limit else 0})
    trend = []
    for offset in range(5, -1, -1):
        month_index = start.year * 12 + start.month - 1 - offset
        year, month = divmod(month_index, 12)
        point_start, point_end = current_month_bounds(date(year, month + 1, 1))
        point_income, point_expense = totals_for(user, point_start, point_end)
        trend.append({'month': point_start.strftime('%Y-%m'), 'label': point_start.strftime('%b'), 'income': str(point_income), 'expense': str(point_expense)})
    return JsonResponse({
        'month': start.strftime('%Y-%m'), 'user': user_data(user), 'profile': profile_data(profile),
        'wallets': [serialize(item) for item in user.wallets.order_by('id')],
        'categories': [serialize(item) for item in user.categories.all()],
        'transactions': [serialize(item) for item in user.transactions.filter(date__range=(start, end)).select_related('wallet', 'category')],
        'goals': [serialize(item) for item in user.goals.order_by('id')],
        'budgets': budgets, 'recurring': [serialize(item) for item in user.recurring_payments.order_by('day_of_month', 'id')],
        'summary': {'income': str(income), 'expenses': str(expenses), 'balance': str(total_balance(user)), 'net': str(q2(income - expenses)), 'savings_rate': round(float((income - expenses) / income * 100), 1) if income else 0},
        'trend': trend,
        'category_spending': [{'category': row['category_id'], 'name': row['category__name'] or 'Uncategorized', 'icon': row['category__icon'] or '•', 'color': row['category__color'] or '#94a3b8', 'amount': str(row['amount']), 'percent': row['pct']} for row in spending],
        'plan': smart_plan(user, start),
    })


@endpoint(['POST', 'PATCH', 'DELETE'])
def resource(request, collection, pk=None):
    if collection not in COLLECTIONS:
        raise APIError('Not found.', 404)
    if (pk is None and request.method != 'POST') or (pk is not None and request.method == 'POST'):
        raise APIError('Method not allowed.', 405)
    model, allowed = COLLECTIONS[collection]
    with transaction.atomic():
        if pk is not None:
            obj = model.objects.select_for_update().filter(pk=pk, user=request.user).first()
            if obj is None:
                raise APIError('Record not found.', 404)
        else:
            obj = model(user=request.user)
        if request.method == 'DELETE':
            if isinstance(obj, Wallet) and (obj.transactions.exists() or obj.recurring_payments.exists()):
                raise APIError('This account has records. Archive it instead of deleting it.', 409)
            if isinstance(obj, Category) and (obj.transactions.exists() or obj.recurringpayment_set.exists() or obj.limits.exists()):
                raise APIError('This category is in use. Reassign its records before deleting it.', 409)
            obj.delete()
            return JsonResponse({'ok': True})
        data = payload(request)
        clean_assignment(obj, data, allowed, request.user)
        if isinstance(obj, Category) and not obj.pk:
            obj.code = ('custom-' + slugify(obj.name))[:50]
        obj.full_clean()
        obj.save()
    return JsonResponse({'ok': True, 'item': serialize(obj)}, status=201 if request.method == 'POST' else 200)


@endpoint(['PATCH'])
def settings(request):
    data = payload(request)
    only_fields(data, ['first_name', 'currency', 'expected_monthly_income'])
    with transaction.atomic():
        profile, _ = Profile.objects.get_or_create(user=request.user)
        profile = Profile.objects.select_for_update().get(pk=profile.pk)
        if 'first_name' in data:
            request.user.first_name = text_field(data, 'first_name')
            request.user.full_clean()
        clean_assignment(profile, {key: value for key, value in data.items() if key != 'first_name'}, ['currency', 'expected_monthly_income'], request.user)
        profile.full_clean()
        profile.save()
        if 'first_name' in data:
            request.user.save(update_fields=['first_name'])
    return JsonResponse({'ok': True, 'profile': profile_data(profile), 'user': user_data(request.user)})


@endpoint(['PATCH'])
def plan(request):
    data = payload(request)
    with transaction.atomic():
        profile, _ = Profile.objects.get_or_create(user=request.user)
        profile = Profile.objects.select_for_update().get(pk=profile.pk)
        clean_assignment(profile, data, ['essential_pct', 'lifestyle_pct', 'savings_pct'], request.user)
        profile.full_clean()
        profile.save()
    request.user.profile = profile
    return JsonResponse({'ok': True, 'plan': smart_plan(request.user)})


@endpoint(['POST'])
def recurring_apply(request):
    data = payload(request)
    only_fields(data, ['month'])
    start, end = month_bounds(data.get('month'))
    today = timezone.localdate()
    if start > today:
        raise ValidationError({'month': 'Future recurring payments cannot be applied yet.'})
    created = 0
    # Lock rules in a stable order; the unique receipt also protects concurrent requests.
    with transaction.atomic():
        for item in request.user.recurring_payments.select_for_update().filter(is_active=True, wallet__is_active=True).order_by('id'):
            tx_date = start.replace(day=min(item.day_of_month, end.day))
            if tx_date > today:
                continue
            occurrence, is_new = RecurringOccurrence.objects.get_or_create(recurring=item, month=start)
            if not is_new:
                continue
            item.full_clean()
            tx = Transaction(user=request.user, wallet=item.wallet, category=item.category, kind=item.kind, amount=item.amount, title=item.title, date=tx_date, note='Created from recurring payment')
            tx.full_clean()
            tx.save()
            occurrence.transaction = tx
            occurrence.save(update_fields=['transaction'])
            created += 1
    return JsonResponse({'ok': True, 'created': created})


def csv_text(value):
    value = str(value)
    return "'" + value if value.lstrip().startswith(('=', '+', '-', '@', '\t', '\r', '\n')) else value


@endpoint(['GET'])
def export(request):
    start, end = month_bounds(request.GET.get('month'))
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="financeflow-{start:%Y-%m}.csv"'
    response.write('\ufeff')
    writer = csv.writer(response)
    writer.writerow(['Date', 'Type', 'Title', 'Category', 'Wallet', 'Amount', 'Currency', 'Note'])
    profile, _ = Profile.objects.get_or_create(user=request.user)
    for tx in request.user.transactions.filter(date__range=(start, end)).select_related('category', 'wallet'):
        writer.writerow([tx.date, tx.kind, csv_text(tx.title), csv_text(tx.category.name if tx.category else ''), csv_text(tx.wallet.name), str(q2(tx.amount)), profile.currency, csv_text(tx.note)])
    return response


@endpoint(['POST'])
def coach(request):
    data = payload(request)
    only_fields(data, ['message'])
    message = text_field(data, 'message', limit=1000)
    return JsonResponse({'reply': coach_reply(request.user, message)})
