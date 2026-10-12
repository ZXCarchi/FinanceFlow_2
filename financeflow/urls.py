from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('finance.api_urls')),
    re_path(r'^(?:dashboard|transactions|wallets|goals|planner|reports|recurring|settings|coach|login|signup)?/?$', TemplateView.as_view(template_name='spa.html'), name='app'),
]
