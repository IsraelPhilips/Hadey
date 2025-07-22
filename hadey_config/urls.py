# hadey_config/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Add this line to include all of Django's built-in authentication URLs
    # This will handle URLs like /accounts/login/, /accounts/logout/, etc.
    path('accounts/', include('django.contrib.auth.urls')),

    # This is our main app's URLs (including the dashboard)
    path('', include('portal.urls')),
]
