from django.urls import path
from .views import CommentListCreateView, LikeToggleView

urlpatterns = [
    path('videos/<int:video_id>/comments/', CommentListCreateView.as_view(), name='video-comments'),
    path('videos/<int:video_id>/like/', LikeToggleView.as_view(), name='video-like'),
]