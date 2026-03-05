from django.contrib import admin
from .models import Video

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'user', 'video_url', 'views_count', 'likes_count', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['title', 'description']
    readonly_fields = ['views_count', 'likes_count', 'comments_count', 'shares_count', 'created_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'title', 'description')
        }),
        ('Media', {
            'fields': ('video_url', 'thumbnail_url')
        }),
        ('Stats', {
            'fields': ('views_count', 'likes_count', 'comments_count', 'shares_count')
        }),
        ('Timing', {
            'fields': ('created_at',)
        }),
    )