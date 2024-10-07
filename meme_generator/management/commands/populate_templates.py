from django.core.management.base import BaseCommand
from meme_generator.models import MemeTemplate

class Command(BaseCommand):
    help = 'Populate MemeTemplates with initial data'

    def handle(self, *args, **kwargs):
        # Add initial meme templates
        MemeTemplate.objects.get_or_create(
            name='Template 1',
            image_url='https://example.com/template1.png',
            default_top_text='Default Top Text 1',
            default_bottom_text='Default Bottom Text 1'
        )
        MemeTemplate.objects.get_or_create(
            name='Template 2',
            image_url='https://example.com/template2.png',
            default_top_text='Default Top Text 2',
            default_bottom_text='Default Bottom Text 2'
        )
        self.stdout.write(self.style.SUCCESS('Successfully populated meme templates.'))
