# portal/admin.py

from django.contrib import admin
from .models import Application, Document, Payment, VisaUpdate, Testimonial
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin

# 1. Create a custom AdminSite
class HadeyAdminSite(admin.AdminSite):
    site_title = 'Hadey Travels Global Site Admin'
    site_header = 'Hadey Travels Global Administration'
    index_title = 'Portal Administration'

    def get_app_list(self, request, app_label=None):
        app_list = super().get_app_list(request)
        app_list = [app for app in app_list if app['app_label'] not in ('account', 'socialaccount')]
        return app_list

# 2. Instantiate the custom admin site
hadey_admin_site = HadeyAdminSite(name='hadey_admin')

# 3. Register your models with the CUSTOM admin site
class VisaUpdateInline(admin.TabularInline):
    model = VisaUpdate
    extra = 1
    readonly_fields = ('created_at',)
    fields = ('status_title', 'details', 'send_email_notification', 'created_at')

class DocumentInline(admin.TabularInline):
    model = Document
    extra = 1
    # CORRECTED: Changed 'created_at' to 'uploaded_at' to match the model field
    readonly_fields = ('uploaded_at',)
    fields = ('document_type', 'file', 'is_admin_upload', 'uploaded_at')

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ('amount', 'status', 'purpose', 'tx_ref', 'created_at')
    can_delete = False
    def has_add_permission(self, request, obj=None): return False

class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'email', 'status', 'visa_status', 'updated_at')
    list_filter = ('status', 'visa_status', 'country_of_interest')
    search_fields = ('user__username', 'full_name', 'email')
    ordering = ('-updated_at',)
    
    # UPDATED: Reorganized fieldsets to include all new fields
    fieldsets = (
        ('Core Info', {
            'fields': ('user', 'status', 'visa_status', 'passport_photograph')
        }),
        ('Personal Information', {
            'classes': ('collapse',),
            'fields': ('full_name', 'date_of_birth', 'place_of_birth', 'gender', 'nationality', 'address', 'city', 'postal_code', 'phone_number', 'email')
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
    inlines = [VisaUpdateInline, DocumentInline, PaymentInline]

class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('application', 'rating', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'rating')
    search_fields = ('application__user__username', 'content')
    list_editable = ('is_approved',)
    readonly_fields = ('created_at', 'application')
    fields = ('application', 'content', 'rating', 'is_approved', 'created_at')

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('application', 'document_type', 'is_admin_upload', 'uploaded_at')
    list_filter = ('document_type', 'is_admin_upload', 'application')
    search_fields = ('application__user__username', 'application__full_name')
    readonly_fields = ('uploaded_at',)

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('application', 'purpose', 'amount', 'status', 'tx_ref', 'updated_at')
    list_filter = ('status', 'purpose')
    search_fields = ('application__user__username', 'tx_ref')
    readonly_fields = ('created_at', 'updated_at', 'tx_ref')

hadey_admin_site.register(Application, ApplicationAdmin)
hadey_admin_site.register(Testimonial, TestimonialAdmin)
hadey_admin_site.register(Document, DocumentAdmin)
hadey_admin_site.register(Payment, PaymentAdmin)
hadey_admin_site.register(User, UserAdmin)
# hadey_admin_site.register(Group, GroupAdmin)
