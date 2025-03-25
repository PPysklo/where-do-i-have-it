from django.apps import AppConfig


class AppThingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_thing'
    verbose_name = 'Thing'

    def ready(self):
        from . import signals