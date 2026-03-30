from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError
from .models import Comment, Like, CommentLike
from videos.models import Video
from .serializers import CommentSerializer
from notifications.models import Notification  # 👈 Import notification model

class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        video_id = self.kwargs['video_id']
        return Comment.objects.filter(video_id=video_id, parent=None).order_by('-created_at')
    
    def perform_create(self, serializer):
        video_id = self.kwargs['video_id']
        video = Video.objects.get(id=video_id)
        parent_id = self.request.data.get('parent')
        parent = Comment.objects.get(id=parent_id) if parent_id else None

        # 👇 SIRF VIDEO OWNER KE LIYE CHECK (duplicate comment prevention)
        if self.request.user == video.user and parent is None:
            existing = Comment.objects.filter(
                user=self.request.user,
                video=video,
                parent=None
            ).exists()
            if existing:
                raise ValidationError("You can only comment once on your own video")

        try:
            comment = serializer.save(user=self.request.user, video=video, parent=parent)
            video.comments_count += 1
            video.save()

            # 👇 Create notification for comment (only top-level comments, and not if commenting on own video)
            if parent is None and video.user != self.request.user:
                Notification.objects.create(
                    recipient=video.user,
                    sender=self.request.user,
                    notification_type='comment',
                    video=video,
                    comment=comment
                )

        except IntegrityError:
            raise ValidationError("Comment failed")

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

                # 👇 Create notification for like (if not liking own video)
                if video.user != request.user:
                    Notification.objects.create(
                        recipient=video.user,
                        sender=request.user,
                        notification_type='like',
                        video=video
                    )

                return Response({'liked': True, 'likes_count': video.likes_count})
            else:
                like.delete()
                video.likes_count -= 1
                video.save()
                return Response({'liked': False, 'likes_count': video.likes_count})
        except Video.DoesNotExist:
            return Response({'error': 'Video not found'}, status=404)

class CommentLikeToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, comment_id):
        try:
            comment = Comment.objects.get(id=comment_id)
            like, created = CommentLike.objects.get_or_create(
                user=request.user,
                comment=comment
            )
            if created:
                return Response({'liked': True, 'likes_count': comment.likes.count()})
            else:
                like.delete()
                return Response({'liked': False, 'likes_count': comment.likes.count()})
        except Comment.DoesNotExist:
            return Response({'error': 'Comment not found'}, status=404)

class CommentDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        try:
            comment = self.get_object()
            video = comment.video
            comment.delete()
            video.comments_count -= 1
            video.save()
            return Response({'message': 'Comment deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Comment.DoesNotExist:
            return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)