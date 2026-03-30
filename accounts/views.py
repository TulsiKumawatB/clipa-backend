from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.db.models import Q
from notifications.models import Notification  # 👈 Notification model import

from .serializers import (
    UserSerializer, RegisterSerializer, 
    CustomTokenObtainPairSerializer, ProfileSerializer
)
from .models import Profile
from shorts_backend.minio_client import MinioClient

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user).data,
            "message": "User created successfully",
        })

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom login view that returns user data along with tokens
    """
    serializer_class = CustomTokenObtainPairSerializer


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        username = self.kwargs['username']
        user = get_object_or_404(User, username=username)
        profile, created = Profile.objects.get_or_create(user=user)
        return profile

    def perform_update(self, serializer):
        # Sirf profile owner hi update kar sakta hai
        if self.request.user.username != self.kwargs['username']:
            raise PermissionDenied("You can only edit your own profile")
        
        # Check if profile_pic file is in request
        if 'profile_pic' in self.request.FILES:
            image_file = self.request.FILES['profile_pic']
            minio_client = MinioClient()
            image_url = minio_client.upload_profile_pic(image_file, image_file.name)
            # Save the profile with the new image URL
            serializer.save(profile_pic=image_url)
        else:
            serializer.save()


# ============= FOLLOW/UNFOLLOW VIEWS =============

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def follow_user(request, username):
    """Follow a user"""
    try:
        user_to_follow = User.objects.get(username=username)
        if request.user == user_to_follow:
            return Response({'error': 'You cannot follow yourself'}, status=status.HTTP_400_BAD_REQUEST)
        
        request.user.following.add(user_to_follow)
        
        # 👇 Create notification for follow
        Notification.objects.create(
            recipient=user_to_follow,
            sender=request.user,
            notification_type='follow'
        )
        
        return Response({
            'message': f'You are now following {username}',
            'following': True
        }, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def unfollow_user(request, username):
    """Unfollow a user"""
    try:
        user_to_unfollow = User.objects.get(username=username)
        request.user.following.remove(user_to_unfollow)
        return Response({
            'message': f'You have unfollowed {username}',
            'following': False
        }, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def user_followers(request, username):
    """Get user's followers"""
    try:
        user = User.objects.get(username=username)
        followers = user.followers.all()
        data = [{'id': u.id, 'username': u.username, 'profile_pic': u.profile.profile_pic if hasattr(u, 'profile') else None} for u in followers]
        return Response(data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def user_following(request, username):
    """Get users that a user is following"""
    try:
        user = User.objects.get(username=username)
        following = user.following.all()
        data = [{'id': u.id, 'username': u.username, 'profile_pic': u.profile.profile_pic if hasattr(u, 'profile') else None} for u in following]
        return Response(data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


# ============= SEARCH VIEW =============

@api_view(['GET'])
@permission_classes([AllowAny])
def search_users(request):
    """Search users by username or email"""
    query = request.query_params.get('q', '')
    if len(query) < 2:
        return Response([])

    users = User.objects.filter(
        Q(username__icontains=query) |
        Q(email__icontains=query)
    )[:20]  # Limit to 20 results

    results = []
    for user in users:
        profile_pic = user.profile.profile_pic if hasattr(user, 'profile') else None
        results.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'profile_pic': profile_pic,
            'followers_count': user.followers.count(),
        })

    return Response(results)