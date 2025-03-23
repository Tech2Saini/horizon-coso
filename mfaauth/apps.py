from django.apps import AppConfig


class MfaauthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mfaauth'

    def ready(self):
        import mfaauth.signals  # Ensure signals are loaded
