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
    
    @property
    def videos_count(self):
        return self.videos.count()
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    profile_pic = models.URLField(blank=True, null=True)  # MiniO URL store karega
    followers = models.ManyToManyField(User, related_name='following_profiles', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    @property
    def followers_count(self):
        return self.followers.count()

    @property
    def following_count(self):
        return self.user.following.count()

    @property
    def videos_count(self):
        return self.user.videos.count()