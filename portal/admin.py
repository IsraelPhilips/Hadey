# portal/admin.py

from django.contrib import admin
from .models import Application, Document, Payment

# Register your models here.

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
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'email', 'status', 'country_of_interest', 'updated_at')
    list_filter = ('status', 'country_of_interest')
    search_fields = ('user__username', 'full_name', 'email')
    ordering = ('-updated_at',)
    fieldsets = (
        ('Applicant Information', {'fields': ('user', 'full_name', 'email', 'phone_number')}),
        ('Application Details', {'fields': ('status', 'country_of_interest')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ('created_at', 'updated_at')
    inlines = [DocumentInline, PaymentInline]


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('application', 'document_type', 'is_admin_upload', 'uploaded_at')
    list_filter = ('document_type', 'is_admin_upload', 'application')
    search_fields = ('application__user__username', 'application__full_name')
    readonly_fields = ('uploaded_at',)
    # The incorrect save_model method has been removed.


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('application', 'purpose', 'amount', 'status', 'tx_ref', 'updated_at')
    list_filter = ('status', 'purpose')
    search_fields = ('application__user__username', 'tx_ref')
    readonly_fields = ('created_at', 'updated_at', 'tx_ref')
