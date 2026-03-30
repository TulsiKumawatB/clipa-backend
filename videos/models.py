from django.db import models
from accounts.models import User

class Video(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    video_url = models.URLField()
    thumbnail_url = models.URLField(blank=True, null=True)
    views_count = models.IntegerField(default=0)
    likes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    shares_count = models.IntegerField(default=0)   # 👈 Ensure this line exists
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']