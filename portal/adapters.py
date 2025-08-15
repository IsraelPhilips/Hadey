# portal/adapters.py

from allauth.account.adapter import DefaultAccountAdapter
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
        
        return user
