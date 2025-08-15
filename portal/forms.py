# portal/forms.py

from django import forms
from allauth.account.forms import SignupForm
from .models import Application, Document, Testimonial, UserProfile, WorkApplication, Country

class CustomSignupForm(SignupForm):
    """
    A custom signup form to override the default styling.
    The account_type field has been removed to prevent conflicts.
    """
    def __init__(self, *args, **kwargs):
        super(CustomSignupForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-green focus:border-primary-green sm:text-sm'})
            field.help_text = ''

class StudentApplicationForm(forms.ModelForm):
    passport_photograph_upload = forms.ImageField(required=False, label="Passport Photograph")
    international_passport_upload = forms.FileField(required=False, label="International Passport")
    school_certificate_upload = forms.FileField(required=False, label="WAEC or NECO Certificate")
    birth_certificate_upload = forms.FileField(required=False, label="Birth Certificate")

    class Meta:
        model = Application
        exclude = ['user', 'status', 'visa_status', 'passport_photograph']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'passport_issue_date': forms.DateInput(attrs={'type': 'date'}),
            'passport_expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'declaration_agreed': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-primary-green focus:ring-primary-green border-gray-300 rounded'}),
            'achievements': forms.Textarea(attrs={'rows': 3}),
            'medical_conditions': forms.Textarea(attrs={'rows': 3}),
            'allergies': forms.Textarea(attrs={'rows': 3}),
        }
    def __init__(self, *args, **kwargs):
        super(StudentApplicationForm, self).__init__(*args, **kwargs)
        base_classes = 'mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-green focus:border-primary-green sm:text-sm'
        for field_name, field in self.fields.items():
            if 'upload' not in field_name and not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': base_classes})

class WorkApplicationForm(forms.ModelForm):
    passport_photograph_upload = forms.ImageField(required=False, label="Passport Photograph")
    international_passport_upload = forms.FileField(required=False, label="International Passport Copy")
    educational_certificate_upload = forms.FileField(required=False, label="Educational Certificate (if any)")
    work_experience_upload = forms.FileField(required=False, label="Work Experience Letters")
    class Meta:
        model = WorkApplication
        exclude = ['user', 'status', 'visa_status', 'passport_photograph']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'passport_issue_date': forms.DateInput(attrs={'type': 'date'}),
            'passport_expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'declaration_agreed': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-primary-green focus:ring-primary-green border-gray-300 rounded'}),
            'previous_application_details': forms.Textarea(attrs={'rows': 3}),
            'skills_certifications': forms.Textarea(attrs={'rows': 3}),
        }
    def __init__(self, *args, **kwargs):
        super(WorkApplicationForm, self).__init__(*args, **kwargs)
        base_classes = 'mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-green focus:border-primary-green sm:text-sm'
        for field_name, field in self.fields.items():
            if 'upload' not in field_name and not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': base_classes})
        self.fields['destination_country'].queryset = Country.objects.all()
        self.fields['destination_country'].widget.attrs.update({'class': base_classes})

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary-green file:text-white hover:file:bg-dark-green'}),
        }

class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ['content', 'rating']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-green focus:border-primary-green sm:text-sm', 'rows': 4, 'placeholder': 'Share your experience with us...'}),
            'rating': forms.HiddenInput(),
        }
