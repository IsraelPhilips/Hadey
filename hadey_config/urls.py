# hadey_config/urls.py

from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# Import our custom admin site
from portal.admin import hadey_admin_site
# Import the custom view for the signup choice page
from portal.views import signup_choice_view

urlpatterns = [
    path('admin/', hadey_admin_site.urls),

    # NEW: A dedicated URL for the page where users choose their application type
    path('accounts/register/', signup_choice_view, name='account_signup_choice'),
    
    # This now correctly handles all of allauth's URLs, including the actual signup form
    path('accounts/', include('allauth.urls')),

    # This is our main app's URLs (including the dashboard)
    path('', include('portal.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # The static root is for production, STATICFILES_DIRS is for development
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
