# portal/models.py

from django.db import models
from django.conf import settings

class UserProfile(models.Model):
    class AccountType(models.TextChoices):
        STUDENT = 'STUDENT', 'Student'
        WORKER = 'WORKER', 'Worker'
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    account_type = models.CharField(max_length=10, choices=AccountType.choices)
    def __str__(self):
        return f"{self.user.username} - {self.get_account_type_display()}"

class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    processing_fee = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total processing fee in USD")
    class Meta:
        verbose_name_plural = "Countries"
        ordering = ['name']
    def __str__(self):
        return self.name

class Application(models.Model): # STUDENT Application
    class Meta:
        # This sets the display name in the admin panel
        verbose_name = "Student Application"
        verbose_name_plural = "Student Applications"

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

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_application')
    status = models.CharField(max_length=50, choices=ApplicationStatus.choices, default=ApplicationStatus.STEP_1_APPLICATION_FORM)
    visa_status = models.CharField(max_length=50, choices=VisaStatus.choices, default=VisaStatus.NOT_STARTED)
    passport_photograph = models.ImageField(upload_to='passport_photos/', blank=True, null=True)

    custom_application_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Overrides the default student application fee (USD).")
    custom_admission_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Overrides the default admission fee (USD).")
    custom_agency_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Overrides the default total agency fee (USD).")
    
    passport_number = models.CharField(max_length=100, blank=True, null=True)
    passport_issue_date = models.DateField(blank=True, null=True)
    passport_expiry_date = models.DateField(blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    place_of_birth = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    father_name = models.CharField(max_length=255, blank=True, null=True)
    father_occupation = models.CharField(max_length=100, blank=True, null=True)
    father_contact = models.CharField(max_length=20, blank=True, null=True)
    mother_name = models.CharField(max_length=255, blank=True, null=True)
    mother_occupation = models.CharField(max_length=100, blank=True, null=True)
    mother_contact = models.CharField(max_length=20, blank=True, null=True)
    guardian_name = models.CharField(max_length=255, blank=True)
    guardian_relationship = models.CharField(max_length=100, blank=True)
    guardian_contact = models.CharField(max_length=20, blank=True)
    grade_level = models.CharField(max_length=100, blank=True, null=True)
    preferred_program = models.CharField(max_length=100, blank=True, null=True)
    previous_school = models.CharField(max_length=255, blank=True, null=True)
    country_applying_from = models.CharField(max_length=100, blank=True, null=True)
    country_of_interest = models.CharField(max_length=100, blank=True, null=True)
    achievements = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=255, blank=True, null=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True, null=True)
    emergency_contact_number = models.CharField(max_length=20, blank=True, null=True)
    medical_conditions = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    how_did_you_hear = models.CharField(max_length=255, blank=True, null=True)
    declaration_agreed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Student Application for {self.user.username}"

