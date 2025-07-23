# portal/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from .models import Document

@receiver(post_save, sender=Document)
def send_email_on_admission_letter_upload(sender, instance, created, **kwargs):
    """
    Listen for when a Document is saved. If it's a new admission letter
    uploaded by an admin, send a notification email to the user.
    """
    # 'instance' is the Document object that was just saved.
    # 'created' is True if this is a new record.
    
    # We only care about newly created documents that are admin uploads
    # for a specific application and are of type ADMISSION_LETTER.
    if (created and 
        instance.is_admin_upload and 
        instance.application and 
        instance.document_type == Document.DocumentType.ADMISSION_LETTER):
        
        user = instance.application.user
        
        # We need to build the full URL. Since we are not in a request-response
        # cycle, we cannot use request.build_absolute_uri.
        # This assumes your site is served over https.
        # In production, you might get the domain from Django's Sites framework.
        dashboard_url = f"http://127.0.0.1:8000{reverse('portal:dashboard')}"

        context = {
            'user': user,
            'dashboard_url': dashboard_url
        }
        
        email_body = render_to_string('portal/emails/admission_letter_ready.txt', context)
        
        send_mail(
            subject='Your Admission Letter is Ready!',
            message=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )
