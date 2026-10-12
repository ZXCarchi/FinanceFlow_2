from calendar import monthrange
from collections import defaultdict
from datetime import date
from decimal import Decimal, ROUND_HALF_UP, ROUND_DOWN
from django.db.models import Sum
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.translation import gettext as _
from .models import Category, Transaction, BudgetLimit

D = Decimal
DEFAULT_CATEGORIES = [
    ('Food','food','expense','🍜','#ff9f43'), ('Transport','transport','expense','🚇','#4f7cff'),
    ('Housing','housing','expense','🏠','#6c5ce7'), ('Utilities','utilities','expense','💡','#7f8c8d'), ('Entertainment','entertainment','expense','🎬','#ef5da8'),
    ('Education','education','expense','🎓','#00a8a8'), ('Health','health','expense','🧡','#f25f5c'),
    ('Shopping','shopping','expense','🛍️','#8d6cab'), ('Subscriptions','subscriptions','expense','🔁','#5d6d7e'),
    ('Salary','salary','income','💼','#13a471'), ('Part-time work','part-time','income','🧑‍💼','#3282b8'), ('Scholarship','scholarship','income','📚','#1f9d8a'),
    ('Freelance','freelance','income','💻','#2f80ed'), ('Other','other','both','✨','#7b8794'),
]
ESSENTIAL_CODES = {'housing','utilities','food','transport','health','education'}
CATEGORY_EN = {code:name for name,code,*_rest in DEFAULT_CATEGORIES}


def q2(v):
    return Decimal(v or 0).quantize(D('0.01'), rounding=ROUND_HALF_UP)


def create_default_categories(user):
    for name, code, kind, icon, color in DEFAULT_CATEGORIES:
        Category.objects.get_or_create(user=user, code=code, defaults={'name':name,'kind':kind,'icon':icon,'color':color,'is_default':True})


def current_month_bounds(today=None):
    today = today or timezone.localdate()
    start = today.replace(day=1)
    end = today.replace(day=monthrange(today.year, today.month)[1])
    return start, end


def totals_for(user, start=None, end=None):
    qs = user.transactions.all()
    if start: qs = qs.filter(date__gte=start)
    if end: qs = qs.filter(date__lte=end)
    inc = qs.filter(kind='income').aggregate(v=Sum('amount'))['v'] or D('0')
    exp = qs.filter(kind='expense').aggregate(v=Sum('amount'))['v'] or D('0')
    return q2(inc), q2(exp)


def total_balance(user):
    return q2(sum((w.current_balance() for w in user.wallets.filter(is_active=True)), D('0')))


def category_spending(user, start=None, end=None):
    qs = user.transactions.filter(kind='expense')
    if start: qs = qs.filter(date__gte=start)
    if end: qs = qs.filter(date__lte=end)
    rows = qs.values('category_id','category__name','category__code','category__icon','category__color').annotate(total=Sum('amount')).order_by('-total')
    total = sum((r['total'] or D('0') for r in rows), D('0'))
    out = []
    for r in rows:
        amount = q2(r['total'])
        out.append({**r, 'amount':amount, 'pct': round(float(amount / total * 100),1) if total else 0, 'label': r.get('category__name') or _('Uncategorized')})
    return out


def monthly_trend(user, months=6, today=None):
    today = today or timezone.localdate()
    points=[]
    y,m=today.year,today.month
    for offset in range(months-1, -1, -1):
        mm=m-offset; yy=y
        while mm<=0: mm+=12; yy-=1
        start=date(yy,mm,1); end=date(yy,mm,monthrange(yy,mm)[1])
        inc,exp=totals_for(user,start,end)
        points.append({'label':date_format(start,'M'),'income':float(inc),'expense':float(exp)})
    return points


def allocate_amount(total, percentages):
    """Allocate whole cents exactly using largest fractional remainders."""
    exact = [total * value / D('100') for value in percentages]
    amounts = [value.quantize(D('.01'), rounding=ROUND_DOWN) for value in exact]
    pennies = int((total - sum(amounts)) * 100)
    order = sorted(range(len(exact)), key=lambda i: exact[i] - amounts[i], reverse=True)
    for index in order[:pennies]:
        amounts[index] += D('.01')
    return amounts


