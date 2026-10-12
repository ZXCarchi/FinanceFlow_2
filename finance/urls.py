from django.urls import path
from . import views
urlpatterns = [
    path('',views.landing,name='landing'),
    path('app/',views.dashboard,name='dashboard'),
    path('app/transactions/',views.transactions,name='transactions'),
    path('app/transactions/add/',views.transaction_add,name='transaction_add'),
    path('app/transactions/<int:pk>/delete/',views.transaction_delete,name='transaction_delete'),
    path('app/wallets/',views.wallets,name='wallets'), path('app/wallets/add/',views.wallet_add,name='wallet_add'),
    path('app/goals/',views.goals,name='goals'), path('app/goals/add/',views.goal_add,name='goal_add'), path('app/goals/<int:pk>/progress/',views.goal_update_progress,name='goal_update_progress'),
    path('app/planner/',views.planner,name='planner'), path('app/planner/limit/',views.budget_limit_add,name='budget_limit_add'),
    path('app/reports/',views.reports,name='reports'),
    path('app/coach/',views.coach,name='coach'), path('app/coach/api/',views.coach_api,name='coach_api'),
    path('app/recurring/',views.recurring,name='recurring'), path('app/recurring/add/',views.recurring_add,name='recurring_add'), path('app/recurring/apply/',views.recurring_apply,name='recurring_apply'),
    path('app/settings/',views.settings_view,name='settings'), path('app/export.csv',views.export_csv,name='export_csv'),
]
