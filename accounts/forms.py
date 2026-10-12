from decimal import Decimal
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import Profile

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(label=_('Name'), max_length=100)
    email = forms.EmailField(label=_('Email'))
    currency = forms.ChoiceField(label=_('Currency'), choices=Profile.CURRENCIES, initial='PLN')
    opening_balance = forms.DecimalField(label=_('Wallet balance'), min_value=0, decimal_places=2, required=False, initial=0)
    expected_monthly_income = forms.DecimalField(label=_('Expected monthly income'), min_value=0, decimal_places=2, required=False, initial=0)
    class Meta:
        model = User
        fields = ('first_name','email','password1','password2','currency','opening_balance','expected_monthly_income')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'select' if isinstance(field.widget, forms.Select) else 'input'
    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError(_('An account with this email already exists.'))
        return email
    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data['email']
        user.username = email
        user.email = email
        user.first_name = self.cleaned_data['first_name']
        if commit:
            user.save()
            Profile.objects.create(user=user, currency=self.cleaned_data['currency'], expected_monthly_income=self.cleaned_data.get('expected_monthly_income') or Decimal('0'), onboarding_complete=True)
        return user
