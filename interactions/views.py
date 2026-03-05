from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Comment, Like
from videos.models import Video
from .serializers import CommentSerializer

class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        video_id = self.kwargs['video_id']
        # Sirf parent comments (jinka parent null hai) dikhao, replies nested mein aayengi
        return Comment.objects.filter(video_id=video_id, parent=None).order_by('-created_at')
    
    def perform_create(self, serializer):
        video_id = self.kwargs['video_id']
        video = Video.objects.get(id=video_id)
        parent_id = self.request.data.get('parent')
        parent = Comment.objects.get(id=parent_id) if parent_id else None
        serializer.save(user=self.request.user, video=video, parent=parent)
        video.comments_count += 1
        video.save()

class LikeToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, video_id):
        try:
            video = Video.objects.get(id=video_id)
            like, created = Like.objects.get_or_create(
                user=request.user,
                video=video
            )
            
            if created:
                video.likes_count += 1
                video.save()
                return Response({
                    'liked': True,
                    'likes_count': video.likes_count
                }, status=status.HTTP_201_CREATED)
            else:
                like.delete()
                video.likes_count -= 1
                video.save()
                return Response({
                    'liked': False,
                    'likes_count': video.likes_count
                }, status=status.HTTP_200_OK)
                
        except Video.DoesNotExist:
            return Response({
                'error': 'Video not found'
            }, status=status.HTTP_404_NOT_FOUND)