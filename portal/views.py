# portal/views.py

import uuid
import json
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from django.urls import reverse
from django.core.mail import send_mail # Import Django's email function
from django.template.loader import render_to_string # To render email templates
from .models import Application, Payment, Document
from .forms import ApplicationForm, DocumentUploadForm

# ... dashboard, application_form_view, document_submission_view, agency_fee_view, and initiate_payment views are unchanged ...
@login_required
def dashboard(request):
    application, _ = Application.objects.get_or_create(user=request.user)
    ALL_STEPS = [
        {'id': Application.ApplicationStatus.STEP_1_APPLICATION_FORM, 'title': 'Application Form', 'number': 1, 'url_name': 'portal:application_form'},
        {'id': Application.ApplicationStatus.STEP_2_ADMISSION_FEE, 'title': 'Admission Letter Fee', 'number': 2, 'url_name': 'portal:document_submission'},
        {'id': Application.ApplicationStatus.STEP_3_AGENCY_FEE, 'title': 'Agency Fee', 'number': 3, 'url_name': 'portal:agency_fee'},
        {'id': Application.ApplicationStatus.STEP_4_VISA_APPLICATION, 'title': 'Visa Application', 'number': 4, 'url_name': '#'},
    ]
    current_status = application.status
    try:
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
    return render(request, 'portal/dashboard.html', context)

@login_required
def application_form_view(request):
    application, _ = Application.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ApplicationForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Application saved successfully!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = ApplicationForm(instance=application)
    return render(request, 'portal/application_form.html', {'form': form})

@login_required
def document_submission_view(request):
    application = request.user.application
    admin_document = Document.objects.filter(application__isnull=True, is_admin_upload=True, document_type=Document.DocumentType.BLANK_FORM_TEMPLATE).order_by('-uploaded_at').first()
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.application = application
            document.document_type = Document.DocumentType.APPLICATION_FORM
            document.save()
            return JsonResponse({'success': True, 'message': 'Document uploaded successfully!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    form = DocumentUploadForm()
    context = {'form': form, 'admin_document': admin_document, 'application': application}
    return render(request, 'portal/document_submission.html', context)

@login_required
def agency_fee_view(request):
    application = request.user.application
    admission_letter = Document.objects.filter(application=application, document_type=Document.DocumentType.ADMISSION_LETTER, is_admin_upload=True).first()
    context = {'application': application, 'admission_letter': admission_letter}
    return render(request, 'portal/agency_fee.html', context)

@login_required
@require_POST
def initiate_payment(request):
    try:
        data = json.loads(request.body)
        purpose = data.get('purpose')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    application = request.user.application
    currency = 'NGN'
    if purpose == 'APPLICATION_FEE':
        amount = 15.00
        payment_purpose = Payment.PaymentPurpose.APPLICATION_FEE
        description = "Application Fee Payment"
    elif purpose == 'ADMISSION_FEE':
        amount = 1000.00
        currency = 'USD'
        payment_purpose = Payment.PaymentPurpose.ADMISSION_FEE
        description = "Admission Letter Fee Payment"
    elif purpose == 'AGENCY_FEE_HALF':
        amount = 250.00
        currency = 'USD'
        payment_purpose = Payment.PaymentPurpose.AGENCY_FEE_HALF
        description = "Agency Fee (Half Payment)"
    elif purpose == 'AGENCY_FEE_FULL':
        amount = 500.00
        currency = 'USD'
        payment_purpose = Payment.PaymentPurpose.AGENCY_FEE_FULL
        description = "Agency Fee (Full Payment)"
    else:
        return JsonResponse({'error': 'Invalid payment purpose'}, status=400)
    tx_ref = f"HTG-{application.id}-{uuid.uuid4().hex[:6].upper()}"
    Payment.objects.create(application=application, amount=amount, purpose=payment_purpose, tx_ref=tx_ref)
    redirect_url = request.build_absolute_uri(reverse('portal:payment_callback'))
    payment_data = {
        'public_key': settings.FLUTTERWAVE_PUBLIC_KEY, 'tx_ref': tx_ref, 'amount': str(amount),
        'currency': currency, 'redirect_url': redirect_url,
        'customer': {'email': application.email, 'phonenumber': application.phone_number, 'name': application.full_name},
        'customizations': {'title': 'Hadey Travels Global', 'description': description, 'logo': 'URL_TO_YOUR_LOGO_IMAGE'}
    }
    return JsonResponse(payment_data)

@csrf_exempt
def flutterwave_webhook(request):
    tx_ref = None
    transaction_id = None
    if request.method == 'POST':
        try:
            payload = json.loads(request.body)
            tx_ref = payload.get('data', {}).get('tx_ref')
            transaction_id = payload.get('data', {}).get('id')
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON in POST request'}, status=400)
    if not tx_ref:
        tx_ref = request.GET.get('tx_ref')
        transaction_id = request.GET.get('transaction_id')

    if not tx_ref or not transaction_id:
        return JsonResponse({'status': 'error', 'message': 'Missing transaction reference or ID'}, status=400)
    
    url = f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify"
    headers = {"Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data.get('status') == 'success':
            payment_data = data.get('data', {})
            payment = Payment.objects.get(tx_ref=payment_data.get('tx_ref'))
            
            if float(payment_data.get('amount')) == float(payment.amount) and payment.status == Payment.PaymentStatus.PENDING:
                payment.status = Payment.PaymentStatus.SUCCESSFUL
                payment.save()
                application = payment.application
                
                if payment.purpose == Payment.PaymentPurpose.APPLICATION_FEE:
                    application.status = Application.ApplicationStatus.STEP_2_ADMISSION_FEE
                elif payment.purpose == Payment.PaymentPurpose.ADMISSION_FEE:
                    application.status = Application.ApplicationStatus.STEP_3_AGENCY_FEE
                elif payment.purpose in [Payment.PaymentPurpose.AGENCY_FEE_FULL, Payment.PaymentPurpose.AGENCY_FEE_HALF]:
                    application.status = Application.ApplicationStatus.STEP_4_VISA_APPLICATION
                
                application.save()

                # --- SEND EMAIL NOTIFICATIONS ---
                user = application.user
                context = {
                    'user': user,
                    'payment': payment,
                    'dashboard_url': request.build_absolute_uri(reverse('portal:dashboard'))
                }
                
                # Send email to user
                user_email_body = render_to_string('portal/emails/payment_successful_user.txt', context)
                send_mail(
                    subject='Your Payment to Hadey Travels Global was Successful!',
                    message=user_email_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False # Set to True in production if you don't want errors to stop the request
                )

                # Send email to admin
                admin_email_body = render_to_string('portal/emails/payment_successful_admin.txt', context)
                send_mail(
                    subject=f'New Payment Received: {payment.get_purpose_display()} from {user.username}',
                    message=admin_email_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.ADMIN_EMAIL],
                    fail_silently=False
                )
                
                return redirect('portal:dashboard')
    except (requests.RequestException, Payment.DoesNotExist) as e:
        pass
    
    return redirect('portal:dashboard')
