# portal/forms.py

from django import forms
from .models import Application

class ApplicationForm(forms.ModelForm):
    """
    A form for users to fill out their application details.
    """
    class Meta:
        model = Application
        # Specify the fields from the model to include in the form
        fields = ['full_name', 'email', 'phone_number', 'country_of_interest']

        # Add widgets to style the form fields with Tailwind CSS classes
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-green focus:border-primary-green sm:text-sm'}),
            'email': forms.EmailInput(attrs={'class': 'mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-green focus:border-primary-green sm:text-sm'}),
            'phone_number': forms.TextInput(attrs={'class': 'mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-green focus:border-primary-green sm:text-sm'}),
            'country_of_interest': forms.TextInput(attrs={'class': 'mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-green focus:border-primary-green sm:text-sm', 'placeholder': 'e.g., Poland, Hungary, etc.'}),
        }
