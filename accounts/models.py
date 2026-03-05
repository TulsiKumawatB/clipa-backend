from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom User Model - Extra fields ke saath
    """
    bio = models.TextField(max_length=500, blank=True)
    profile_pic = models.URLField(blank=True, null=True)  # MiniO URL store karega
    followers = models.ManyToManyField(
        'self', 
        symmetrical=False, 
        related_name='following',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.username
    
    @property
    def followers_count(self):
        return self.followers.count()
    
    @property
    def following_count(self):
        return self.following.count()
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'