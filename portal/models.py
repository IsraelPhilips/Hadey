# portal/models.py

from django.db import models
from django.conf import settings

class Application(models.Model):
    class ApplicationStatus(models.TextChoices):
        STEP_1_APPLICATION_FORM = 'STEP_1_APPLICATION_FORM', 'Step 1: Application Form'
        STEP_2_ADMISSION_FEE = 'STEP_2_ADMISSION_FEE', 'Step 2: Admission Fee'
        STEP_3_AGENCY_FEE = 'STEP_3_AGENCY_FEE', 'Step 3: Agency Fee'
        STEP_4_VISA_APPLICATION = 'STEP_4_VISA_APPLICATION', 'Step 4: Visa Application'
        # ADDED: A final status for when the process is complete
        COMPLETED = 'COMPLETED', 'Completed'
        
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='application')
    status = models.CharField(max_length=50, choices=ApplicationStatus.choices, default=ApplicationStatus.STEP_1_APPLICATION_FORM)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    country_of_interest = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Application for {self.user.username} ({self.get_status_display()})"

class Document(models.Model):
    class DocumentType(models.TextChoices):
        APPLICATION_FORM = 'APPLICATION_FORM', 'Application Form (Filled)'
        ADMISSION_LETTER = 'ADMISSION_LETTER', 'Admission Letter'
        BLANK_FORM_TEMPLATE = 'BLANK_FORM_TEMPLATE', 'Blank Form Template'
    application = models.ForeignKey(
        Application, 
        on_delete=models.CASCADE, 
        related_name='documents',
        blank=True,
        null=True
    )
    document_type = models.CharField(max_length=50, choices=DocumentType.choices)
    file = models.FileField(upload_to='documents/')
    is_admin_upload = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        if self.application:
            return f"{self.get_document_type_display()} for {self.application.user.username}"
        return f"Global Document: {self.get_document_type_display()}"

class Payment(models.Model):
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
