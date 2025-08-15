# portal/views.py

import uuid
import json
import requests
from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from django.urls import reverse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import (
    UserProfile, Application, WorkApplication, Country, Document, 
    Payment, Testimonial
)
from .forms import (
    StudentApplicationForm, WorkApplicationForm, DocumentUploadForm, 
    TestimonialForm
)

# --- Authentication ---
def signup_choice_view(request):
    """
    Displays the page where users choose their application path.
    """
    return render(request, 'account/signup_choice.html')

# --- Main Dashboard Router ---
@login_required
def dashboard(request):
    """
    Acts as a router, displaying the correct dashboard based on user type.
    It creates a UserProfile if one doesn't exist for some reason.
    """
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if profile.account_type == UserProfile.AccountType.STUDENT:
        return student_dashboard(request)
    else:
        return worker_dashboard(request)

# --- Student Dashboard & Views ---
def student_dashboard(request):
    application, _ = Application.objects.get_or_create(user=request.user)
    ALL_STEPS = [
        {'id': Application.ApplicationStatus.STEP_1_APPLICATION_FORM, 'title': 'Application Form', 'number': 1, 'url_name': 'portal:student_application_form'},
        {'id': Application.ApplicationStatus.STEP_2_ADMISSION_FEE, 'title': 'Admission Letter Fee', 'number': 2, 'url_name': 'portal:student_document_submission'},
        {'id': Application.ApplicationStatus.STEP_3_AGENCY_FEE, 'title': 'Agency Fee', 'number': 3, 'url_name': 'portal:student_agency_fee'},
        {'id': Application.ApplicationStatus.STEP_4_VISA_APPLICATION, 'title': 'Visa Application', 'number': 4, 'url_name': 'portal:student_visa_application'},
    ]
    current_status = application.status
    try:
        if current_status == Application.ApplicationStatus.COMPLETED:
            current_index = len(ALL_STEPS)
        else:
            current_index = next(i for i, step in enumerate(ALL_STEPS) if step['id'] == current_status)
    except StopIteration:
        current_index = 0
    processed_steps = []
    for i, step in enumerate(ALL_STEPS):
        step_info = step.copy()
        if i < current_index:
            step_info['status'] = 'completed'
        elif i == current_index:
            step_info['status'] = 'active'
        else:
            step_info['status'] = 'pending'
        processed_steps.append(step_info)
    context = { 'application': application, 'steps': processed_steps }
    return render(request, 'portal/dashboard_student.html', context)

