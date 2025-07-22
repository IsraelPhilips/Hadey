# portal/admin.py

from django.contrib import admin
from .models import Application, Document, Payment

# Register your models here.

class DocumentInline(admin.TabularInline):
    """
    Allows viewing and adding Documents directly within the Application view
    in the admin panel. This is more user-friendly than managing them separately.
    """
    model = Document
    extra = 1 # Number of empty forms to display
    readonly_fields = ('uploaded_at',)
    fields = ('document_type', 'file', 'is_admin_upload', 'uploaded_at')


class PaymentInline(admin.TabularInline):
    """
    Allows viewing Payments directly within the Application view.
    """
    model = Payment
    extra = 0 # Don't show empty forms, just list existing payments
    readonly_fields = ('amount', 'status', 'purpose', 'tx_ref', 'created_at')
    can_delete = False # Usually, we don't want to delete payment records

    def has_add_permission(self, request, obj=None):
        # Disable adding payments from the admin directly
        return False


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    """
    Customizes the admin interface for the Application model.
    """
    list_display = (
        'user',
        'full_name',
        'email',
        'status',
        'country_of_interest',
        'updated_at'
    )
    list_filter = ('status', 'country_of_interest')
    search_fields = ('user__username', 'full_name', 'email')
    ordering = ('-updated_at',)
    fieldsets = (
        ('Applicant Information', {
            'fields': ('user', 'full_name', 'email', 'phone_number')
        }),
        ('Application Details', {
            'fields': ('status', 'country_of_interest')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    inlines = [DocumentInline, PaymentInline]


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """
    Customizes the admin interface for the Document model.
    """
    list_display = ('application', 'document_type', 'is_admin_upload', 'uploaded_at')
    list_filter = ('document_type', 'is_admin_upload')
    search_fields = ('application__user__username', 'application__full_name')
    readonly_fields = ('uploaded_at',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Customizes the admin interface for the Payment model.
    """
    # CORRECTED: Replaced 'paystack_reference' with 'tx_ref'
    list_display = ('application', 'purpose', 'amount', 'status', 'tx_ref', 'updated_at')
    list_filter = ('status', 'purpose')
    # CORRECTED: Replaced 'paystack_reference' with 'tx_ref'
    search_fields = ('application__user__username', 'tx_ref')
    # CORRECTED: Replaced 'paystack_reference' with 'tx_ref'
    readonly_fields = ('created_at', 'updated_at', 'tx_ref')

