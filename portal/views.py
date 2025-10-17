# portal/views.py

import uuid
from .utils import get_currency_context, is_nigerian_user
import json
import requests
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.urls import reverse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import (
    UserProfile, Application, WorkApplication, Country, Document, 
    Payment, Testimonial, FeeStructure
)
from .forms import (
    StudentApplicationForm, WorkApplicationForm, DocumentUploadForm, 
    TestimonialForm
)

# --- Authentication ---
def signup_choice_view(request):
    return render(request, 'account/signup_choice.html')

# --- Main Dashboard Router ---
@login_required
def dashboard(request):
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
        {'id': Application.ApplicationStatus.STEP_2_ADMISSION_FEE, 'title': 'Admission Form', 'number': 2, 'url_name': 'portal:student_document_submission'},
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
    payment_made = Payment.objects.filter(
        application=application, 
        purpose=Payment.PaymentPurpose.STUDENT_APP_FEE, 
        status=Payment.PaymentStatus.SUCCESSFUL
    ).exists()
    
    # Get the default fee from the FeeStructure model
    default_fee = FeeStructure.objects.filter(fee_type='STUDENT_APP_FEE').first()
    default_fee_amount = default_fee.amount if default_fee else Decimal('15.00')

    # Use the application's custom fee if it exists, otherwise use the default
    application_fee_amount = application.custom_application_fee or default_fee_amount
    
    currency_context = get_currency_context(request, application_fee_amount)
    
    

    if request.method == 'POST':
        form = StudentApplicationForm(request.POST, request.FILES, instance=application)
        
        is_payment_submission = 'submit_payment' in request.POST

        if is_payment_submission:
            if not application.passport_photograph and 'passport_photograph_upload' not in request.FILES:
                form.add_error('passport_photograph_upload', 'Passport photograph is required to proceed.')
            if not application.documents.filter(document_type=Document.DocumentType.INTERNATIONAL_PASSPORT).exists() and 'international_passport_upload' not in request.FILES:
                form.add_error('international_passport_upload', 'International passport is required to proceed.')
            if not application.documents.filter(document_type=Document.DocumentType.SCHOOL_CERTIFICATE).exists() and 'school_certificate_upload' not in request.FILES:
                form.add_error('school_certificate_upload', 'School certificate is required to proceed.')
            if not application.documents.filter(document_type=Document.DocumentType.BIRTH_CERTIFICATE).exists() and 'birth_certificate_upload' not in request.FILES:
                form.add_error('birth_certificate_upload', 'Birth certificate is required to proceed.')

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
            return JsonResponse({'success': True, 'message': 'Application data saved successfully!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = StudentApplicationForm(instance=application)
    
    existing_docs = { doc.document_type: doc for doc in application.documents.all() }
    context = {
        'form': form, 'payment_made': payment_made,
        'existing_docs': existing_docs, 'doc_types': Document.DocumentType,
        'application_fee_amount': application_fee_amount
    }

    context.update(currency_context)
    return render(request, 'portal/student_application_form.html', context)

@login_required
def student_document_submission_view(request):
    application = request.user.student_application
    admin_document = Document.objects.filter(
        application=application, 
        is_admin_upload=True, 
        document_type=Document.DocumentType.BLANK_ADMISSION_FORM
    ).order_by('-uploaded_at').first()
    
    payment_made = Payment.objects.filter(
        application=application, 
        purpose=Payment.PaymentPurpose.ADMISSION_FEE, 
        status=Payment.PaymentStatus.SUCCESSFUL
    ).exists()
    
    default_fee = FeeStructure.objects.filter(fee_type='ADMISSION_FEE').first()
    default_fee_amount = default_fee.amount if default_fee else Decimal('1000.00')

    # Use the application's custom fee if it exists, otherwise use the default
    admission_fee_amount = application.custom_admission_fee or default_fee_amount

    currency_context = get_currency_context(request, admission_fee_amount)

    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            Document.objects.update_or_create(
                application=application,
                document_type=Document.DocumentType.FILLED_ADMISSION_FORM,
                defaults={'file': request.FILES['file']}
            )
            return JsonResponse({'success': True, 'message': 'Document uploaded successfully!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
            
    form = DocumentUploadForm()
    existing_docs = { doc.document_type: doc for doc in application.documents.all() }
    context = {
        'form': form, 'admin_document': admin_document, 
        'application': application, 'payment_made': payment_made,
        'existing_docs': existing_docs, 'doc_types': Document.DocumentType,
        'admission_fee_amount': admission_fee_amount
    }
    context.update(currency_context)
    return render(request, 'portal/student_document_submission.html', context)

@login_required
def student_agency_fee_view(request):
    application = request.user.student_application
    admission_letter = Document.objects.filter(application=application, document_type=Document.DocumentType.ADMISSION_LETTER, is_admin_upload=True).first()
    full_payment = Payment.objects.filter(application=application, purpose=Payment.PaymentPurpose.AGENCY_FEE_FULL, status=Payment.PaymentStatus.SUCCESSFUL).exists()
    half_payment_count = Payment.objects.filter(application=application, purpose=Payment.PaymentPurpose.AGENCY_FEE_HALF, status=Payment.PaymentStatus.SUCCESSFUL).count()
    
    payment_status = 'none'
    if full_payment or half_payment_count >= 2:
        payment_status = 'full_paid'
    elif half_payment_count == 1:
        payment_status = 'half_paid'
        
    # Get the default fee from the FeeStructure model
    default_fee = FeeStructure.objects.filter(fee_type='AGENCY_FEE').first()
    default_fee_amount = default_fee.amount if default_fee else Decimal('500.00')

    # Use the application's custom fee if it exists, otherwise use the default
    total_agency_fee = application.custom_agency_fee or default_fee_amount
    half_agency_fee = total_agency_fee * Decimal('0.50')

    full_currency_context = get_currency_context(request, total_agency_fee)
    half_currency_context = get_currency_context(request, half_agency_fee)

    context.update({
        'full_currency': full_currency_context,
        'half_currency': half_currency_context,
    })

    context = {
        'application': application, 'admission_letter': admission_letter,
        'payment_status': payment_status, 'total_agency_fee': total_agency_fee,  # Add total fee to context
        'half_agency_fee': half_agency_fee 
    }
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
        {'id': WorkApplication.WorkApplicationStatus.STEP_2_EMPLOYMENT_FORM, 'title': 'Employment Processing Form', 'number': 2, 'url_name': 'portal:work_employment_form'},
        {'id': WorkApplication.WorkApplicationStatus.STEP_3_JOB_OFFER, 'title': 'Employment Offer Letter', 'number': 3, 'url_name': 'portal:work_job_offer'},
        {'id': WorkApplication.WorkApplicationStatus.STEP_4_VISA_APPLICATION, 'title': 'Visa Application', 'number': 4, 'url_name': 'portal:work_visa_application'},
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
    payment_made = Payment.objects.filter(
        work_application=application, 
        purpose=Payment.PaymentPurpose.WORK_APP_FEE, 
        status=Payment.PaymentStatus.SUCCESSFUL
    ).exists()
    
    default_fee = FeeStructure.objects.filter(fee_type='WORK_APP_FEE').first()
    default_fee_amount = default_fee.amount if default_fee else Decimal('30.00')

    # Use the application's custom fee if it exists, otherwise use the default
    application_fee_amount = application.custom_application_fee or default_fee_amount

    currency_context = get_currency_context(request, application_fee_amount)

    
    if request.method == 'POST':
        form = WorkApplicationForm(request.POST, request.FILES, instance=application)
        is_payment_submission = 'submit_payment' in request.POST
        if is_payment_submission:
            if not application.passport_photograph and 'passport_photograph_upload' not in request.FILES:
                form.add_error('passport_photograph_upload', 'Passport photograph is required to proceed.')
            if not application.documents.filter(document_type=Document.DocumentType.INTERNATIONAL_PASSPORT).exists() and 'international_passport_upload' not in request.FILES:
                form.add_error('international_passport_upload', 'International passport is required to proceed.')
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
    existing_docs = { doc.document_type: doc for doc in application.documents.all() }
    context = {
        'form': form, 'payment_made': payment_made,
        'existing_docs': existing_docs, 'doc_types': Document.DocumentType,
        'application_fee_amount': application_fee_amount 
    }
    context.update(currency_context)
    return render(request, 'portal/work_application_form.html', context)

@login_required
def work_employment_form_view(request):
    application = request.user.work_application
    admin_document = Document.objects.filter(
        work_application=application, 
        is_admin_upload=True, 
        document_type=Document.DocumentType.BLANK_EMPLOYMENT_FORM
    ).order_by('-uploaded_at').first()
    payment_made = Payment.objects.filter(
        work_application=application, 
        purpose=Payment.PaymentPurpose.WORK_VISA_50_PERCENT, 
        status=Payment.PaymentStatus.SUCCESSFUL
    ).exists()
    fifty_percent_amount = 0
    if application.destination_country:
        fifty_percent_amount = application.destination_country.processing_fee * Decimal('0.50')
    if request.method == 'POST':
        doc_type = request.POST.get('doc_type')
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document_type_enum = Document.DocumentType.RESUME_CV if doc_type == 'cv' else Document.DocumentType.FILLED_EMPLOYMENT_FORM
            Document.objects.update_or_create(
                work_application=application,
                document_type=document_type_enum,
                defaults={'file': request.FILES['file']}
            )
            return JsonResponse({'success': True, 'message': 'Document uploaded successfully!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    form = DocumentUploadForm()
    existing_docs = { doc.document_type: doc for doc in application.documents.all() }
    context = {
        'form': form, 'admin_document': admin_document, 
        'application': application, 'payment_made': payment_made,
        'fifty_percent_amount': fifty_percent_amount,
        'existing_docs': existing_docs, 'doc_types': Document.DocumentType
    }
    if fifty_percent_amount:
        currency_context = get_currency_context(request, fifty_percent_amount)
        context.update(currency_context)
    return render(request, 'portal/work_employment_form.html', context)

@login_required
def work_job_offer_view(request):
    application = request.user.work_application
    if request.method == 'POST':
        application.job_offer_accepted = True
        application.save()
        return JsonResponse({'success': True, 'message': 'Offer accepted successfully!'})
    job_offer = Document.objects.filter(work_application=application, document_type=Document.DocumentType.JOB_OFFER, is_admin_upload=True).first()
    fifty_paid = Payment.objects.filter(work_application=application, purpose=Payment.PaymentPurpose.WORK_VISA_50_PERCENT, status=Payment.PaymentStatus.SUCCESSFUL).exists()
    final_fifty_paid = Payment.objects.filter(work_application=application, purpose=Payment.PaymentPurpose.WORK_VISA_FINAL_50_PERCENT, status=Payment.PaymentStatus.SUCCESSFUL).exists()
    twenty_five_paid_count = Payment.objects.filter(work_application=application, purpose=Payment.PaymentPurpose.WORK_VISA_25_PERCENT, status=Payment.PaymentStatus.SUCCESSFUL).count()
    payment_status = 'none'
    if final_fifty_paid or twenty_five_paid_count >= 2:
        payment_status = 'full_paid'
    elif fifty_paid:
        payment_status = 'half_paid'
    remaining_50_percent = 0
    remaining_25_percent = 0
    if application.destination_country:
        total_fee = application.destination_country.processing_fee
        remaining_50_percent = total_fee * Decimal('0.50')
        remaining_25_percent = total_fee * Decimal('0.25')

    
    context = {
        'application': application, 'job_offer': job_offer,
        'payment_status': payment_status, 
        'remaining_50_percent': remaining_50_percent,
        'remaining_25_percent': remaining_25_percent
    }

    if remaining_50_percent:
        full_currency_context = get_currency_context(request, remaining_50_percent)
        half_currency_context = get_currency_context(request, remaining_25_percent)
        context.update({
            'full_currency': full_currency_context,
            'half_currency': half_currency_context,
        })
    return render(request, 'portal/work_job_offer.html', context)

@login_required
def work_visa_application_view(request):
    application = request.user.work_application
    if request.method == 'POST':
        if Testimonial.objects.filter(work_application=application).exists():
            return JsonResponse({'success': False, 'message': 'You have already submitted a testimonial.'}, status=400)
        form = TestimonialForm(request.POST)
        if form.is_valid():
            testimonial = form.save(commit=False)
            testimonial.work_application = application
            testimonial.save()
            application.status = WorkApplication.WorkApplicationStatus.COMPLETED
            application.save()
            return JsonResponse({'success': True, 'message': 'Thank you for your feedback!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    twenty_five_paid_count = Payment.objects.filter(
        work_application=application, 
        purpose__in=[Payment.PaymentPurpose.WORK_VISA_25_PERCENT, Payment.PaymentPurpose.WORK_VISA_REMAINING_25_PERCENT], 
        status=Payment.PaymentStatus.SUCCESSFUL
    ).count()
    final_payment_needed = (twenty_five_paid_count == 1)
    final_25_percent_amount = 0
    if application.destination_country:
        final_25_percent_amount = application.destination_country.processing_fee * Decimal('0.25')
    visa_updates = application.visa_updates.all()
    testimonial = Testimonial.objects.filter(work_application=application).first()
    form = TestimonialForm(instance=testimonial)
    context = {
        'application': application, 'visa_updates': visa_updates,
        'testimonial_form': form, 'testimonial': testimonial,
        'final_payment_needed': final_payment_needed,
        'final_25_percent_amount': final_25_percent_amount
    }

    if final_25_percent_amount:
        currency_context = get_currency_context(request, final_25_percent_amount)
        context.update(currency_context)
        
    return render(request, 'portal/work_visa_application.html', context)

# --- Generic Payment & Webhook Views ---
@login_required
@require_POST
def initiate_payment(request):
    try:
        data = json.loads(request.body)
        purpose = data.get('purpose')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    fees = {fee.fee_type: fee.amount for fee in FeeStructure.objects.all()}
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

    currency = 'USD'
    
    if purpose == 'STUDENT_APP_FEE':
        # Use custom fee if available, otherwise use global default
        amount = application.custom_application_fee or fees.get('STUDENT_APP_FEE', Decimal('15.00'))
        currency = 'USD'
        payment_purpose = Payment.PaymentPurpose.STUDENT_APP_FEE
    elif purpose == 'ADMISSION_FEE':
        amount = application.custom_admission_fee or fees.get('ADMISSION_FEE', Decimal('1000.00'))
        payment_purpose = Payment.PaymentPurpose.ADMISSION_FEE
    elif purpose == 'AGENCY_FEE_HALF':
        total_agency_fee = application.custom_agency_fee or fees.get('AGENCY_FEE', Decimal('500.00'))
        amount = total_agency_fee * Decimal('0.50')
        payment_purpose = Payment.PaymentPurpose.AGENCY_FEE_HALF
    elif purpose == 'AGENCY_FEE_FULL':
        amount = application.custom_agency_fee or fees.get('AGENCY_FEE', Decimal('500.00'))
        payment_purpose = Payment.PaymentPurpose.AGENCY_FEE_FULL
    elif purpose == 'WORK_APP_FEE':
        amount = work_application.custom_application_fee or fees.get('WORK_APP_FEE', Decimal('30.00'))
        payment_purpose = Payment.PaymentPurpose.WORK_APP_FEE
    elif purpose == 'WORK_VISA_50_PERCENT':
        if not work_application or not work_application.destination_country: return JsonResponse({'error': 'Destination country not selected.'}, status=400)
        amount = work_application.destination_country.processing_fee * Decimal('0.50')
        payment_purpose = Payment.PaymentPurpose.WORK_VISA_50_PERCENT
    elif purpose == 'WORK_VISA_FINAL_50_PERCENT':
        if not work_application or not work_application.destination_country: return JsonResponse({'error': 'Destination country not selected.'}, status=400)
        amount = work_application.destination_country.processing_fee * Decimal('0.50')
        payment_purpose = Payment.PaymentPurpose.WORK_VISA_FINAL_50_PERCENT
    elif purpose == 'WORK_VISA_25_PERCENT':
        if not work_application or not work_application.destination_country: return JsonResponse({'error': 'Destination country not selected.'}, status=400)
        amount = work_application.destination_country.processing_fee * Decimal('0.25')
        payment_purpose = Payment.PaymentPurpose.WORK_VISA_25_PERCENT
    elif purpose == 'WORK_VISA_REMAINING_25_PERCENT':
        if not work_application or not work_application.destination_country:
            return JsonResponse({'error': 'Destination country not selected.'}, status=400)
        amount = work_application.destination_country.processing_fee * Decimal('0.25')
        payment_purpose = Payment.PaymentPurpose.WORK_VISA_REMAINING_25_PERCENT
    else:
        return JsonResponse({'error': 'Invalid payment purpose'}, status=400)

    tx_ref = f"HTG-{request.user.id}-{uuid.uuid4().hex[:6].upper()}"

    payment_currency = data.get('currency', 'USD')  # Get currency from frontend
    if payment_currency == 'NGN':
        from .utils import convert_usd_to_ngn
        # Convert to NGN if user chose NGN payment
        amount = convert_usd_to_ngn(amount)
        currency = 'NGN'
    else:
        currency = 'USD'
        
    Payment.objects.create(
        application=application, work_application=work_application,
        amount=amount, purpose=payment_purpose, tx_ref=tx_ref
    )
    
    redirect_url = request.build_absolute_uri(reverse('portal:payment_callback'))
    payment_data = {
        'public_key': settings.FLUTTERWAVE_PUBLIC_KEY, 'tx_ref': tx_ref, 'amount': str(amount),
        'currency': currency, 'redirect_url': redirect_url,
        'customer': {'email': customer_email, 'phonenumber': customer_phone, 'name': customer_name},
        'customizations': {'title': 'Hadey Travels Global', 'description': str(payment_purpose), 'logo': 'URL_TO_YOUR_LOGO_IMAGE'}
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
                    elif payment.purpose == Payment.PaymentPurpose.WORK_VISA_50_PERCENT:
                        application.status = WorkApplication.WorkApplicationStatus.STEP_3_JOB_OFFER
                    elif payment.purpose in [Payment.PaymentPurpose.WORK_VISA_FINAL_50_PERCENT, Payment.PaymentPurpose.WORK_VISA_25_PERCENT, Payment.PaymentPurpose.WORK_VISA_REMAINING_25_PERCENT]:
                        application.status = WorkApplication.WorkApplicationStatus.STEP_4_VISA_APPLICATION
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
    
    
@staff_member_required
def generate_pdf_view(request, app_type, app_id):
    """
    Generates a PDF summary for a given application.
    """
    template_path = 'portal/pdf_template.html'
    context = {}

    if app_type == 'student':
        app = get_object_or_404(Application, id=app_id)
        context['title'] = 'Student Application Summary'
        context['sections'] = {
            'Personal Information': {
                'Full Name': app.full_name,
                'Date of Birth': app.date_of_birth,
                'Place of Birth': app.place_of_birth,
                'Gender': app.gender,
                'Nationality': app.nationality,
                'Address': f"{app.address}, {app.city}, {app.postal_code}",
                'Contact': f"{app.phone_number} / {app.email}",
                'Passport Number': app.passport_number,
                'Passport Issue Date': app.passport_issue_date,
                'Passport Expiry Date': app.passport_expiry_date,
            },
            'Parent/Guardian Information': {
                "Father's Details": f"{app.father_name} ({app.father_occupation}) - {app.father_contact}",
                "Mother's Details": f"{app.mother_name} ({app.mother_occupation}) - {app.mother_contact}",
            },
            'Academic Information': {
                'Grade/Level': app.grade_level,
                'Preferred Program': app.preferred_program,
                'Previous School': app.previous_school,
                'Applying From': app.country_applying_from,
                'Applying To': app.country_of_interest,
            }
        }
    elif app_type == 'work':
        app = get_object_or_404(WorkApplication, id=app_id)
        context['title'] = 'Work Application Summary'
        context['sections'] = {
            'Personal Information': {
                'Full Name': app.full_name,
                'Date of Birth': app.date_of_birth,
                'Place of Birth': app.place_of_birth,
                'Gender': app.gender,
                'Nationality': app.nationality,
                'Marital Status': app.marital_status,
                'Address': app.current_address,
                'Contact': f"{app.contact_number} / {app.email}",
            },
            'Passport Information': {
                'Passport Number': app.passport_number,
                'Issue Date': app.passport_issue_date,
                'Expiry Date': app.passport_expiry_date,
            },
            'Employment & Visa Details': {
                'Applying For': app.job_title,
                'Sponsor': app.sponsor,
                'Destination Country': app.destination_country.name if app.destination_country else "N/A",
            }
        }
    else:
        return HttpResponse("Invalid application type", status=400)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="application_{app_type}_{app.user.username}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

