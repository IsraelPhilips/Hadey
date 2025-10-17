# portal/adapters.py

from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import UserProfile

class CustomAccountAdapter(DefaultAccountAdapter):

    def save_user(self, request, user, form, commit=True):
        """
        This is called when a user signs up. We override it to create a
        UserProfile object.
        """
        # First, let the default save_user run to create the user
        user = super().save_user(request, user, form, commit=False)
        
        # CORRECTED: Get the account type directly from the request's POST data
        account_type = request.POST.get('account_type')
        
        if commit:
            user.save()
            # Create the UserProfile if the account_type was provided
            if account_type:
                UserProfile.objects.create(user=user, account_type=account_type)

            send_mail(
                f'New User Signup: {user.email}',
                f"""Hello Admin,

                A new user has successfully signed up on the Hadey Travels Global portal.

                --- User Details ---
                Email: {user.email}
                Account Type: {account_type}
                --------------------

                You can manage this user from the admin dashboard.

                Regards,
                The Hadey Travels Global System""",
                settings.DEFAULT_FROM_EMAIL,
                ['hadeytravelsglobal@gmail.com']
            )
        
        return user
