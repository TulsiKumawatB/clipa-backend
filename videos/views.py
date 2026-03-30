from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from .models import Video
from .serializers import VideoSerializer, VideoUploadSerializer
from shorts_backend.minio_client import MinioClient
from accounts.models import User
from notifications.models import Notification  # 👈 Import notification model

class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return VideoUploadSerializer
        return VideoSerializer
    
    def perform_create(self, serializer):
        video_file = self.request.FILES.get('video')
        if video_file:
            minio_client = MinioClient()
            video_url = minio_client.upload_video(video_file, video_file.name)
            thumbnail = self.request.FILES.get('thumbnail')
            thumbnail_url = None
            if thumbnail:
                thumbnail_url = minio_client.upload_thumbnail(thumbnail, thumbnail.name)
            serializer.save(
                user=self.request.user,
                video_url=video_url,
                thumbnail_url=thumbnail_url
            )
        else:
            raise serializers.ValidationError({"video": "Video file is required"})
    
    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("You can only delete your own videos")
        instance.delete()
    
    @action(detail=False, methods=['get'])
    def feed(self, request):
        videos = Video.objects.all().order_by('-created_at')[:20]
        serializer = self.get_serializer(videos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        video = self.get_object()
        video.likes_count += 1
        video.save()
        return Response({'likes_count': video.likes_count})
    
    @action(detail=True, methods=['post'])
    def view(self, request, pk=None):
        video = self.get_object()
        video.views_count += 1
        video.save()
        return Response({'views_count': video.views_count})
    
    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        video = self.get_object()
        video.shares_count += 1
        video.save()
        
        # 👇 Create notification for share (if not sharing own video)
        if video.user != request.user:
            Notification.objects.create(
                recipient=video.user,
                sender=request.user,
                notification_type='share',
                video=video
            )
        
        return Response({'shares_count': video.shares_count})
    
    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)')
    def user_videos(self, request, user_id=None):
        try:
            user = User.objects.get(id=user_id)
            videos = Video.objects.filter(user=user).order_by('-created_at')
            page = self.paginate_queryset(videos)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(videos, many=True)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)
        
    @action(detail=False, methods=['get'], url_path='search')
    def search_videos(self, request):
        """Search videos by title or description"""
        query = request.query_params.get('q', '')
        if len(query) < 2:
            return Response([])
        
        videos = Video.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        ).order_by('-created_at')[:20]
        
        serializer = self.get_serializer(videos, many=True)
        return Response(serializer.data)