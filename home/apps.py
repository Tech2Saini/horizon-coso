from django.contrib import admin
from django.apps import AppConfig


class HomeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'home'

    def ready(self):
        # Customizing Django Admin Branding
        admin.site.site_header = "Horizon Administration"
        admin.site.site_title = "Horizon Admin Portal"
        admin.site.index_title = "Welcome to Horizon Dashboard"
