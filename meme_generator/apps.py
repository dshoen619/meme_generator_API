from django.apps import AppConfig


class MemeAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'meme_generator'

    def ready(self):
        from django.core.management import call_command
        call_command('populate_templates')
