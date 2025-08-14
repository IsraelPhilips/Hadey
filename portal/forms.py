# portal/forms.py

from django import forms
from allauth.account.forms import SignupForm
from .models import Application, Document, Testimonial # Add Testimonial

class CustomSignupForm(SignupForm):
    # ... unchanged ...
    def __init__(self, *args, **kwargs):
        super(CustomSignupForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-green focus:border-primary-green sm:text-sm'})
            field.help_text = ''

class ApplicationForm(forms.ModelForm):
    """
    A comprehensive form for the entire Step 1 application.
    """
    passport_photograph_upload = forms.ImageField(required=True, label="Passport Photograph")
    international_passport_upload = forms.FileField(required=True, label="International Passport")
    school_certificate_upload = forms.FileField(required=True, label="WAEC or NECO Certificate")
    birth_certificate_upload = forms.FileField(required=True, label="Birth Certificate")

    class Meta:
        model = Application
        fields = [
            # Personal Info
            'full_name', 'date_of_birth', 'place_of_birth', 'gender', 'nationality', 
            'address', 'city', 'postal_code', 'phone_number', 'email',
            # Parent/Guardian Info
            'father_name', 'father_occupation', 'father_contact', 'mother_name', 
            'mother_occupation', 'mother_contact', 'guardian_name', 
            'guardian_relationship', 'guardian_contact',
            # Academic Info
            'grade_level', 'preferred_program', 'previous_school', 
            'country_applying_from', 'country_of_interest', 'achievements',
            # Emergency Contact
            'emergency_contact_name', 'emergency_contact_relationship', 'emergency_contact_number',
            # Medical Info
            'medical_conditions', 'allergies',
            # Additional Info
            'how_did_you_hear', 'declaration_agreed'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'declaration_agreed': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-primary-green focus:ring-primary-green border-gray-300 rounded'}),
            'achievements': forms.Textarea(attrs={'rows': 3}),
            'medical_conditions': forms.Textarea(attrs={'rows': 3}),
            'allergies': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super(ApplicationForm, self).__init__(*args, **kwargs)
        # Apply Tailwind classes to all fields
        text_based_inputs = ['text', 'email', 'date', 'password', 'number']
        for field_name, field in self.fields.items():
            # CORRECTED: Check if the widget has 'input_type' before accessing it
            if hasattr(field.widget, 'input_type') and field.widget.input_type in text_based_inputs:
                field.widget.attrs.update({
                    'class': 'mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-green focus:border-primary-green sm:text-sm'
                })
            elif isinstance(field.widget, forms.Textarea):
                 field.widget.attrs.update({
                    'class': 'mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-green focus:border-primary-green sm:text-sm'
                })


class DocumentUploadForm(forms.ModelForm):
    # ... unchanged ...
    class Meta:
        model = Document
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary-green file:text-white hover:file:bg-dark-green'}),
        }

class TestimonialForm(forms.ModelForm):
    """
    A form for users to submit their testimonials.
    """
    class Meta:
        model = Testimonial
        fields = ['content', 'rating']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-green focus:border-primary-green sm:text-sm',
                'rows': 4,
                'placeholder': 'Share your experience with us...'
            }),
            'rating': forms.HiddenInput(), # We will use a custom star rating widget
        }
