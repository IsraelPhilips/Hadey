# hadey_config/urls.py

from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# Import our custom admin site
from portal.admin import hadey_admin_site

urlpatterns = [
    # Use our custom admin site's URLs
    path('admin/', hadey_admin_site.urls),

    path('accounts/', include('allauth.urls')),
    path('', include('portal.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

