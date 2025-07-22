# portal/forms.py

from django import forms
from .models import Application, Document # Add Document to imports

class ApplicationForm(forms.ModelForm):
    """
    A form for users to fill out their application details.
    """
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
    """
    A form for students to upload their filled documents.
    """
    class Meta:
        model = Document
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary-green file:text-white hover:file:bg-dark-green'}),
        }
