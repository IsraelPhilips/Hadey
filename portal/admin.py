# portal/admin.py

from django.contrib import admin
from .models import Application, Document, Payment, VisaUpdate, Testimonial # Import new models

class VisaUpdateInline(admin.TabularInline):
    """
    Allows adding Visa Updates directly within the Application view.
    """
    model = VisaUpdate
    extra = 1 # Show one empty form to add a new update
    readonly_fields = ('created_at',)
    fields = ('status_title', 'details', 'created_at')

class DocumentInline(admin.TabularInline):
    model = Document
    extra = 1
    readonly_fields = ('uploaded_at',)
    fields = ('document_type', 'file', 'is_admin_upload', 'uploaded_at')

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ('amount', 'status', 'purpose', 'tx_ref', 'created_at')
    can_delete = False
    def has_add_permission(self, request, obj=None): return False

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'email', 'status', 'visa_status', 'updated_at')
    list_filter = ('status', 'visa_status', 'country_of_interest')
    search_fields = ('user__username', 'full_name', 'email')
    ordering = ('-updated_at',)
    fieldsets = (
        ('Applicant Information', {'fields': ('user', 'full_name', 'email', 'phone_number')}),
        ('Application Details', {'fields': ('status', 'visa_status', 'country_of_interest')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ('created_at', 'updated_at')
    # Add the new VisaUpdateInline
    inlines = [VisaUpdateInline, DocumentInline, PaymentInline]

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    """
    Admin view for managing testimonials.
    """
    list_display = ('application', 'rating', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'rating')
    search_fields = ('application__user__username', 'content')
    # Add 'is_approved' to the editable list for quick toggling
    list_editable = ('is_approved',)
    readonly_fields = ('created_at', 'application')
    fields = ('application', 'content', 'rating', 'is_approved', 'created_at')

# ... other admin classes are unchanged ...
@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('application', 'document_type', 'is_admin_upload', 'uploaded_at')
    list_filter = ('document_type', 'is_admin_upload', 'application')
    search_fields = ('application__user__username', 'application__full_name')
    readonly_fields = ('uploaded_at',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('application', 'purpose', 'amount', 'status', 'tx_ref', 'updated_at')
    list_filter = ('status', 'purpose')
    search_fields = ('application__user__username', 'tx_ref')
    readonly_fields = ('created_at', 'updated_at', 'tx_ref')
