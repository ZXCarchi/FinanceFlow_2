from decimal import Decimal
from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .models import Transaction, Wallet, SavingsGoal, BudgetLimit, RecurringPayment, Category

CATEGORY_NAMES = {
    'food':'Food','transport':'Transport','housing':'Housing','utilities':'Utilities','entertainment':'Entertainment',
    'education':'Education','health':'Health','shopping':'Shopping','subscriptions':'Subscriptions','salary':'Salary',
    'part-time':'Part-time work','scholarship':'Scholarship','freelance':'Freelance','other':'Other'
}

class CategoryChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.icon} {_(CATEGORY_NAMES.get(obj.code, obj.name))}"

class StyledFormMixin:
    def apply_style(self):
        for field in self.fields.values():
            field.widget.attrs['class'] = 'select' if isinstance(field.widget, forms.Select) else 'input'

class TransactionForm(StyledFormMixin, forms.ModelForm):
    category = CategoryChoiceField(queryset=Category.objects.none(), required=False, label=_('Category'))
    class Meta:
        model = Transaction
        fields = ['kind','title','amount','wallet','category','date','note']
        labels = {'kind':_('Type'),'title':_('Title'),'amount':_('Amount'),'wallet':_('Wallet'),'category':_('Category'),'date':_('Date'),'note':_('Note')}
        widgets = {'date': forms.DateInput(attrs={'type':'date'}), 'note': forms.TextInput(attrs={'placeholder':_('Optional note')})}
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_style()
        self.fields['date'].initial = timezone.localdate()
        self.fields['amount'].min_value = Decimal('0.01')
        if user:
            self.fields['wallet'].queryset = user.wallets.filter(is_active=True)
            self.fields['category'].queryset = user.categories.all()

class WalletForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Wallet
        fields = ['name','wallet_type','opening_balance']
        labels = {'name':_('Wallet name'),'wallet_type':_('Wallet type'),'opening_balance':_('Opening balance')}
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.apply_style()

class GoalForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = SavingsGoal
        fields = ['name','target_amount','saved_amount','target_date','icon']
        labels = {'name':_('Goal name'),'target_amount':_('Target amount'),'saved_amount':_('Already saved'),'target_date':_('Target date'),'icon':_('Icon')}
        widgets = {'target_date': forms.DateInput(attrs={'type':'date'})}
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.apply_style()
        self.fields['target_amount'].min_value = Decimal('0.01')
        self.fields['saved_amount'].min_value = Decimal('0')

class BudgetLimitForm(StyledFormMixin, forms.ModelForm):
    category = CategoryChoiceField(queryset=Category.objects.none(), label=_('Category'))
    class Meta:
        model = BudgetLimit
        fields = ['category','monthly_limit']
        labels = {'category':_('Category'),'monthly_limit':_('Monthly limit')}
    def __init__(self,*args,user=None,**kwargs):
        super().__init__(*args,**kwargs)
        self.apply_style()
        self.fields['monthly_limit'].min_value = Decimal('0.01')
        if user:
            self.fields['category'].queryset = user.categories.filter(kind__in=['expense','both'])

class RecurringPaymentForm(StyledFormMixin, forms.ModelForm):
    category = CategoryChoiceField(queryset=Category.objects.none(), required=False, label=_('Category'))
    class Meta:
        model = RecurringPayment
        fields = ['title','amount','kind','wallet','category','day_of_month','is_active']
        labels = {'title':_('Title'),'amount':_('Amount'),'kind':_('Type'),'wallet':_('Wallet'),'category':_('Category'),'day_of_month':_('Day of month'),'is_active':_('Active')}
    def __init__(self,*args,user=None,**kwargs):
        super().__init__(*args,**kwargs)
        self.apply_style()
        self.fields['amount'].min_value = Decimal('0.01')
        self.fields['day_of_month'].min_value = 1
        self.fields['day_of_month'].max_value = 31
        if user:
            self.fields['wallet'].queryset = user.wallets.filter(is_active=True)
            self.fields['category'].queryset = user.categories.all()
