# portal/urls.py

from django.urls import path
from . import views

app_name = 'portal'

urlpatterns = [
    # --- Main Dashboard ---
    path('', views.dashboard, name='dashboard'),

    # --- Student Application URLs ---
    path('student/application/', views.student_application_form_view, name='student_application_form'),
    path('student/documents/', views.student_document_submission_view, name='student_document_submission'),
    path('student/agency-fee/', views.student_agency_fee_view, name='student_agency_fee'),
    path('student/visa-application/', views.student_visa_application_view, name='student_visa_application'),

    # --- Worker Application URLs ---
    path('worker/application/', views.work_application_form_view, name='work_application_form'),
    path('worker/employment-form/', views.work_employment_form_view, name='work_employment_form'),
    path('worker/job-offer/', views.work_job_offer_view, name='work_job_offer'),
    path('worker/visa-application/', views.work_visa_application_view, name='work_visa_application'),

    # --- Generic Payment URLs ---
    path('payment/initiate/', views.initiate_payment, name='initiate_payment'),
    path('payment/callback/', views.flutterwave_webhook, name='payment_callback'),

    # --- Admin PDF Generation URL ---
    path('admins/pdf/<str:app_type>/<int:app_id>/', views.generate_pdf_view, name='generate_pdf'),
]
