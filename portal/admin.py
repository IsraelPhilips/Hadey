# portal/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    Application, Document, Payment, VisaUpdate, Testimonial, 
    UserProfile, WorkApplication, Country, FeeStructure
)
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group

from django.contrib.sites.models import Site
from django.contrib.sites.admin import SiteAdmin

# --- Custom Admin Site ---
class HadeyAdminSite(admin.AdminSite):
    site_title = 'Hadey Travels Global Site Admin'
    site_header = 'Hadey Travels Global Administration'
    index_title = 'Portal Administration'

    def get_app_list(self, request, app_label=None):
        app_list = super().get_app_list(request)
        app_list = [app for app in app_list if app['app_label'] not in ('account', 'socialaccount')]
        return app_list

hadey_admin_site = HadeyAdminSite(name='hadey_admin')

# --- Inlines for STUDENT Application ---
class StudentVisaUpdateInline(admin.TabularInline):
    model = VisaUpdate
    extra = 1
    readonly_fields = ('created_at',)
    fields = ('status_title', 'details', 'send_email_notification', 'created_at')
    exclude = ('work_application',)
    verbose_name = "Student Visa Update"
    verbose_name_plural = "Student Visa Updates"

class StudentDocumentInline(admin.TabularInline):
    model = Document
    extra = 1
    readonly_fields = ('uploaded_at',)
    fields = ('document_type', 'file', 'is_admin_upload', 'uploaded_at')
    exclude = ('work_application',)
    verbose_name = "Student Document"
    verbose_name_plural = "Student Documents"

class StudentPaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ('amount', 'status', 'purpose', 'tx_ref', 'created_at')
    can_delete = False
    exclude = ('work_application',)
    verbose_name = "Student Payment"
    verbose_name_plural = "Student Payments"

# --- Inlines for WORK Application ---
class WorkerVisaUpdateInline(admin.TabularInline):
    model = VisaUpdate
    extra = 1
    readonly_fields = ('created_at',)
    fields = ('status_title', 'details', 'send_email_notification', 'created_at')
    exclude = ('application',)
    verbose_name = "Worker Visa Update"
    verbose_name_plural = "Worker Visa Updates"

class WorkerDocumentInline(admin.TabularInline):
    model = Document
    extra = 1
    readonly_fields = ('uploaded_at',)
    fields = ('document_type', 'file', 'is_admin_upload', 'uploaded_at')
    exclude = ('application',)
    verbose_name = "Worker Document"
    verbose_name_plural = "Worker Documents"

class WorkerPaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ('amount', 'status', 'purpose', 'tx_ref', 'created_at')
    can_delete = False
    exclude = ('application',)
    verbose_name = "Worker Payment"
    verbose_name_plural = "Worker Payments"

# --- ModelAdmins ---
class ApplicationAdmin(admin.ModelAdmin): # Student Application Admin
    list_display = ('user', 'full_name', 'email', 'status', 'visa_status', 'updated_at')
    list_filter = ('status', 'visa_status', 'country_of_interest')
    search_fields = ('user__username', 'full_name', 'email')
    ordering = ('-updated_at',)
    inlines = [StudentVisaUpdateInline, StudentDocumentInline, StudentPaymentInline]
    fieldsets = (
        ('Fee Overrides (Optional)', {
            'classes': ('collapse',),
            'fields': ('custom_application_fee', 'custom_admission_fee', 'custom_agency_fee')
        }),
        ('Core Info', {'fields': ('user', 'status', 'visa_status', 'passport_photograph')}),
        ('Personal Information', {
            'classes': ('collapse',),
            'fields': ('full_name', 'date_of_birth', 'place_of_birth', 'gender', 'nationality', 'address', 'city', 'postal_code', 'phone_number', 'email', 'passport_number', 'passport_issue_date', 'passport_expiry_date')
        }),
        ('Parent/Guardian Information', {
            'classes': ('collapse',),
            'fields': ('father_name', 'father_occupation', 'father_contact', 'mother_name', 'mother_occupation', 'mother_contact', 'guardian_name', 'guardian_relationship', 'guardian_contact')
        }),
        ('Academic Information', {
            'classes': ('collapse',),
            'fields': ('grade_level', 'preferred_program', 'previous_school', 'country_applying_from', 'country_of_interest', 'achievements')
        }),
        ('Emergency & Medical', {
            'classes': ('collapse',),
            'fields': ('emergency_contact_name', 'emergency_contact_relationship', 'emergency_contact_number', 'medical_conditions', 'allergies')
        }),
        ('Additional Info', {
            'classes': ('collapse',),
            'fields': ('how_did_you_hear', 'declaration_agreed')
        }),
        ('Timestamps', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

class WorkApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'email', 'status', 'destination_country', 'updated_at')
    list_filter = ('status', 'destination_country')
    search_fields = ('user__username', 'full_name', 'email')
    ordering = ('-updated_at',)
    inlines = [WorkerVisaUpdateInline, WorkerDocumentInline, WorkerPaymentInline]
    
    fieldsets = (
        ('Fee Override (Optional)', {
            'classes': ('collapse',),
            'fields': ('custom_application_fee',)
        }),
        ('Core Info', {'fields': ('user', 'status', 'visa_status', 'passport_photograph')}),
        ('Personal Information', {'classes': ('collapse',), 'fields': ('full_name', 'gender', 'date_of_birth', 'place_of_birth', 'nationality', 'passport_number', 'passport_issue_date', 'passport_expiry_date', 'marital_status', 'current_address', 'contact_number', 'email')}),
        ('Employment & Visa Details', {'classes': ('collapse',), 'fields': ('job_title', 'sponsor', 'destination_country', 'applied_before', 'previous_application_details')}),
        ('Professional Background', {'classes': ('collapse',), 'fields': ('highest_qualification', 'field_of_study', 'years_of_experience', 'skills_certifications')}),
        ('Consent', {'fields': ('declaration_agreed', 'job_offer_accepted')}),
        ('Timestamps', {'classes': ('collapse',), 'fields': ('created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at')

class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'processing_fee')
    search_fields = ('name',)

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_account_type')

    def get_account_type(self, instance):
        try:
            return instance.profile.get_account_type_display()
        except UserProfile.DoesNotExist:
            return "No Profile"
    get_account_type.short_description = 'Account Type'

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'account_type')
    list_filter = ('account_type',)
    search_fields = ('user__username',)

class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('get_fee_type_display', 'amount')

# --- Registration ---
hadey_admin_site.register(Application, ApplicationAdmin)
hadey_admin_site.register(WorkApplication, WorkApplicationAdmin)
hadey_admin_site.register(Country, CountryAdmin)
hadey_admin_site.register(Testimonial)
hadey_admin_site.register(Document)
hadey_admin_site.register(Payment)
hadey_admin_site.register(UserProfile, UserProfileAdmin)
hadey_admin_site.register(FeeStructure, FeeStructureAdmin) # ADDED THIS LINE


# Re-register User to our custom site, unregistering the base one first
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass
hadey_admin_site.register(User, UserAdmin)
hadey_admin_site.register(Group)
hadey_admin_site.register(Site, SiteAdmin)
