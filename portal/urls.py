# portal/urls.py

from django.urls import path
from . import views

app_name = 'portal'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('application/', views.application_form_view, name='application_form'),
    path('documents/', views.document_submission_view, name='document_submission'),
    path('agency-fee/', views.agency_fee_view, name='agency_fee'),

    # Add the URL for the final visa application step
    path('visa-application/', views.visa_application_view, name='visa_application'),

    # Payment URLs
    path('payment/initiate/', views.initiate_payment, name='initiate_payment'),
    path('payment/callback/', views.flutterwave_webhook, name='payment_callback'),
]
