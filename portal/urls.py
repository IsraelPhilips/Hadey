# portal/urls.py

from django.urls import path
from . import views

app_name = 'portal'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('application/', views.application_form_view, name='application_form'),
    
    # Payment URLs
    path('payment/initiate/', views.initiate_payment_view, name='initiate_payment'),
    path('payment/callback/', views.flutterwave_webhook, name='payment_callback'),
]