def smart_plan(user, today=None):
    anchor = today or timezone.localdate()
    real_today = timezone.localdate()
    start, end = current_month_bounds(anchor)
    income, expenses = totals_for(user, start, end)
    profile = getattr(user, 'profile', None)
    expected = q2(profile.expected_monthly_income if profile else 0)
    planning_income = max(income, expected)
    percentages = [D(str(getattr(profile, field, default))) for field, default in
                   [('essential_pct', 50), ('lifestyle_pct', 30), ('savings_pct', 20)]]
    essential_amount, lifestyle_amount, savings_amount = allocate_amount(planning_income, percentages)

    elapsed = max(0, min(real_today.day if start <= real_today <= end else (end.day if real_today > end else 0), end.day))
    actual_income, actual_expenses = totals_for(user, start, min(real_today, end)) if elapsed else (D(0), D(0))
    forecast_records = user.transactions.filter(wallet__is_active=True, date__range=(start, end))
    active_income = forecast_records.filter(kind='income').aggregate(v=Sum('amount'))['v'] or D(0)
    active_expenses = forecast_records.filter(kind='expense').aggregate(v=Sum('amount'))['v'] or D(0)
    elapsed_expenses = forecast_records.filter(kind='expense', date__lte=real_today).aggregate(v=Sum('amount'))['v'] or D(0)
    avg_daily = elapsed_expenses / D(elapsed) if elapsed else D(0)
    projected_expenses = max(active_expenses, q2(avg_daily * D(end.day)))
    # A month-end estimate starts with that month's opening ledger balance.
    opening = sum((wallet.opening_balance for wallet in user.wallets.filter(is_active=True)), D(0))
    previous = user.transactions.filter(wallet__is_active=True, date__lt=start)
    opening += (previous.filter(kind='income').aggregate(v=Sum('amount'))['v'] or D(0))
    opening -= (previous.filter(kind='expense').aggregate(v=Sum('amount'))['v'] or D(0))
    projected_balance = q2(opening + max(active_income, expected) - projected_expenses)
    remaining_expected_income = max(D(0), planning_income - actual_income)

    cat = category_spending(user, start, end)
    spend_map = {row['category_id']: row['amount'] for row in cat}
    alerts = []
    for limit in user.budget_limits.select_related('category'):
        spent = spend_map.get(limit.category_id, D(0))
        pct = spent / limit.monthly_limit * 100 if limit.monthly_limit else D(0)
        if pct >= 100:
            alerts.append({'level': 'danger', 'title': _('Budget limit reached'),
                           'text': _('%(category)s has used %(percent)s%% of its monthly limit.') % {'category': limit.category.name, 'percent': round(pct)}})
        elif pct >= 80:
            alerts.append({'level': 'warn', 'title': _('Budget limit almost reached'),
                           'text': _('%(category)s has used %(percent)s%% of its monthly limit.') % {'category': limit.category.name, 'percent': round(pct)}})
    if planning_income and expenses > planning_income * D('.8'):
        alerts.append({'level': 'warn', 'title': _('High monthly spending'),
                       'text': _('You have spent more than 80% of your planned monthly income.')})
    if not planning_income:
        alerts.append({'level': 'info', 'title': _('Set your monthly income'),
                       'text': _('Add income or enter expected monthly income in settings to calculate your plan.')})
    return {
        'income': income, 'expenses': expenses, 'planning_income': q2(planning_income), 'balance': total_balance(user),
        'essential_pct': percentages[0], 'lifestyle_pct': percentages[1], 'savings_pct': percentages[2],
        'essential_amount': essential_amount, 'lifestyle_amount': lifestyle_amount, 'savings_amount': savings_amount,
        'avg_daily': q2(avg_daily), 'projected_expenses': projected_expenses, 'projected_balance': projected_balance,
        'remaining_expected_income': q2(remaining_expected_income), 'category_targets': [], 'alerts': alerts,
    }


def dashboard_snapshot(user):
    start,end=current_month_bounds()
    income,expenses=totals_for(user,start,end)
    balance=total_balance(user)
    savings_rate=round(float((income-expenses)/income*100),1) if income else 0
    return {
        'income':income,'expenses':expenses,'balance':balance,'savings_rate':savings_rate,
        'categories':category_spending(user,start,end)[:6], 'recent':user.transactions.select_related('wallet','category')[:7],
        'goals':user.goals.all()[:3], 'plan':smart_plan(user), 'trend':monthly_trend(user),
    }


def coach_reply(user, text):
    t=(text or '').strip().lower()
    plan=smart_plan(user)
    top=category_spending(user,*current_month_bounds())
    currency=getattr(getattr(user,'profile',None),'currency','PLN')
    fmt=lambda v: f"{q2(v):,.2f} {currency}".replace(',', ' ')
    if any(k in t for k in ['save','saving','oszcz','odkład','odklad']):
        return _('A practical target for this month is %(amount)s (%(percent)s%% of planned income). Start by moving this amount to savings soon after income arrives.') % {'amount':fmt(plan['savings_amount']),'percent':plan['savings_pct']}
    if any(k in t for k in ['cut','reduce','spend','wydat','ogranicz','ciąć','ciac']):
        if top:
            return _('Your largest spending category this month is %(category)s at %(amount)s. Review the biggest transactions there first, then set a monthly category limit.') % {'category':top[0].get('label') or _('Uncategorized'),'amount':fmt(top[0]['amount'])}
        return _('Add a few expenses first. Then I can identify the categories with the strongest saving potential.')
    if any(k in t for k in ['balance','left','remaining','saldo','zosta']):
        return _('Your current total wallet balance is %(balance)s. At the current spending pace, the estimated month-end balance is %(forecast)s.') % {'balance':fmt(plan['balance']),'forecast':fmt(plan['projected_balance'])}
    if any(k in t for k in ['budget','plan','budż','budz']):
        return _('Your current smart plan is %(essential)s%% essentials, %(lifestyle)s%% flexible spending and %(savings)s%% savings. You can edit these percentages in the planner.') % {'essential':plan['essential_pct'],'lifestyle':plan['lifestyle_pct'],'savings':plan['savings_pct']}
    return _('This month you have %(income)s income and %(expenses)s expenses. Ask me how much to save, what to reduce, how much is left, or for a budget plan.') % {'income':fmt(plan['income']),'expenses':fmt(plan['expenses'])}
