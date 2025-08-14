# portal/models.py

from django.db import models
from django.conf import settings

class Application(models.Model):
    # --- Main Application Status ---
    class ApplicationStatus(models.TextChoices):
        STEP_1_APPLICATION_FORM = 'STEP_1_APPLICATION_FORM', 'Step 1: Application Form'
        STEP_2_ADMISSION_FEE = 'STEP_2_ADMISSION_FEE', 'Step 2: Admission Fee'
        STEP_3_AGENCY_FEE = 'STEP_3_AGENCY_FEE', 'Step 3: Agency Fee'
        STEP_4_VISA_APPLICATION = 'STEP_4_VISA_APPLICATION', 'Step 4: Visa Application'
        COMPLETED = 'COMPLETED', 'Completed'
    
    class VisaStatus(models.TextChoices):
        NOT_STARTED = 'NOT_STARTED', 'Not Started'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='application')
    status = models.CharField(max_length=50, choices=ApplicationStatus.choices, default=ApplicationStatus.STEP_1_APPLICATION_FORM)
    visa_status = models.CharField(max_length=50, choices=VisaStatus.choices, default=VisaStatus.NOT_STARTED)
    
    passport_photograph = models.ImageField(upload_to='passport_photos/', blank=True, null=True)

    # --- Section 1: Personal Information (Now Mandatory) ---
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    place_of_birth = models.CharField(max_length=100)
    gender = models.CharField(max_length=20)
    nationality = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()

    # --- Section 2: Parent/Guardian Information (Mandatory Parents, Optional Guardian) ---
    father_name = models.CharField(max_length=255)
    father_occupation = models.CharField(max_length=100)
    father_contact = models.CharField(max_length=20)
    mother_name = models.CharField(max_length=255)
    mother_occupation = models.CharField(max_length=100)
    mother_contact = models.CharField(max_length=20)
    guardian_name = models.CharField(max_length=255, blank=True)
    guardian_relationship = models.CharField(max_length=100, blank=True)
    guardian_contact = models.CharField(max_length=20, blank=True)

    # --- Section 3: Academic Information (Mandatory except Achievements) ---
    grade_level = models.CharField(max_length=100)
    preferred_program = models.CharField(max_length=100)
    previous_school = models.CharField(max_length=255)
    country_applying_from = models.CharField(max_length=100)
    country_of_interest = models.CharField(max_length=100)
    achievements = models.TextField(blank=True)

    # --- Section 4: Emergency Contact (Mandatory) ---
    emergency_contact_name = models.CharField(max_length=255)
    emergency_contact_relationship = models.CharField(max_length=50)
    emergency_contact_number = models.CharField(max_length=20)
    
    # --- Section 5: Medical Information (Optional) ---
    medical_conditions = models.TextField(blank=True)
    allergies = models.TextField(blank=True)

    # --- Section 6: Additional Information (Mandatory) ---
    how_did_you_hear = models.CharField(max_length=255)
    declaration_agreed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Application for {self.user.username}"


class Document(models.Model):
    class DocumentType(models.TextChoices):
        PASSPORT_PHOTOGRAPH = 'PASSPORT_PHOTOGRAPH', 'Passport Photograph'
        INTERNATIONAL_PASSPORT = 'INTERNATIONAL_PASSPORT', 'International Passport'
        SCHOOL_CERTIFICATE = 'SCHOOL_CERTIFICATE', 'School Certificate (WAEC/NECO)'
        BIRTH_CERTIFICATE = 'BIRTH_CERTIFICATE', 'Birth Certificate'
        FILLED_APPLICATION_FORM = 'FILLED_APPLICATION_FORM', 'Filled Application Form (Step 2)'
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

class VisaUpdate(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='visa_updates')
    status_title = models.CharField(max_length=255)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    send_email_notification = models.BooleanField(default=False, help_text="Check this box to send an email notification to the user about this update.")
    class Meta:
        ordering = ['-created_at']
    def __str__(self):
        return f"Update for {self.application.user.username}: {self.status_title}"

class Testimonial(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='testimonial')
    content = models.TextField()
    rating = models.PositiveIntegerField(default=5)
    is_approved = models.BooleanField(default=False, help_text="Check this box to feature the testimonial on the public website.")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Testimonial from {self.application.user.username}"

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
