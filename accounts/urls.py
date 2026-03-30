from django.urls import path
from .views import (
    RegisterView, CustomTokenObtainPairView, ProfileDetailView,
    follow_user, unfollow_user, user_followers, user_following,
    search_users 
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/<str:username>/', ProfileDetailView.as_view(), name='profile-detail'),
    path('follow/<str:username>/', follow_user, name='follow-user'),
    path('unfollow/<str:username>/', unfollow_user, name='unfollow-user'),
    path('followers/<str:username>/', user_followers, name='user-followers'),
    path('following/<str:username>/', user_following, name='user-following'),
    path('search/', search_users, name='search-users'),  
]