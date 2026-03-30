from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/videos/', include('videos.urls')),
    path('api/interactions/', include('interactions.urls')),
    path('api/notifications/', include('notifications.urls')),  # 👈 YEH LINE ADD KARO
]