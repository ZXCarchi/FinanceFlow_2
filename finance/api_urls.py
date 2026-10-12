from django.urls import re_path

from . import api

urlpatterns = [
    re_path(r'^session/?$', api.session, name='api_session'),
    re_path(r'^register/?$', api.register, name='api_register'),
    re_path(r'^login/?$', api.login, name='api_login'),
    re_path(r'^logout/?$', api.logout, name='api_logout'),
    re_path(r'^state/?$', api.state, name='api_state'),
    re_path(r'^settings/?$', api.settings, name='api_settings'),
    re_path(r'^plan/?$', api.plan, name='api_plan'),
    re_path(r'^recurring/apply/?$', api.recurring_apply, name='api_recurring_apply'),
    re_path(r'^export/?$', api.export, name='api_export'),
    re_path(r'^coach/?$', api.coach, name='api_coach'),
    re_path(r'^(?P<collection>wallets|categories|transactions|goals|budgets|recurring)/?$', api.resource, name='api_collection'),
    re_path(r'^(?P<collection>wallets|categories|transactions|goals|budgets|recurring)/(?P<pk>\d+)/?$', api.resource, name='api_item'),
]
