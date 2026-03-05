from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Video
from .serializers import VideoSerializer, VideoUploadSerializer
from shorts_backend.minio_client import MinioClient

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
        # Get video file from request
        video_file = self.request.FILES.get('video')
        
        if video_file:
            # Upload to MiniO
            minio_client = MinioClient()
            video_url = minio_client.upload_video(video_file, video_file.name)
            
            # Optional thumbnail
            thumbnail = self.request.FILES.get('thumbnail')
            thumbnail_url = None
            if thumbnail:
                thumbnail_url = minio_client.upload_thumbnail(thumbnail, thumbnail.name)
            
            # Save to database
            serializer.save(
                user=self.request.user,
                video_url=video_url,
                thumbnail_url=thumbnail_url
            )
        else:
            # Agar video file nahi hai toh error return karo
            raise serializers.ValidationError({"video": "Video file is required"})
    
    @action(detail=False, methods=['get'])
    def feed(self, request):
        """Get video feed (paginated)"""
        videos = Video.objects.all().order_by('-created_at')[:20]
        serializer = self.get_serializer(videos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Like a video"""
        video = self.get_object()
        video.likes_count += 1
        video.save()
        return Response({'likes_count': video.likes_count})
    
    @action(detail=True, methods=['post'])
    def view(self, request, pk=None):
        """Increment view count"""
        video = self.get_object()
        video.views_count += 1
        video.save()
        return Response({'views_count': video.views_count})