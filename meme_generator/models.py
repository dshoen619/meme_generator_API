from django.db import models
from django.contrib.auth.models import User

class MemeTemplate(models.Model):
    name = models.CharField(max_length=100)
    image_url = models.URLField()
    default_top_text = models.CharField(max_length=100, blank=True)
    default_bottom_text = models.CharField(max_length=100, blank=True)

class Meme(models.Model):
    template = models.ForeignKey(MemeTemplate, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meme_generator_memes')  # Add related_name here
    top_text = models.CharField(max_length=255, blank=True)
    bottom_text = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Rating(models.Model):
    meme = models.ForeignKey(Meme, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meme_generator_ratings')  # Add related_name here
    score = models.IntegerField()
    rated_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('meme', 'user')
