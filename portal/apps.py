# portal/apps.py

from django.apps import AppConfig

class PortalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'portal'

    def ready(self):
        # This line is crucial. It imports our signals module
        # so that the signal handlers are registered.
        import portal.signals