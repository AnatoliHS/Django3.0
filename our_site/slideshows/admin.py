from django.contrib import admin
from .models import SlideshowProgress

@admin.register(SlideshowProgress)
class SlideshowProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'slideshow_slug', 'current_h', 'current_v', 'max_percentage', 'completed', 'last_updated')
    list_filter = ('slideshow_slug', 'completed')
    search_fields = ('user__username', 'slideshow_slug')
