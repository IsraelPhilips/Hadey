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
    # ... unchanged ...
    class Meta:
        model = Application
        fields = ['full_name', 'email', 'phone_number', 'country_of_interest']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-green focus:border-primary-green sm:text-sm'}),
            'email': forms.EmailInput(attrs={'class': 'mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-green focus:border-primary-green sm:text-sm'}),
            'phone_number': forms.TextInput(attrs={'class': 'mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-green focus:border-primary-green sm:text-sm'}),
            'country_of_interest': forms.TextInput(attrs={'class': 'mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-green focus:border-primary-green sm:text-sm', 'placeholder': 'e.g., Poland, Hungary, etc.'}),
        }

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
