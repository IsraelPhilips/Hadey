# portal/admin.py

from django.contrib import admin
from .models import (
    Application, Document, Payment, VisaUpdate, Testimonial, 
    UserProfile, WorkApplication, Country
)
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group

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

# --- Inlines ---
class VisaUpdateInline(admin.TabularInline):
    model = VisaUpdate
    extra = 1
    readonly_fields = ('created_at',)
    fields = ('status_title', 'details', 'send_email_notification', 'created_at')
    exclude = ('work_application',)

class DocumentInline(admin.TabularInline):
    model = Document
    extra = 1
    readonly_fields = ('uploaded_at',)
    fields = ('document_type', 'file', 'is_admin_upload', 'uploaded_at')
    exclude = ('work_application',)

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ('amount', 'status', 'purpose', 'tx_ref', 'created_at')
    can_delete = False
    exclude = ('work_application',)
    def has_add_permission(self, request, obj=None): return False

# --- ModelAdmins ---
class ApplicationAdmin(admin.ModelAdmin): # Student Application Admin
    list_display = ('user', 'full_name', 'email', 'status', 'visa_status', 'updated_at')
    list_filter = ('status', 'visa_status', 'country_of_interest')
    search_fields = ('user__username', 'full_name', 'email')
    ordering = ('-updated_at',)
    inlines = [VisaUpdateInline, DocumentInline, PaymentInline]
    # Fieldsets would need to be updated with all the new student fields

class WorkApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'email', 'status', 'destination_country', 'updated_at')
    list_filter = ('status', 'destination_country')
    search_fields = ('user__username', 'full_name', 'email')
    ordering = ('-updated_at',)
    # Inlines for work application can be added here later

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
        return instance.profile.get_account_type_display()
    get_account_type.short_description = 'Account Type'

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'account_type')
    list_filter = ('account_type',)
    search_fields = ('user__username',)

# --- Registration ---
hadey_admin_site.register(Application, ApplicationAdmin)
hadey_admin_site.register(WorkApplication, WorkApplicationAdmin)
hadey_admin_site.register(Country, CountryAdmin)
hadey_admin_site.register(Testimonial)
hadey_admin_site.register(Document)
hadey_admin_site.register(Payment)
hadey_admin_site.register(UserProfile, UserProfileAdmin)

# Re-register User to our custom site, unregistering the base one first
admin.site.unregister(User)
hadey_admin_site.register(User, UserAdmin)
hadey_admin_site.register(Group)
