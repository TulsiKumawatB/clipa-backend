from rest_framework import serializers
from .models import User, Profile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserSerializer(serializers.ModelSerializer):
    followers_count = serializers.IntegerField(source='followers.count', read_only=True)
    following_count = serializers.IntegerField(source='following.count', read_only=True)
    videos_count = serializers.IntegerField(source='videos.count', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'bio', 'profile_pic',
            'followers_count', 'following_count', 'videos_count',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
        }
        return data


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    followers_count = serializers.IntegerField(source='user.followers.count', read_only=True)   # 👈 correct source
    following_count = serializers.IntegerField(source='user.following.count', read_only=True)   # 👈 correct source
    videos_count = serializers.IntegerField(source='user.videos.count', read_only=True)
    profile_pic = serializers.URLField(read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'user_id', 'username', 'email', 'bio', 'profile_pic', 
                  'followers_count', 'following_count', 'videos_count', 'created_at']
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'bio': {'required': False, 'allow_blank': True},
        }