from rest_framework import serializers
from .models import Comment, CommentLike

class CommentSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_profile_pic = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'user_username', 'user_profile_pic', 'video', 'parent', 'text', 'created_at', 
                  'replies', 'reply_count', 'likes_count', 'is_liked']
        read_only_fields = ['id', 'user', 'video', 'created_at']

    def get_user_profile_pic(self, obj):
        if hasattr(obj.user, 'profile') and obj.user.profile.profile_pic:
            return obj.user.profile.profile_pic
        return None

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True, context=self.context).data
        return []

    def get_reply_count(self, obj):
        return obj.replies.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False