class WorkApplication(models.Model):
    class Meta:
        # This sets the display name in the admin panel
        verbose_name = "Work Application"
        verbose_name_plural = "Work Applications"
        
    class WorkApplicationStatus(models.TextChoices):
        STEP_1_APPLICATION_FORM = 'STEP_1_APPLICATION_FORM', 'Step 1: Application Form'
        STEP_2_EMPLOYMENT_FORM = 'STEP_2_EMPLOYMENT_FORM', 'Step 2: Employment Form & 50% Fee'
        STEP_3_JOB_OFFER = 'STEP_3_JOB_OFFER', 'Step 3: Job Offer & Final Fee'
        STEP_4_VISA_APPLICATION = 'STEP_4_VISA_APPLICATION', 'Step 4: Visa Application'
        COMPLETED = 'COMPLETED', 'Completed'
    class VisaStatus(models.TextChoices):
        NOT_STARTED = 'NOT_STARTED', 'Not Started'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='work_application')
    status = models.CharField(max_length=50, choices=WorkApplicationStatus.choices, default=WorkApplicationStatus.STEP_1_APPLICATION_FORM)
    visa_status = models.CharField(max_length=50, choices=VisaStatus.choices, default=VisaStatus.NOT_STARTED)
    passport_photograph = models.ImageField(upload_to='passport_photos/', blank=True, null=True)
    custom_application_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Overrides the default work application fee (USD).")

    full_name = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    place_of_birth = models.CharField(max_length=100, blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    passport_number = models.CharField(max_length=100, blank=True, null=True)
    passport_issue_date = models.DateField(blank=True, null=True)
    passport_expiry_date = models.DateField(blank=True, null=True)
    marital_status = models.CharField(max_length=20, blank=True, null=True)
    current_address = models.CharField(max_length=255, blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    job_title = models.CharField(max_length=255, blank=True, null=True)
    sponsor = models.CharField(max_length=100, blank=True, null=True)
    destination_country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    applied_before = models.BooleanField(default=False)
    previous_application_details = models.TextField(blank=True)
    highest_qualification = models.CharField(max_length=255, blank=True, null=True)
    field_of_study = models.CharField(max_length=255, blank=True, null=True)
    years_of_experience = models.CharField(max_length=50, blank=True, null=True)
    skills_certifications = models.TextField(blank=True)
    declaration_agreed = models.BooleanField(default=False)
    job_offer_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Work Application for {self.user.username}"

class Document(models.Model):
    class DocumentType(models.TextChoices):
        # Student Path
        INTERNATIONAL_PASSPORT = 'INTERNATIONAL_PASSPORT', 'International Passport'
        SCHOOL_CERTIFICATE = 'SCHOOL_CERTIFICATE', 'School Certificate (WAEC/NECO)'
        BIRTH_CERTIFICATE = 'BIRTH_CERTIFICATE', 'Birth Certificate'
        ADMISSION_LETTER = 'ADMISSION_LETTER', 'Admission Letter'
        BLANK_ADMISSION_FORM = 'BLANK_ADMISSION_FORM', 'Blank Admission Form'
        FILLED_ADMISSION_FORM = 'FILLED_ADMISSION_FORM', 'Filled Admission Form'
        
        # Worker Path
        RESUME_CV = 'RESUME_CV', 'Resume/CV'
        WORK_EXPERIENCE_LETTER = 'WORK_EXPERIENCE_LETTER', 'Work Experience Letter'
        JOB_OFFER = 'JOB_OFFER', 'Job Offer'
        BLANK_EMPLOYMENT_FORM = 'BLANK_EMPLOYMENT_FORM', 'Blank Employment Form'
        FILLED_EMPLOYMENT_FORM = 'FILLED_EMPLOYMENT_FORM', 'Filled Employment Form'

    # CORRECTED: These are now tied to one or the other, never global for these types
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='documents', blank=True, null=True)
    work_application = models.ForeignKey(WorkApplication, on_delete=models.CASCADE, related_name='documents', blank=True, null=True)
    
    document_type = models.CharField(max_length=50, choices=DocumentType.choices)
    file = models.FileField(upload_to='documents/')
    is_admin_upload = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        if self.application: return f"{self.get_document_type_display()} for {self.application.user.username}"
        if self.work_application: return f"{self.get_document_type_display()} for {self.work_application.user.username}"
        return f"Global Document: {self.get_document_type_display()}"

class VisaUpdate(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='visa_updates', null=True, blank=True)
    work_application = models.ForeignKey(WorkApplication, on_delete=models.CASCADE, related_name='visa_updates', null=True, blank=True)
    status_title = models.CharField(max_length=255)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    send_email_notification = models.BooleanField(default=False, help_text="Check this box to send an email notification to the user about this update.")
    class Meta:
        ordering = ['-created_at']
    def __str__(self):
        return f"Update for {self.application.user.username if self.application else self.work_application.user.username}: {self.status_title}"

class Testimonial(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='testimonial', null=True, blank=True)
    work_application = models.OneToOneField(WorkApplication, on_delete=models.CASCADE, related_name='testimonial', null=True, blank=True)
    content = models.TextField()
    rating = models.PositiveIntegerField(default=5)
    is_approved = models.BooleanField(default=False, help_text="Check this box to feature the testimonial on the public website.")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        user = self.application.user if self.application else self.work_application.user
        return f"Testimonial from {user.username}"

class Payment(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        SUCCESSFUL = 'SUCCESSFUL', 'Successful'
        FAILED = 'FAILED', 'Failed'
    class PaymentPurpose(models.TextChoices):
        STUDENT_APP_FEE = 'STUDENT_APP_FEE', 'Student Application Fee'
        ADMISSION_FEE = 'ADMISSION_FEE', 'Admission Fee'
        AGENCY_FEE_FULL = 'AGENCY_FEE_FULL', 'Agency Fee (Full)'
        AGENCY_FEE_HALF = 'AGENCY_FEE_HALF', 'Agency Fee (Half)'
        WORK_APP_FEE = 'WORK_APP_FEE', 'Work Application Fee'
        WORK_VISA_50_PERCENT = 'WORK_VISA_50_PERCENT', 'Work Visa Fee (50%)'
        WORK_VISA_25_PERCENT = 'WORK_VISA_25_PERCENT', 'Work Visa Fee (25%)'
        # CORRECTED: Added the missing payment purpose
        WORK_VISA_FINAL_50_PERCENT = 'WORK_VISA_FINAL_50_PERCENT', 'Work Visa Fee (Final 50%)'
        WORK_VISA_REMAINING_25_PERCENT = 'WORK_VISA_REMAINING_25_PERCENT', 'Work Visa Fee (Remaining 25%)'

    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    work_application = models.ForeignKey(WorkApplication, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    purpose = models.CharField(max_length=50, choices=PaymentPurpose.choices)
    tx_ref = models.CharField(max_length=100, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.purpose} - {self.status}"



class FeeStructure(models.Model):
    """
    A model to store all application fees, manageable from the admin panel.
    """
    class FeeType(models.TextChoices):
        STUDENT_APP_FEE = 'STUDENT_APP_FEE', 'Student Application Fee (USD)'
        ADMISSION_FEE = 'ADMISSION_FEE', 'Student Admission Fee (USD)'
        AGENCY_FEE = 'AGENCY_FEE', 'Student Agency Fee (USD)'
        WORK_APP_FEE = 'WORK_APP_FEE', 'Work Application Fee (USD)'

    fee_type = models.CharField(max_length=50, choices=FeeType.choices, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.get_fee_type_display()}: {self.amount}"