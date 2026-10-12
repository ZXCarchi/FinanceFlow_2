from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from finance.models import Wallet
from finance.services import create_default_categories
from .forms import SignUpForm


def signup(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            Wallet.objects.create(user=user, name=_('Main wallet'), wallet_type='card', opening_balance=form.cleaned_data.get('opening_balance') or 0)
            create_default_categories(user)
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})
