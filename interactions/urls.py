from django.urls import path
from .views import CommentListCreateView, LikeToggleView, CommentLikeToggleView, CommentDeleteView

urlpatterns = [
    path('videos/<int:video_id>/comments/', CommentListCreateView.as_view(), name='video-comments'),
    path('videos/<int:video_id>/like/', LikeToggleView.as_view(), name='video-like'),
    path('comments/<int:comment_id>/like/', CommentLikeToggleView.as_view(), name='comment-like'),
    path('comments/<int:pk>/delete/', CommentDeleteView.as_view(), name='comment-delete'),
]