# portal/views.py

import uuid
import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from django.urls import reverse # Import reverse
from .models import Application, Payment
from .forms import ApplicationForm

# ... dashboard view is unchanged ...
@login_required
def dashboard(request):
    application, _ = Application.objects.get_or_create(user=request.user)
    ALL_STEPS = [
        {'id': Application.ApplicationStatus.STEP_1_APPLICATION_FORM, 'title': 'Application Form', 'number': 1, 'url_name': 'portal:application_form'},
        {'id': Application.ApplicationStatus.STEP_2_ADMISSION_FEE, 'title': 'Admission Letter Fee', 'number': 2, 'url_name': '#'},
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
def initiate_payment_view(request):
    """
    Creates a Payment record and returns the necessary data for
    the Flutterwave inline popup.
    """
    application = request.user.application
    amount = 20000.00 
    tx_ref = f"HTG-{application.id}-{uuid.uuid4().hex[:6].upper()}"

    payment = Payment.objects.create(
        application=application,
        amount=amount,
        purpose=Payment.PaymentPurpose.APPLICATION_FEE,
        tx_ref=tx_ref,
    )

    # CORRECTED: Use reverse() to generate the correct URL dynamically
    redirect_url = request.build_absolute_uri(reverse('portal:payment_callback'))

    payment_data = {
        'public_key': settings.FLUTTERWAVE_PUBLIC_KEY,
        'tx_ref': tx_ref,
        'amount': str(amount),
        'currency': 'NGN',
        'redirect_url': redirect_url, # Use the correctly generated URL
        'customer': {
            'email': application.email,
            'phonenumber': application.phone_number,
            'name': application.full_name,
        },
        'customizations': {
            'title': 'Hadey Travels Global',
            'description': 'Application Fee Payment',
            'logo': 'URL_TO_YOUR_LOGO_IMAGE', 
        }
    }
    return JsonResponse(payment_data)


@csrf_exempt
def flutterwave_webhook(request):
    """
    Handles payment verification from Flutterwave.
    """
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
            tx_ref_from_fw = payment_data.get('tx_ref')
            amount_from_fw = payment_data.get('amount')

            try:
                payment = Payment.objects.get(tx_ref=tx_ref_from_fw)
                if float(amount_from_fw) == float(payment.amount):
                    payment.status = Payment.PaymentStatus.SUCCESSFUL
                    payment.save()
                    
                    application = payment.application
                    application.status = Application.ApplicationStatus.STEP_2_ADMISSION_FEE
                    application.save()
                    
                    return redirect('portal:dashboard')
                else:
                    payment.status = Payment.PaymentStatus.FAILED
                    payment.save()
            except Payment.DoesNotExist:
                pass
    except requests.RequestException as e:
        pass
    
    return redirect('portal:dashboard')
