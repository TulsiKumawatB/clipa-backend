from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Notification
from .serializers import NotificationSerializer

class NotificationListView(generics.ListAPIView):
    """
    Get user's notifications (latest first)
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).order_by('-created_at')[:50]  # Last 50 notifications

class NotificationMarkReadView(APIView):
    """
    Mark a single notification as read
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        try:
            notification = Notification.objects.get(
                id=pk, 
                recipient=request.user
            )
            notification.is_read = True
            notification.save()
            return Response({'status': 'marked read'})
        except Notification.DoesNotExist:
            return Response(
                {'error': 'Notification not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

class NotificationMarkAllReadView(APIView):
    """
    Mark all notifications as read for the current user
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        Notification.objects.filter(
            recipient=request.user, 
            is_read=False
        ).update(is_read=True)
        return Response({'status': 'all marked read'})