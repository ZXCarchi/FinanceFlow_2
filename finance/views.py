import csv, json
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST
from .forms import TransactionForm, WalletForm, GoalForm, BudgetLimitForm, RecurringPaymentForm
from .models import Transaction, Wallet, SavingsGoal, BudgetLimit, RecurringPayment
from .services import dashboard_snapshot, category_spending, current_month_bounds, monthly_trend, smart_plan, coach_reply, create_default_categories


def landing(request):
    if request.user.is_authenticated: return redirect('dashboard')
    return render(request,'finance/landing.html')

@login_required
def dashboard(request):
    create_default_categories(request.user)
    ctx=dashboard_snapshot(request.user); ctx['tx_form']=TransactionForm(user=request.user); return render(request,'finance/dashboard.html',ctx)

@login_required
def transactions(request):
    qs=request.user.transactions.select_related('wallet','category')
    kind=request.GET.get('kind',''); category=request.GET.get('category',''); q=request.GET.get('q','').strip(); date_from=request.GET.get('from',''); date_to=request.GET.get('to','')
    if kind in ['income','expense']: qs=qs.filter(kind=kind)
    if category.isdigit(): qs=qs.filter(category_id=category)
    if q: qs=qs.filter(title__icontains=q)
    parsed_from=parse_date(date_from) if date_from else None; parsed_to=parse_date(date_to) if date_to else None
    if parsed_from: qs=qs.filter(date__gte=parsed_from)
    if parsed_to: qs=qs.filter(date__lte=parsed_to)
    form=TransactionForm(user=request.user)
    return render(request,'finance/transactions.html',{'transactions':qs[:250],'form':form,'categories':request.user.categories.all(),'filters':{'kind':kind,'category':category,'q':q,'from':date_from,'to':date_to}})

@login_required
@require_POST
def transaction_add(request):
    form=TransactionForm(request.POST,user=request.user)
    if form.is_valid():
        obj=form.save(commit=False); obj.user=request.user; obj.save(); messages.success(request,_('Transaction added.'))
    else: messages.error(request,_('Please check the transaction fields.'))
    return redirect(request.POST.get('next') or 'transactions')

@login_required
@require_POST
def transaction_delete(request, pk):
    get_object_or_404(Transaction,pk=pk,user=request.user).delete(); messages.success(request,_('Transaction deleted.')); return redirect('transactions')

@login_required
def wallets(request):
    return render(request,'finance/wallets.html',{'wallets':request.user.wallets.filter(is_active=True),'form':WalletForm()})

@login_required
@require_POST
def wallet_add(request):
    form=WalletForm(request.POST)
    if form.is_valid(): obj=form.save(commit=False); obj.user=request.user; obj.save(); messages.success(request,_('Wallet added.'))
    else: messages.error(request,_('Please check the wallet fields.'))
    return redirect('wallets')

@login_required
def goals(request):
    return render(request,'finance/goals.html',{'goals':request.user.goals.all(),'form':GoalForm()})

@login_required
@require_POST
def goal_add(request):
    form=GoalForm(request.POST)
    if form.is_valid(): obj=form.save(commit=False); obj.user=request.user; obj.save(); messages.success(request,_('Savings goal created.'))
    else: messages.error(request,_('Please check the goal fields.'))
    return redirect('goals')

@login_required
@require_POST
def goal_update_progress(request,pk):
    goal=get_object_or_404(SavingsGoal,pk=pk,user=request.user)
    try: goal.saved_amount=max(Decimal('0'),Decimal(request.POST.get('saved_amount','0'))); goal.save(update_fields=['saved_amount']); messages.success(request,_('Goal progress updated.'))
    except Exception: messages.error(request,_('Enter a valid amount.'))
    return redirect('goals')

@login_required
def planner(request):
    start,end=current_month_bounds(); rows=category_spending(request.user,start,end); spent={r['category_id']:r['amount'] for r in rows}
    limits=[]
    for limit in request.user.budget_limits.select_related('category'):
        used=spent.get(limit.category_id,Decimal('0')); pct=min(100,round(float(used/limit.monthly_limit*100),1)) if limit.monthly_limit else 0
        limits.append({'obj':limit,'used':used,'pct':pct})
    return render(request,'finance/planner.html',{'plan':smart_plan(request.user),'limits':limits,'form':BudgetLimitForm(user=request.user)})

