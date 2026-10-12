from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.functions import Round


class Profile(models.Model):
    CURRENCIES = [('PLN', 'PLN'), ('EUR', 'EUR'), ('USD', 'USD'), ('GBP', 'GBP'), ('KGS', 'KGS')]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    currency = models.CharField(max_length=3, choices=CURRENCIES, default='PLN')
    expected_monthly_income = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    essential_pct = models.DecimalField(max_digits=5, decimal_places=2, default=50, validators=[MinValueValidator(0), MaxValueValidator(100)])
    lifestyle_pct = models.DecimalField(max_digits=5, decimal_places=2, default=30, validators=[MinValueValidator(0), MaxValueValidator(100)])
    savings_pct = models.DecimalField(max_digits=5, decimal_places=2, default=20, validators=[MinValueValidator(0), MaxValueValidator(100)])
    onboarding_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(expected_monthly_income__gte=0), name='profile_income_nonnegative'),
            models.CheckConstraint(condition=models.Q(essential_pct__gte=0, essential_pct__lte=100, lifestyle_pct__gte=0, lifestyle_pct__lte=100, savings_pct__gte=0, savings_pct__lte=100), name='profile_percentages_in_range'),
            models.CheckConstraint(condition=models.Q(essential_pct=Round(100 - models.F('lifestyle_pct') - models.F('savings_pct'), precision=2)), name='profile_percentages_sum_100'),
        ]

    def clean(self):
        super().clean()
        values = (self.essential_pct, self.lifestyle_pct, self.savings_pct)
        if all(isinstance(value, Decimal) and value.is_finite() for value in values):
            if sum(values) != Decimal('100'):
                raise ValidationError({'savings_pct': 'The three percentages must add up to exactly 100.'})

    def __str__(self):
        return f'{self.user.username} profile'
