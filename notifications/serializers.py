from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    sender_profile_pic = serializers.SerializerMethodField()
    video_title = serializers.CharField(source='video.title', read_only=True, default='')
    
    class Meta:
        model = Notification
        fields = [
            'id', 'sender_username', 'sender_profile_pic', 
            'notification_type', 'video_title', 'is_read', 'created_at'
        ]
    
    def get_sender_profile_pic(self, obj):
        if hasattr(obj.sender, 'profile') and obj.sender.profile.profile_pic:
            return obj.sender.profile.profile_pic
        return None