@login_required
@require_POST
def budget_limit_add(request):
    form=BudgetLimitForm(request.POST,user=request.user)
    if form.is_valid():
        cat=form.cleaned_data['category']; amount=form.cleaned_data['monthly_limit']
        BudgetLimit.objects.update_or_create(user=request.user,category=cat,defaults={'monthly_limit':amount}); messages.success(request,_('Budget limit saved.'))
    else: messages.error(request,_('Please check the budget fields.'))
    return redirect('planner')

@login_required
def reports(request):
    start,end=current_month_bounds(); trend=monthly_trend(request.user,6)
    return render(request,'finance/reports.html',{'categories':category_spending(request.user,start,end),'trend_json':json.dumps(trend),'plan':smart_plan(request.user)})

@login_required
def coach(request):
    return render(request,'finance/coach.html',{'plan':smart_plan(request.user)})

@login_required
@require_POST
def coach_api(request):
    try: payload=json.loads(request.body.decode('utf-8'))
    except Exception: payload=request.POST
    return JsonResponse({'reply':coach_reply(request.user,payload.get('message',''))})

@login_required
def recurring(request):
    return render(request,'finance/recurring.html',{'items':request.user.recurring_payments.select_related('wallet','category'),'form':RecurringPaymentForm(user=request.user)})

@login_required
@require_POST
def recurring_add(request):
    form=RecurringPaymentForm(request.POST,user=request.user)
    if form.is_valid(): obj=form.save(commit=False); obj.user=request.user; obj.save(); messages.success(request,_('Recurring item saved.'))
    else: messages.error(request,_('Please check the recurring payment fields.'))
    return redirect('recurring')


@login_required
@require_POST
def recurring_apply(request):
    from calendar import monthrange
    from django.utils import timezone
    today=timezone.localdate(); created=0
    last_day=monthrange(today.year,today.month)[1]
    for item in request.user.recurring_payments.filter(is_active=True):
        day=min(item.day_of_month,last_day); tx_date=today.replace(day=day)
        if tx_date>today: continue
        exists=request.user.transactions.filter(wallet=item.wallet,title=item.title,amount=item.amount,kind=item.kind,date=tx_date).exists()
        if not exists:
            Transaction.objects.create(user=request.user,wallet=item.wallet,category=item.category,title=item.title,amount=item.amount,kind=item.kind,date=tx_date,note=_('Created from recurring item'))
            created+=1
    messages.success(request,_('%(count)s recurring transactions added for this month.') % {'count':created})
    return redirect('recurring')

@login_required
def settings_view(request):
    profile=request.user.profile
    if request.method=='POST':
        currency=request.POST.get('currency')
        income=request.POST.get('expected_monthly_income')
        if currency in dict(profile.CURRENCIES): profile.currency=currency
        try: profile.expected_monthly_income=max(Decimal('0'),Decimal(income or '0'))
        except Exception: pass
        request.user.first_name=request.POST.get('first_name','').strip()[:150] or request.user.first_name
        request.user.save(update_fields=['first_name']); profile.save(); messages.success(request,_('Settings saved.')); return redirect('settings')
    return render(request,'finance/settings.html',{'profile':profile})

@login_required
def export_csv(request):
    response=HttpResponse(content_type='text/csv; charset=utf-8'); response['Content-Disposition']='attachment; filename="financeflow-transactions.csv"'; response.write('\ufeff')
    w=csv.writer(response); w.writerow(['Date','Type','Title','Category','Wallet','Amount','Note'])
    for tx in request.user.transactions.select_related('category','wallet').order_by('-date'):
        w.writerow([tx.date,tx.kind,tx.title,tx.category.name if tx.category else '',tx.wallet.name,tx.amount,tx.note])
    return response

def service_worker(request):
    js="""const C='financeflow-v1';self.addEventListener('install',e=>self.skipWaiting());self.addEventListener('activate',e=>self.clients.claim());self.addEventListener('fetch',e=>{if(e.request.method==='GET')e.respondWith(fetch(e.request).catch(()=>caches.match(e.request)));});"""
    return HttpResponse(js,content_type='application/javascript')
