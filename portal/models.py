# portal/models.py

from django.db import models
from django.conf import settings

class Application(models.Model):
    class ApplicationStatus(models.TextChoices):
        STEP_1_APPLICATION_FORM = 'STEP_1_APPLICATION_FORM', 'Step 1: Application Form'
        STEP_2_ADMISSION_FEE = 'STEP_2_ADMISSION_FEE', 'Step 2: Admission Fee'
        STEP_3_AGENCY_FEE = 'STEP_3_AGENCY_FEE', 'Step 3: Agency Fee'
        STEP_4_VISA_APPLICATION = 'STEP_4_VISA_APPLICATION', 'Step 4: Visa Application'
        COMPLETED = 'COMPLETED', 'Completed'
    
    # ADDED: A field to track the specific visa process status
    class VisaStatus(models.TextChoices):
        NOT_STARTED = 'NOT_STARTED', 'Not Started'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='application')
    status = models.CharField(max_length=50, choices=ApplicationStatus.choices, default=ApplicationStatus.STEP_1_APPLICATION_FORM)
    visa_status = models.CharField(max_length=50, choices=VisaStatus.choices, default=VisaStatus.NOT_STARTED)
    
    full_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    country_of_interest = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Application for {self.user.username} ({self.get_status_display()})"

class VisaUpdate(models.Model):
    """
    A model to store a timeline of visa status updates for an application.
    """
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='visa_updates')
    status_title = models.CharField(max_length=255)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at'] # Show the newest updates first

    def __str__(self):
        return f"Update for {self.application.user.username}: {self.status_title}"

class Testimonial(models.Model):
    """
    A model to store user testimonials.
    """
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='testimonial')
    content = models.TextField()
    rating = models.PositiveIntegerField(default=5) # e.g., 1-5 stars
    is_approved = models.BooleanField(default=False, help_text="Check this box to feature the testimonial on the public website.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Testimonial from {self.application.user.username}"


class Document(models.Model):
    # ... Document model is unchanged ...
    class DocumentType(models.TextChoices):
        APPLICATION_FORM = 'APPLICATION_FORM', 'Application Form (Filled)'
        ADMISSION_LETTER = 'ADMISSION_LETTER', 'Admission Letter'
        BLANK_FORM_TEMPLATE = 'BLANK_FORM_TEMPLATE', 'Blank Form Template'
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='documents', blank=True, null=True)
    document_type = models.CharField(max_length=50, choices=DocumentType.choices)
    file = models.FileField(upload_to='documents/')
    is_admin_upload = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        if self.application: return f"{self.get_document_type_display()} for {self.application.user.username}"
        return f"Global Document: {self.get_document_type_display()}"

class Payment(models.Model):
    # ... Payment model is unchanged ...
    class PaymentStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        SUCCESSFUL = 'SUCCESSFUL', 'Successful'
        FAILED = 'FAILED', 'Failed'
    class PaymentPurpose(models.TextChoices):
        APPLICATION_FEE = 'APPLICATION_FEE', 'Application Fee'
        ADMISSION_FEE = 'ADMISSION_FEE', 'Admission Fee'
        AGENCY_FEE_FULL = 'AGENCY_FEE_FULL', 'Agency Fee (Full)'
        AGENCY_FEE_HALF = 'AGENCY_FEE_HALF', 'Agency Fee (Half)'
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    purpose = models.CharField(max_length=50, choices=PaymentPurpose.choices)
    tx_ref = models.CharField(max_length=100, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.purpose} - {self.status} ({self.application.user.username})"
