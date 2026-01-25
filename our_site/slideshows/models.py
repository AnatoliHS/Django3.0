from django.db import models
from django.contrib.auth.models import User

class SlideshowProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    slideshow_slug = models.CharField(max_length=255)
    current_h = models.IntegerField(default=0)
    current_v = models.IntegerField(default=0)
    max_percentage = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'slideshow_slug')
        verbose_name_plural = "Slideshow Progress"

    def __str__(self):
        return f"{self.user.username} - {self.slideshow_slug} ({self.max_percentage}%)"
