from django.contrib import admin
from .models import Wallet, Category, Transaction, SavingsGoal, BudgetLimit, RecurringPayment
for model in [Wallet, Category, Transaction, SavingsGoal, BudgetLimit, RecurringPayment]:
    admin.site.register(model)