@login_required
def student_application_form_view(request):
    application, _ = Application.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = StudentApplicationForm(request.POST, request.FILES, instance=application)
        if form.is_valid():
            application_instance = form.save(commit=False)
            if 'passport_photograph_upload' in request.FILES:
                application_instance.passport_photograph = request.FILES['passport_photograph_upload']
            application_instance.save()
            document_uploads = {
                'international_passport_upload': Document.DocumentType.INTERNATIONAL_PASSPORT,
                'school_certificate_upload': Document.DocumentType.SCHOOL_CERTIFICATE,
                'birth_certificate_upload': Document.DocumentType.BIRTH_CERTIFICATE,
            }
            for field_name, doc_type in document_uploads.items():
                if field_name in request.FILES:
                    Document.objects.update_or_create(
                        application=application_instance, document_type=doc_type,
                        defaults={'file': request.FILES[field_name]}
                    )
            return JsonResponse({'success': True, 'message': 'Application saved successfully!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = StudentApplicationForm(instance=application)
    return render(request, 'portal/student_application_form.html', {'form': form})

@login_required
def student_document_submission_view(request):
    application = request.user.student_application
    admin_document = Document.objects.filter(application__isnull=True, work_application__isnull=True, is_admin_upload=True, document_type=Document.DocumentType.BLANK_FORM_TEMPLATE).order_by('-uploaded_at').first()
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.application = application
            document.document_type = Document.DocumentType.FILLED_APPLICATION_FORM
            document.save()
            return JsonResponse({'success': True, 'message': 'Document uploaded successfully!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    form = DocumentUploadForm()
    context = {'form': form, 'admin_document': admin_document, 'application': application}
    return render(request, 'portal/student_document_submission.html', context)

@login_required
def student_agency_fee_view(request):
    application = request.user.student_application
    admission_letter = Document.objects.filter(application=application, document_type=Document.DocumentType.ADMISSION_LETTER, is_admin_upload=True).first()
    context = {'application': application, 'admission_letter': admission_letter}
    return render(request, 'portal/student_agency_fee.html', context)

@login_required
def student_visa_application_view(request):
    application = request.user.student_application
    if request.method == 'POST':
        if Testimonial.objects.filter(application=application).exists():
            return JsonResponse({'success': False, 'message': 'You have already submitted a testimonial.'}, status=400)
        form = TestimonialForm(request.POST)
        if form.is_valid():
            testimonial = form.save(commit=False)
            testimonial.application = application
            testimonial.save()
            application.status = Application.ApplicationStatus.COMPLETED
            application.save()
            return JsonResponse({'success': True, 'message': 'Thank you for your feedback!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    visa_updates = application.visa_updates.all()
    testimonial = Testimonial.objects.filter(application=application).first()
    form = TestimonialForm(instance=testimonial)
    context = {
        'application': application, 'visa_updates': visa_updates,
        'testimonial_form': form, 'testimonial': testimonial,
    }
    return render(request, 'portal/student_visa_application.html', context)

# --- Worker Dashboard & Views ---
def worker_dashboard(request):
    application, _ = WorkApplication.objects.get_or_create(user=request.user)
    ALL_STEPS = [
        {'id': WorkApplication.WorkApplicationStatus.STEP_1_APPLICATION_FORM, 'title': 'Application Form', 'number': 1, 'url_name': 'portal:work_application_form'},
        {'id': WorkApplication.WorkApplicationStatus.STEP_2_EMPLOYMENT_FORM, 'title': 'Employment Form & 50% Fee', 'number': 2, 'url_name': '#'},
        {'id': WorkApplication.WorkApplicationStatus.STEP_3_JOB_OFFER, 'title': 'Job Offer & Final Fee', 'number': 3, 'url_name': '#'},
        {'id': WorkApplication.WorkApplicationStatus.STEP_4_VISA_APPLICATION, 'title': 'Visa Application', 'number': 4, 'url_name': '#'},
    ]
    current_status = application.status
    try:
        if current_status == WorkApplication.WorkApplicationStatus.COMPLETED:
            current_index = len(ALL_STEPS)
        else:
            current_index = next(i for i, step in enumerate(ALL_STEPS) if step['id'] == current_status)
    except StopIteration:
        current_index = 0
    processed_steps = []
    for i, step in enumerate(ALL_STEPS):
        step_info = step.copy()
        if i < current_index:
            step_info['status'] = 'completed'
        elif i == current_index:
            step_info['status'] = 'active'
        else:
            step_info['status'] = 'pending'
        processed_steps.append(step_info)
    context = {'application': application, 'steps': processed_steps}
    return render(request, 'portal/dashboard_worker.html', context)

@login_required
def work_application_form_view(request):
    application, _ = WorkApplication.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = WorkApplicationForm(request.POST, request.FILES, instance=application)
        if form.is_valid():
            application_instance = form.save(commit=False)
            if 'passport_photograph_upload' in request.FILES:
                application_instance.passport_photograph = request.FILES['passport_photograph_upload']
            application_instance.save()
            document_uploads = {
                'international_passport_upload': Document.DocumentType.INTERNATIONAL_PASSPORT,
                'educational_certificate_upload': Document.DocumentType.SCHOOL_CERTIFICATE,
                'work_experience_upload': Document.DocumentType.WORK_EXPERIENCE_LETTER,
            }
            for field_name, doc_type in document_uploads.items():
                if field_name in request.FILES:
                    Document.objects.update_or_create(
                        work_application=application_instance, document_type=doc_type,
                        defaults={'file': request.FILES[field_name]}
                    )
            return JsonResponse({'success': True, 'message': 'Application saved successfully!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = WorkApplicationForm(instance=application)
    return render(request, 'portal/work_application_form.html', {'form': form})

# --- Generic Payment & Webhook Views ---
@login_required
@require_POST
def initiate_payment(request):
    try:
        data = json.loads(request.body)
        purpose = data.get('purpose')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    profile = request.user.profile
    application = None
    work_application = None
    
    if profile.account_type == UserProfile.AccountType.STUDENT:
        application = request.user.student_application
        customer_email = application.email
        customer_phone = application.phone_number
        customer_name = application.full_name
    else:
        work_application = request.user.work_application
        customer_email = work_application.email
        customer_phone = work_application.contact_number
        customer_name = work_application.full_name

    currency = 'NGN'
    
    if purpose == 'STUDENT_APP_FEE':
        amount = Decimal('15.00')
        currency = 'NGN'
        payment_purpose = Payment.PaymentPurpose.STUDENT_APP_FEE
    elif purpose == 'ADMISSION_FEE':
        amount = Decimal('1000.00')
        payment_purpose = Payment.PaymentPurpose.ADMISSION_FEE
    elif purpose == 'AGENCY_FEE_HALF':
        amount = Decimal('250.00')
        payment_purpose = Payment.PaymentPurpose.AGENCY_FEE_HALF
    elif purpose == 'AGENCY_FEE_FULL':
        amount = Decimal('500.00')
        payment_purpose = Payment.PaymentPurpose.AGENCY_FEE_FULL
    elif purpose == 'WORK_APP_FEE':
        amount = Decimal('30.00')
        payment_purpose = Payment.PaymentPurpose.WORK_APP_FEE
    elif purpose in ['WORK_VISA_50_PERCENT', 'WORK_VISA_25_PERCENT']:
        if not work_application or not work_application.destination_country:
            return JsonResponse({'error': 'Destination country not selected.'}, status=400)
        total_fee = work_application.destination_country.processing_fee
        if purpose == 'WORK_VISA_50_PERCENT':
            amount = total_fee * Decimal('0.50')
            payment_purpose = Payment.PaymentPurpose.WORK_VISA_50_PERCENT
        else:
            amount = total_fee * Decimal('0.25')
            payment_purpose = Payment.PaymentPurpose.WORK_VISA_25_PERCENT
    else:
        return JsonResponse({'error': 'Invalid payment purpose'}, status=400)

    tx_ref = f"HTG-{request.user.id}-{uuid.uuid4().hex[:6].upper()}"
    Payment.objects.create(
        application=application, work_application=work_application,
        amount=amount, purpose=payment_purpose, tx_ref=tx_ref
    )
    
    redirect_url = request.build_absolute_uri(reverse('portal:payment_callback'))
    payment_data = {
        'public_key': settings.FLUTTERWAVE_PUBLIC_KEY, 'tx_ref': tx_ref, 'amount': str(amount),
        'currency': currency, 'redirect_url': redirect_url,
        'customer': {'email': customer_email, 'phonenumber': customer_phone, 'name': customer_name},
        'customizations': {'title': 'Hadey Travels Global', 'description': payment_purpose, 'logo': 'URL_TO_YOUR_LOGO_IMAGE'}
    }
    return JsonResponse(payment_data)

@csrf_exempt
def flutterwave_webhook(request):
    tx_ref = request.GET.get('tx_ref')
    transaction_id = request.GET.get('transaction_id')
    if not tx_ref or not transaction_id:
        return JsonResponse({'status': 'error', 'message': 'Missing transaction reference or ID'}, status=400)
    
    url = f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify"
    headers = {"Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}"}
    
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        data = response.json()
        if data.get('status') == 'success':
            payment_data = data.get('data', {})
            payment = Payment.objects.get(tx_ref=payment_data.get('tx_ref'))
            
            if float(payment_data.get('amount')) == float(payment.amount) and payment.status == Payment.PaymentStatus.PENDING:
                payment.status = Payment.PaymentStatus.SUCCESSFUL
                payment.save()
                
                user = None
                if payment.application:
                    application = payment.application
                    user = application.user
                    if payment.purpose == Payment.PaymentPurpose.STUDENT_APP_FEE:
                        application.status = Application.ApplicationStatus.STEP_2_ADMISSION_FEE
                    elif payment.purpose == Payment.PaymentPurpose.ADMISSION_FEE:
                        application.status = Application.ApplicationStatus.STEP_3_AGENCY_FEE
                    elif payment.purpose in [Payment.PaymentPurpose.AGENCY_FEE_FULL, Payment.PaymentPurpose.AGENCY_FEE_HALF]:
                        application.status = Application.ApplicationStatus.STEP_4_VISA_APPLICATION
                    application.save()
                
                elif payment.work_application:
                    application = payment.work_application
                    user = application.user
                    if payment.purpose == Payment.PaymentPurpose.WORK_APP_FEE:
                        application.status = WorkApplication.WorkApplicationStatus.STEP_2_EMPLOYMENT_FORM
                    # Add other worker status updates here
                    application.save()

                if user:
                    context = {'user': user, 'payment': payment, 'dashboard_url': request.build_absolute_uri(reverse('portal:dashboard'))}
                    user_email_body = render_to_string('portal/emails/payment_successful_user.txt', context)
                    send_mail(subject='Your Payment to Hadey Travels Global was Successful!', message=user_email_body, from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[user.email], fail_silently=True)
                    admin_email_body = render_to_string('portal/emails/payment_successful_admin.txt', context)
                    send_mail(subject=f'New Payment Received: {payment.get_purpose_display()} from {user.username}', message=admin_email_body, from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[settings.ADMIN_EMAIL], fail_silently=True)
                
                return redirect('portal:dashboard')
    except (requests.RequestException, Payment.DoesNotExist) as e:
        pass
    return redirect('portal:dashboard')
