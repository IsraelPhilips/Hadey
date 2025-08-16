# portal/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from .models import Document, VisaUpdate, WorkApplication

@receiver(post_save, sender=Document)
def send_email_on_admission_letter_upload(sender, instance, created, **kwargs):
    # ... this signal is unchanged ...
    if (created and 
        instance.is_admin_upload and 
        instance.application and 
        instance.document_type == Document.DocumentType.ADMISSION_LETTER):
        user = instance.application.user
        dashboard_url = f"http://127.0.0.1:8000{reverse('portal:dashboard')}"
        context = {'user': user, 'dashboard_url': dashboard_url}
        email_body = render_to_string('portal/emails/admission_letter_ready.txt', context)
        send_mail(
            subject='Your Admission Letter is Ready!',
            message=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )

@receiver(post_save, sender=Document)
def send_email_on_admin_upload(sender, instance, created, **kwargs):
    """
    Listen for when a Document is saved. If it's a new admin upload for a
    specific document type, send a notification email to the user.
    """
    if not (created and instance.is_admin_upload):
        return

    user = None
    dashboard_url = f"http://127.0.0.1:8000{reverse('portal:dashboard')}"
    context = {'dashboard_url': dashboard_url}
    subject = ''
    template_name = ''

    # Student Admission Letter
    if instance.application and instance.document_type == Document.DocumentType.ADMISSION_LETTER:
        user = instance.application.user
        subject = 'Your Admission Letter is Ready!'
        template_name = 'portal/emails/admission_letter_ready.txt'
        context['user'] = user

    # Worker Job Offer
    elif instance.work_application and instance.document_type == Document.DocumentType.JOB_OFFER:
        user = instance.work_application.user
        subject = 'Your Job Offer is Ready!'
        template_name = 'portal/emails/job_offer_ready.txt' # We need to create this template
        context['user'] = user

    if user and subject and template_name:
        email_body = render_to_string(template_name, context)
        send_mail(
            subject=subject,
            message=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )


@receiver(post_save, sender=VisaUpdate)
def send_email_on_visa_update(sender, instance, created, **kwargs):
    """
    Listen for when a VisaUpdate is saved. If it's a new update and the
    'send_email_notification' box was checked, send an email to the user.
    """
    # We only care about newly created updates where the admin opted to send an email
    if created and instance.send_email_notification:
        user = instance.application.user
        dashboard_url = f"http://127.0.0.1:8000{reverse('portal:dashboard')}"
        
        context = {
            'user': user,
            'update': instance, # Pass the update object to the template
            'dashboard_url': dashboard_url
        }
        
        email_body = render_to_string('portal/emails/visa_update_notification.txt', context)
        
        send_mail(
            subject='An Update on Your Visa Application',
            message=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )
