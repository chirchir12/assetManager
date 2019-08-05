from django.urls import path
from django.urls import re_path
from .views import (
    registerEmployer, 
    employer_dashboard_view,
    account_activation_sent,
    activate
    ) 

urlpatterns = [
    path('signUp/', registerEmployer, name='signup'),
    path('account_activation_sent/', account_activation_sent, name='account_activation_sent'),
    re_path(r'activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',activate, name='activate'),
    path('dashboard/', employer_dashboard_view, name='dashboard'),
    
]