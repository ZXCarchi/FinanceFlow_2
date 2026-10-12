from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase
from accounts.models import Profile
from .models import Wallet, Transaction
from .services import create_default_categories, total_balance, smart_plan, coach_reply

class FinanceFlowCoreTests(TestCase):
    def setUp(self):
        self.user=User.objects.create_user('test@example.com',password='StrongPass123!',first_name='Test')
        Profile.objects.create(user=self.user,currency='PLN',expected_monthly_income=Decimal('5000'))
        create_default_categories(self.user)
        self.wallet=Wallet.objects.create(user=self.user,name='Main',opening_balance=Decimal('1000'))
    def test_balance_math(self):
        Transaction.objects.create(user=self.user,wallet=self.wallet,kind='income',title='Salary',amount=Decimal('5000'))
        Transaction.objects.create(user=self.user,wallet=self.wallet,kind='expense',title='Rent',amount=Decimal('1500'))
        self.assertEqual(total_balance(self.user),Decimal('4500.00'))
    def test_smart_plan_returns_allocations(self):
        plan=smart_plan(self.user)
        self.assertGreater(plan['planning_income'],0)
        self.assertGreaterEqual(plan['savings_pct'],10)
        self.assertEqual(plan['essential_pct']+plan['lifestyle_pct']+plan['savings_pct'],100)
    def test_coach_uses_user_data(self):
        reply=coach_reply(self.user,'How much should I save?')
        self.assertIn('PLN',reply)
