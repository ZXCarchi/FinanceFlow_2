from datetime import timedelta
from decimal import Decimal
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone
from accounts.models import Profile
from finance.models import Wallet, Transaction, SavingsGoal, BudgetLimit, RecurringPayment
from finance.services import create_default_categories

class Command(BaseCommand):
    help = 'Create or refresh a local demo account for FinanceFlow AI.'
    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('Demo data is available only in local DEBUG mode.')
        email='demo@financeflow.local'
        user,created=User.objects.get_or_create(username=email, defaults={'email':email,'first_name':'Alex'})
        user.set_password('DemoPass123!'); user.email=email; user.first_name='Alex'; user.save()
        profile,_=Profile.objects.get_or_create(user=user)
        profile.currency='PLN'; profile.expected_monthly_income=Decimal('6200'); profile.onboarding_complete=True; profile.save()
        create_default_categories(user)
        user.transactions.all().delete(); user.wallets.all().delete(); user.goals.all().delete(); user.budget_limits.all().delete(); user.recurring_payments.all().delete()
        card=Wallet.objects.create(user=user,name='Everyday card',wallet_type='card',opening_balance=Decimal('5400'))
        cash=Wallet.objects.create(user=user,name='Cash',wallet_type='cash',opening_balance=Decimal('350'))
        savings=Wallet.objects.create(user=user,name='Savings',wallet_type='savings',opening_balance=Decimal('1600'))
        cats={c.code:c for c in user.categories.all()}
        today=timezone.localdate(); start=today.replace(day=1)
        rows=[
            ('income','Salary',Decimal('6200'),card,cats['salary'],1),
            ('expense','Rent',Decimal('1800'),card,cats['housing'],2),
            ('expense','Groceries',Decimal('286'),card,cats['food'],4),
            ('expense','Public transport',Decimal('110'),card,cats['transport'],5),
            ('expense','Lunch with friends',Decimal('92'),card,cats['food'],7),
            ('expense','Streaming',Decimal('49'),card,cats['subscriptions'],8),
            ('expense','Course materials',Decimal('160'),card,cats['education'],10),
            ('expense','Cinema',Decimal('58'),cash,cats['entertainment'],12),
            ('expense','Shopping',Decimal('220'),card,cats['shopping'],14),
        ]
        for kind,title,amount,wallet,cat,day in rows:
            safe_day=min(day,today.day)
            Transaction.objects.create(user=user,kind=kind,title=title,amount=amount,wallet=wallet,category=cat,date=start.replace(day=safe_day))
        SavingsGoal.objects.create(user=user,name='Emergency fund',target_amount=Decimal('8000'),saved_amount=Decimal('2100'),target_date=today+timedelta(days=220),icon='🛟')
        SavingsGoal.objects.create(user=user,name='Trip',target_amount=Decimal('3500'),saved_amount=Decimal('900'),target_date=today+timedelta(days=140),icon='✈️')
        BudgetLimit.objects.create(user=user,category=cats['food'],monthly_limit=Decimal('850'))
        BudgetLimit.objects.create(user=user,category=cats['entertainment'],monthly_limit=Decimal('350'))
        RecurringPayment.objects.create(user=user,wallet=card,category=cats['housing'],title='Rent',amount=Decimal('1800'),kind='expense',day_of_month=2)
        RecurringPayment.objects.create(user=user,wallet=card,category=cats['subscriptions'],title='Streaming',amount=Decimal('49'),kind='expense',day_of_month=8)
        self.stdout.write(self.style.SUCCESS('Demo ready: demo@financeflow.local / DemoPass123!'))
