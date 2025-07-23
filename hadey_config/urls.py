# hadey_config/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # This includes all the necessary allauth URLs
    # for login, logout, signup, password reset, etc.
    path('accounts/', include('allauth.urls')),

    # This is our main app's URLs (including the dashboard)
    path('', include('portal.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
