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
from .models import Application, Payment, Document
from .forms import ApplicationForm, DocumentUploadForm

# ... dashboard view is unchanged ...
@login_required
def dashboard(request):
    application, _ = Application.objects.get_or_create(user=request.user)
    ALL_STEPS = [
        {'id': Application.ApplicationStatus.STEP_1_APPLICATION_FORM, 'title': 'Application Form', 'number': 1, 'url_name': 'portal:application_form'},
        {'id': Application.ApplicationStatus.STEP_2_ADMISSION_FEE, 'title': 'Admission Letter Fee', 'number': 2, 'url_name': 'portal:document_submission'},
        {'id': Application.ApplicationStatus.STEP_3_AGENCY_FEE, 'title': 'Agency Fee', 'number': 3, 'url_name': '#'},
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


# ... application_form_view is unchanged ...
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
    """
    Handles the document download/upload process for Step 2.
    """
    application = request.user.application
    
    # UPDATED: Fetch the most recent GLOBAL form uploaded by an admin.
    # A global form is one not tied to any specific application.
    admin_document = Document.objects.filter(
        application__isnull=True, 
        is_admin_upload=True,
        document_type=Document.DocumentType.BLANK_FORM_TEMPLATE
    ).order_by('-uploaded_at').first()

    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            # The student's upload IS tied to their application
            document.application = application
            document.document_type = Document.DocumentType.APPLICATION_FORM
            document.save()
            return JsonResponse({'success': True, 'message': 'Document uploaded successfully!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    form = DocumentUploadForm()
    context = {
        'form': form,
        'admin_document': admin_document,
        'application': application,
    }
    return render(request, 'portal/document_submission.html', context)


# ... payment views are unchanged ...
@login_required
@require_POST
def initiate_payment(request):
    try:
        data = json.loads(request.body)
        purpose = data.get('purpose')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    application = request.user.application
    if purpose == 'APPLICATION_FEE':
        amount = 20000.00
        payment_purpose = Payment.PaymentPurpose.APPLICATION_FEE
        description = "Application Fee Payment"
    elif purpose == 'ADMISSION_FEE':
        amount = 1000.00
        payment_purpose = Payment.PaymentPurpose.ADMISSION_FEE
        description = "Admission Letter Fee Payment"
    else:
        return JsonResponse({'error': 'Invalid payment purpose'}, status=400)
    tx_ref = f"HTG-{application.id}-{uuid.uuid4().hex[:6].upper()}"
    Payment.objects.create(application=application, amount=amount, purpose=payment_purpose, tx_ref=tx_ref)
    redirect_url = request.build_absolute_uri(reverse('portal:payment_callback'))
    payment_data = {
        'public_key': settings.FLUTTERWAVE_PUBLIC_KEY, 'tx_ref': tx_ref, 'amount': str(amount),
        'currency': 'NGN', 'redirect_url': redirect_url,
        'customer': {'email': application.email, 'phonenumber': application.phone_number, 'name': application.full_name},
        'customizations': {'title': 'Hadey Travels Global', 'description': description, 'logo': 'URL_TO_YOUR_LOGO_IMAGE'}
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
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data.get('status') == 'success':
            payment_data = data.get('data', {})
            payment = Payment.objects.get(tx_ref=payment_data.get('tx_ref'))
            if float(payment_data.get('amount')) == float(payment.amount):
                payment.status = Payment.PaymentStatus.SUCCESSFUL
                payment.save()
                application = payment.application
                if payment.purpose == Payment.PaymentPurpose.APPLICATION_FEE:
                    application.status = Application.ApplicationStatus.STEP_2_ADMISSION_FEE
                elif payment.purpose == Payment.PaymentPurpose.ADMISSION_FEE:
                    application.status = Application.ApplicationStatus.STEP_3_AGENCY_FEE
                application.save()
                return redirect('portal:dashboard')
    except (requests.RequestException, Payment.DoesNotExist) as e:
        pass
    return redirect('portal:dashboard')
