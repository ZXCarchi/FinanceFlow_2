from datetime import date
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Wallet(models.Model):
    TYPES = [('card', _('Card')), ('cash', _('Cash')), ('savings', _('Savings')), ('other', _('Other'))]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallets')
    name = models.CharField(max_length=80)
    wallet_type = models.CharField(max_length=20, choices=TYPES, default='card')
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def current_balance(self):
        totals = self.transactions.filter(date__lte=timezone.localdate()).aggregate(
            income=models.Sum('amount', filter=models.Q(kind='income')),
            expense=models.Sum('amount', filter=models.Q(kind='expense')),
        )
        return self.opening_balance + (totals['income'] or Decimal(0)) - (totals['expense'] or Decimal(0))

    def __str__(self):
        return self.name


class Category(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=80)
    code = models.SlugField(max_length=50, blank=True)
    kind = models.CharField(max_length=10, choices=[('expense', _('Expense')), ('income', _('Income')), ('both', _('Both'))], default='expense')
    icon = models.CharField(max_length=16, default='•')
    color = models.CharField(max_length=16, default='#6c5ce7', validators=[RegexValidator(r'^#[0-9a-fA-F]{6}$', 'Use a color such as #6c5ce7.')])
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ['kind', 'name']

    def clean(self):
        super().clean()
        if self.pk and self.kind != 'both':
            incompatible = self.transactions.exclude(kind=self.kind).exists() or self.recurringpayment_set.exclude(kind=self.kind).exists()
            if incompatible or (self.kind == 'income' and self.limits.exists()):
                raise ValidationError({'kind': 'This category is already used by incompatible records.'})

    def __str__(self):
        return self.name


def validate_financial_relations(instance):
    errors = {}
    if instance.wallet_id:
        if instance.wallet.user_id != instance.user_id:
            errors['wallet'] = 'Choose one of your own accounts.'
        elif not instance.wallet.is_active:
            errors['wallet'] = 'Choose an active account.'
    if instance.category_id:
        if instance.category.user_id != instance.user_id:
            errors['category'] = 'Choose one of your own categories.'
        elif instance.category.kind not in ('both', instance.kind):
            errors['category'] = 'The category does not match this transaction type.'
    if errors:
        raise ValidationError(errors)


class Transaction(models.Model):
    KINDS = [('income', _('Income')), ('expense', _('Expense'))]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    kind = models.CharField(max_length=10, choices=KINDS)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    title = models.CharField(max_length=120)
    date = models.DateField(default=timezone.localdate, validators=[MinValueValidator(date(1900, 1, 1)), MaxValueValidator(date(9998, 12, 31))])
    note = models.CharField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']
        constraints = [models.CheckConstraint(condition=models.Q(amount__gt=0), name='transaction_amount_positive')]
        indexes = [models.Index(fields=['user', 'date'], name='transaction_user_date_idx')]

    def clean(self):
        super().clean()
        validate_financial_relations(self)

    def __str__(self):
        return f'{self.title} {self.amount}'


class SavingsGoal(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='goals')
    name = models.CharField(max_length=120)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    saved_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    target_date = models.DateField(null=True, blank=True, validators=[MinValueValidator(date(1900, 1, 1)), MaxValueValidator(date(9998, 12, 31))])
    icon = models.CharField(max_length=16, default='🎯')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(target_amount__gt=0), name='goal_target_positive'),
            models.CheckConstraint(condition=models.Q(saved_amount__gte=0), name='goal_saved_nonnegative'),
        ]

    def progress(self):
        if not self.target_amount:
            return 0
        return min(100, round(float(self.saved_amount / self.target_amount * 100), 1))

    def remaining(self):
        return max(Decimal('0'), self.target_amount - self.saved_amount)

    def __str__(self):
        return self.name


class BudgetLimit(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='budget_limits')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='limits')
    monthly_limit = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'category'], name='unique_user_category_budget'),
            models.CheckConstraint(condition=models.Q(monthly_limit__gt=0), name='budget_limit_positive'),
        ]

    def clean(self):
        super().clean()
        if self.category_id and (self.category.user_id != self.user_id or self.category.kind == 'income'):
            raise ValidationError({'category': 'Choose one of your expense categories.'})


class RecurringPayment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recurring_payments')
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='recurring_payments')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    kind = models.CharField(max_length=10, choices=Transaction.KINDS, default='expense')
    day_of_month = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(31)])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(amount__gt=0), name='recurring_amount_positive'),
            models.CheckConstraint(condition=models.Q(day_of_month__gte=1, day_of_month__lte=31), name='recurring_day_valid'),
        ]

    def clean(self):
        super().clean()
        validate_financial_relations(self)

    def __str__(self):
        return self.title


class RecurringOccurrence(models.Model):
    """Permanent application receipt: deleting a transaction cannot create a duplicate."""
    recurring = models.ForeignKey(RecurringPayment, on_delete=models.CASCADE, related_name='occurrences')
    month = models.DateField()
    transaction = models.OneToOneField(Transaction, on_delete=models.SET_NULL, null=True, related_name='recurring_occurrence')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['recurring', 'month'], name='unique_recurring_month')]
