from rest_framework import serializers
from .models import Video
from accounts.models import User

class VideoSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    is_liked = serializers.SerializerMethodField()
    user_profile_pic = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = [
            'id', 'user', 'user_username', 'user_profile_pic', 'title', 'description',
            'video_url', 'thumbnail_url', 'views_count', 
            'likes_count', 'comments_count', 'shares_count', 'created_at',
            'is_liked'
        ]
        read_only_fields = ['id', 'user', 'views_count', 'likes_count', 
                           'comments_count', 'shares_count', 'created_at', 'video_url', 'thumbnail_url']

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def get_user_profile_pic(self, obj):
        if hasattr(obj.user, 'profile') and obj.user.profile.profile_pic:
            return obj.user.profile.profile_pic
        return None


class VideoUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['title', 'description']