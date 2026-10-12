import csv
import io
import json
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.test import Client, TestCase
from django.utils import timezone

from accounts.models import Profile
from .models import BudgetLimit, Category, RecurringOccurrence, RecurringPayment, SavingsGoal, Transaction, Wallet
from .services import allocate_amount, smart_plan


class APITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('owner@example.com', email='owner@example.com', password='LongPass!9842', first_name='Owner')
        self.profile = Profile.objects.create(user=self.user)
        self.wallet = Wallet.objects.create(user=self.user, name='Main', opening_balance=Decimal('100.00'))
        self.category = Category.objects.create(user=self.user, name='Food', code='food')
        self.other = User.objects.create_user('other@example.com', password='LongPass!9842')
        Profile.objects.create(user=self.other)
        self.other_wallet = Wallet.objects.create(user=self.other, name='Private')
        self.other_category = Category.objects.create(user=self.other, name='Private')
        self.client.force_login(self.user)

    def send(self, method, url, data=None, client=None):
        return getattr(client or self.client, method)(url, json.dumps(data or {}), content_type='application/json')

    def tx_data(self, **overrides):
        return {'title': 'Lunch', 'kind': 'expense', 'amount': '10.50', 'wallet': self.wallet.pk, 'category': self.category.pk, 'date': timezone.localdate().isoformat(), **overrides}

    def test_anonymous_cannot_read_finances(self):
        self.client.logout()
        response = self.client.get('/api/state')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['ok'], False)

    def test_session_and_csrf_protection(self):
        client = Client(enforce_csrf_checks=True)
        session = client.get('/api/session').json()
        self.assertFalse(session['authenticated'])
        self.assertIn('csrfToken', session)
        response = self.send('post', '/api/login', {'email': 'owner@example.com', 'password': 'LongPass!9842'}, client)
        self.assertEqual(response.status_code, 403)
        response = client.post('/api/login', json.dumps({'email': 'owner@example.com', 'password': 'LongPass!9842'}), content_type='application/json', HTTP_X_CSRFTOKEN=session['csrfToken'])
        self.assertEqual(response.status_code, 200)
        new_token = response.json()['csrfToken']
        self.assertNotEqual(new_token, session['csrfToken'])
        response = client.post('/api/wallets', json.dumps({'name': 'Cash'}), content_type='application/json')
        self.assertEqual(response.status_code, 403)
        response = client.post('/api/wallets', json.dumps({'name': 'Cash'}), content_type='application/json', HTTP_X_CSRFTOKEN=new_token)
        self.assertEqual(response.status_code, 201)

    def test_register_password_validation_and_default_data(self):
        self.client.logout()
        payload = {'email': 'new@example.com', 'first_name': 'New', 'password': '12345678'}
        response = self.send('post', '/api/register', payload)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.filter(username='new@example.com').exists())
        payload['password'] = 'QuiteUnique!497834'
        response = self.send('post', '/api/register', payload)
        self.assertEqual(response.status_code, 201, response.content)
        new_user = User.objects.get(username='new@example.com')
        self.assertTrue(new_user.check_password(payload['password']))
        self.assertEqual(new_user.wallets.count(), 1)
        self.assertEqual(new_user.categories.count(), 14)
        self.assertEqual(new_user.profile.essential_pct, Decimal('50'))
        self.assertTrue(self.client.get('/api/session').json()['authenticated'])

    def test_password_confirmation_and_email_case_duplicate(self):
        self.client.logout()
        data = {'email': 'OWNER@EXAMPLE.COM', 'first_name': 'Owner', 'password': 'QuiteUnique!497834'}
        self.assertEqual(self.send('post', '/api/register', data).status_code, 400)
        data.update(email='unique@example.com', password_confirm='different')
        self.assertEqual(self.send('post', '/api/register', data).status_code, 400)

    def test_transaction_crud_recalculates_balance_and_chart(self):
        response = self.send('post', '/api/transactions/', self.tx_data())
        self.assertEqual(response.status_code, 201, response.content)
        pk = response.json()['item']['id']
        state = self.client.get('/api/state').json()
        self.assertEqual(state['summary']['balance'], '89.50')
        self.assertEqual(state['summary']['expenses'], '10.50')
        self.assertEqual(state['category_spending'][0]['percent'], 100)
        self.assertEqual(state['wallets'][0]['balance'], '89.50')
        response = self.send('patch', f'/api/transactions/{pk}', {'amount': '20.00'})
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(self.client.get('/api/state').json()['summary']['balance'], '80.00')
        self.assertEqual(self.send('delete', f'/api/transactions/{pk}').status_code, 200)
        state = self.client.get('/api/state').json()
        self.assertEqual(state['summary']['balance'], '100.00')
        self.assertEqual(state['category_spending'], [])

    def test_decimal_comma_is_accepted_from_mobile_keyboards(self):
        response = self.send('post', '/api/transactions/', self.tx_data(amount='10,50'))
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(response.json()['item']['amount'], '10.50')
        response = self.send('patch', '/api/plan', {
            'essential_pct': '50,25', 'lifestyle_pct': '29,75', 'savings_pct': '20,00',
        })
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()['plan']['essential_pct'], '50.25')

    def test_ownership_on_foreign_keys_and_object_operations(self):
        other_goal = SavingsGoal.objects.create(user=self.other, name='Secret', target_amount=100)
        cases = [self.tx_data(wallet=self.other_wallet.pk), self.tx_data(category=self.other_category.pk)]
        for data in cases:
            self.assertEqual(self.send('post', '/api/transactions', data).status_code, 400)
        for method in ['patch', 'delete']:
            self.assertEqual(self.send(method, f'/api/goals/{other_goal.pk}', {'saved_amount': '10'}).status_code, 404)
        self.assertNotIn('Secret', self.client.get('/api/state').content.decode())
        self.assertNotIn('Private', self.client.get('/api/state').content.decode())

    def test_transaction_rejects_nonpositive_nonfinite_and_precision_errors(self):
        for amount in ['0', '-1', 'NaN', 'Infinity', '-Infinity', '1e100', '1.001', True, [], {}, None]:
            with self.subTest(amount=amount):
                response = self.send('post', '/api/transactions', self.tx_data(amount=amount))
                self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(Transaction.objects.count(), 0)

    def test_validation_all_collections(self):
        invalid = [
            ('wallets', {'name': 'Main', 'opening_balance': 'Infinity'}),
            ('wallets', {'name': 'Main', 'is_active': 'false'}),
            ('categories', {'name': 'Food', 'color': 'red'}),
            ('goals', {'name': 'Trip', 'target_amount': '0'}),
            ('goals', {'name': 'Trip', 'target_amount': '100', 'saved_amount': '-1'}),
            ('budgets', {'category': self.category.pk, 'monthly_limit': '-1'}),
            ('recurring', {'title': 'Rent', 'amount': '10', 'wallet': self.wallet.pk, 'day_of_month': 0}),
            ('recurring', {'title': 'Rent', 'amount': '10', 'wallet': self.wallet.pk, 'day_of_month': 32}),
            ('recurring', {'title': 'Rent', 'amount': '10', 'wallet': self.wallet.pk, 'day_of_month': 1.5}),
            ('transactions', self.tx_data(date='2026-02-30')),
            ('transactions', self.tx_data(date='0001-01-01')),
            ('transactions', self.tx_data(date='9999-01-01')),
        ]
        for collection, data in invalid:
            with self.subTest(collection=collection, data=data):
                response = self.send('post', f'/api/{collection}', data)
                self.assertEqual(response.status_code, 400, response.content)

    def test_kind_must_match_category(self):
        response = self.send('post', '/api/transactions', self.tx_data(kind='income'))
        self.assertEqual(response.status_code, 400)
        self.assertIn('category', response.json()['errors'])
        both = Category.objects.create(user=self.user, name='Both', kind='both')
        self.assertEqual(self.send('post', '/api/transactions', self.tx_data(kind='income', category=both.pk)).status_code, 201)
        response = self.send('patch', f'/api/categories/{both.pk}', {'kind': 'expense'})
        self.assertEqual(response.status_code, 400)

    def test_unknown_fields_and_wrong_json_rejected(self):
        self.assertEqual(self.send('post', '/api/wallets', {'name': 'Cash', 'user': self.other.pk}).status_code, 400)
        for body in ['[]', 'null', '{"amount":NaN}', 'bad json']:
            self.assertEqual(self.client.post('/api/wallets', body, content_type='application/json').status_code, 400)
        self.assertEqual(self.client.post('/api/wallets', {'name': 'Cash'}).status_code, 415)
        self.assertEqual(self.client.get('/api/wallets').status_code, 405)

    def test_month_filter_totals_and_trend(self):
        Transaction.objects.create(user=self.user, wallet=self.wallet, kind='income', title='October', amount=200, date=date(2025, 10, 1))
        Transaction.objects.create(user=self.user, wallet=self.wallet, kind='expense', title='November', amount=50, date=date(2025, 11, 1))
        result = self.client.get('/api/state?month=2025-10').json()
        self.assertEqual(result['summary']['income'], '200.00')
        self.assertEqual(result['summary']['expenses'], '0.00')
        self.assertEqual(len(result['transactions']), 1)
        self.assertEqual(len(result['trend']), 6)
        self.assertEqual(result['trend'][-1]['month'], '2025-10')
        self.assertEqual(result['trend'][-1]['income'], '200.00')
        for month in ['2026-13', 'x', '0001-01', '2026-1']:
            self.assertEqual(self.client.get('/api/state', {'month': month}).status_code, 400)

    def test_future_transactions_do_not_change_current_balance(self):
        tomorrow = timezone.localdate() + timedelta(days=1)
        Transaction.objects.create(user=self.user, wallet=self.wallet, kind='income', title='Tomorrow', amount=500, date=tomorrow)
        self.assertEqual(self.wallet.current_balance(), Decimal('100.00'))
        self.assertEqual(self.client.get('/api/state').json()['summary']['balance'], '100.00')

    def test_plan_zero_income_and_manual_percentages(self):
        empty = self.client.get('/api/state').json()['plan']
        self.assertEqual(empty['planning_income'], '0.00')
        self.assertEqual(empty['essential_amount'], '0.00')
        self.send('patch', '/api/settings', {'expected_monthly_income': '0.01'})
        result = self.send('patch', '/api/plan', {'essential_pct': '33.33', 'lifestyle_pct': '33.33', 'savings_pct': '33.34'})
        self.assertEqual(result.status_code, 200, result.content)
        plan = result.json()['plan']
        self.assertEqual(sum(Decimal(plan[key]) for key in ['essential_pct', 'lifestyle_pct', 'savings_pct']), Decimal('100'))
        self.assertEqual(sum(Decimal(plan[key]) for key in ['essential_amount', 'lifestyle_amount', 'savings_amount']), Decimal('.01'))
        self.assertEqual(plan['savings_amount'], '0.01')
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.essential_pct, Decimal('33.33'))

    def test_plan_invalid_updates_do_not_change_saved_values(self):
        for data in [{'essential_pct': 51}, {'essential_pct': -1, 'lifestyle_pct': 81}, {'essential_pct': 'NaN'}, {'essential_pct': '50.001'}, {'savings_pct': 'Infinity'}]:
            self.assertEqual(self.send('patch', '/api/plan', data).status_code, 400)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.essential_pct, Decimal('50'))

    def test_allocations_one_cent_and_zero_share_never_negative(self):
        for total, percentages in [('.01', ['50', '50', '0']), ('.02', ['25', '75', '0']), ('999.99', ['33.33', '33.33', '33.34'])]:
            allocations = allocate_amount(Decimal(total), list(map(Decimal, percentages)))
            self.assertEqual(sum(allocations), Decimal(total))
            self.assertTrue(all(value >= 0 for value in allocations))
            if percentages[-1] == '0':
                self.assertEqual(allocations[-1], 0)

    def test_settings_validation_is_atomic(self):
        for data in [{'expected_monthly_income': '-1'}, {'expected_monthly_income': 'NaN'}, {'currency': 'BAD'}, {'first_name': 'Changed', 'expected_monthly_income': '1e100'}]:
            response = self.send('patch', '/api/settings', data)
            self.assertEqual(response.status_code, 400, response.content)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Owner')
        response = self.send('patch', '/api/settings', {'first_name': 'New name', 'currency': 'EUR', 'expected_monthly_income': '1234.56'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['profile']['expected_monthly_income'], '1234.56')

    def test_budget_overspend_and_unique_category(self):
        data = {'category': self.category.pk, 'monthly_limit': '10'}
        self.assertEqual(self.send('post', '/api/budgets', data).status_code, 201)
        self.assertEqual(self.send('post', '/api/budgets', data).status_code, 400)
        self.send('post', '/api/transactions', self.tx_data(amount='15'))
        result = self.client.get('/api/state').json()['budgets'][0]
        self.assertEqual(result['percent'], 150)
        self.assertEqual(result['remaining'], '-5.00')

    def test_goal_overfunding_and_null_date(self):
        result = self.send('post', '/api/goals', {'name': 'Trip', 'target_amount': '100', 'saved_amount': '120', 'target_date': None})
        self.assertEqual(result.status_code, 201)
        self.assertEqual(result.json()['item']['progress'], 100)
        self.assertEqual(result.json()['item']['remaining'], '0.00')
        self.assertEqual(self.wallet.current_balance(), Decimal('100.00'))

    def test_deleting_used_records_requires_explicit_cleanup(self):
        self.send('post', '/api/transactions', self.tx_data())
        self.assertEqual(self.send('delete', f'/api/wallets/{self.wallet.pk}').status_code, 409)
        self.assertEqual(self.send('delete', f'/api/categories/{self.category.pk}').status_code, 409)
        self.assertEqual(self.send('patch', f'/api/wallets/{self.wallet.pk}', {'is_active': False}).status_code, 200)
        self.assertEqual(self.send('post', '/api/transactions', self.tx_data()).status_code, 400)

    def test_recurring_idempotent_receipts_and_same_named_rules(self):
        for _ in range(2):
            RecurringPayment.objects.create(user=self.user, wallet=self.wallet, category=self.category, title='Same', amount=5, day_of_month=31)
        with patch('finance.api.timezone.localdate', return_value=date(2024, 3, 1)):
            response = self.send('post', '/api/recurring/apply', {'month': '2024-02'})
            self.assertEqual(response.status_code, 200, response.content)
            self.assertEqual(response.json()['created'], 2)
            self.assertEqual(set(Transaction.objects.values_list('date', flat=True)), {date(2024, 2, 29)})
            self.assertEqual(self.send('post', '/api/recurring/apply', {'month': '2024-02'}).json()['created'], 0)
            Transaction.objects.all().delete()
            self.assertEqual(RecurringOccurrence.objects.count(), 2)
            self.assertEqual(self.send('post', '/api/recurring/apply', {'month': '2024-02'}).json()['created'], 0)
            self.assertEqual(self.send('post', '/api/recurring/apply', {'month': '2024-04'}).status_code, 400)

    def test_recurring_skips_not_due_and_archived_accounts(self):
        RecurringPayment.objects.create(user=self.user, wallet=self.wallet, title='Late', amount=10, day_of_month=31)
        with patch('finance.api.timezone.localdate', return_value=date(2024, 2, 15)):
            self.assertEqual(self.send('post', '/api/recurring/apply', {'month': '2024-02'}).json()['created'], 0)
        self.wallet.is_active = False
        self.wallet.save()
        self.assertEqual(self.send('post', '/api/recurring/apply', {'month': '2024-02'}).json()['created'], 0)

    def test_forecast_excludes_future_month_and_future_daily_average(self):
        with patch('finance.services.timezone.localdate', return_value=date(2024, 10, 10)):
            Transaction.objects.create(user=self.user, wallet=self.wallet, title='Actual', amount=10, kind='expense', date=date(2024, 10, 1))
            Transaction.objects.create(user=self.user, wallet=self.wallet, title='Planned', amount=20, kind='expense', date=date(2024, 10, 20))
            Transaction.objects.create(user=self.user, wallet=self.wallet, title='Later month', amount=1000, kind='expense', date=date(2024, 11, 1))
            plan = smart_plan(self.user)
            self.assertEqual(plan['avg_daily'], Decimal('1'))
            self.assertEqual(plan['projected_expenses'], Decimal('31'))
            self.assertEqual(plan['projected_balance'], Decimal('69'))

    def test_forecast_uses_only_active_wallets(self):
        archived = Wallet.objects.create(user=self.user, name='Archived', is_active=False)
        Transaction.objects.create(user=self.user, wallet=archived, title='Old account income', amount=500, kind='income')
        plan = smart_plan(self.user)
        self.assertEqual(plan['income'], Decimal('500'))
        self.assertEqual(plan['projected_balance'], Decimal('100'))

    def test_renamed_category_used_by_coach(self):
        self.category.name = 'Groceries'
        self.category.save()
        self.send('post', '/api/transactions', self.tx_data())
        response = self.send('post', '/api/coach', {'message': 'What should I reduce?'})
        self.assertIn('Groceries', response.json()['reply'])

    def test_csv_export_filtered_and_formula_neutralized(self):
        Transaction.objects.create(user=self.user, wallet=self.wallet, title='=1+1', note=' +SUM(A1)', kind='expense', amount=10, date=date(2024, 10, 1))
        Transaction.objects.create(user=self.user, wallet=self.wallet, title='Outside month', kind='expense', amount=10, date=date(2024, 11, 1))
        result = self.client.get('/api/export?month=2024-10')
        self.assertEqual(result.status_code, 200)
        rows = list(csv.reader(io.StringIO(result.content.decode('utf-8-sig'))))
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1][2], "'=1+1")
        self.assertTrue(rows[1][-1].startswith("'"))

    def test_database_rejects_invalid_money_bypassing_api(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Transaction.objects.create(user=self.user, wallet=self.wallet, title='Invalid', kind='expense', amount=-1)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Profile.objects.filter(pk=self.profile.pk).update(essential_pct=99)

    def test_logout_and_local_coach(self):
        self.assertEqual(self.send('post', '/api/coach', {'message': 'How much can I save?'}).status_code, 200)
        self.assertEqual(self.send('post', '/api/logout').status_code, 200)
        self.assertFalse(self.client.get('/api/session').json()['authenticated'])
        self.assertEqual(self.client.get('/api/state').status_code, 401)
