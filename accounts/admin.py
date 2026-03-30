from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile

class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'bio', 'followers_count', 'following_count', 'created_at')
    list_filter = ('is_staff', 'is_active', 'created_at')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email', 'bio', 'profile_pic')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'bio', 'profile_pic'),
        }),
    )
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)

    def followers_count(self, obj):
        return obj.followers.count()
    followers_count.short_description = 'Followers'

    def following_count(self, obj):
        return obj.following.count()
    following_count.short_description = 'Following'


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'bio', 'followers_count', 'following_count', 'created_at')
    search_fields = ('user__username', 'bio')
    list_filter = ('created_at',)

    def followers_count(self, obj):
        return obj.user.followers.count()
    followers_count.short_description = 'Followers'

    def following_count(self, obj):
        return obj.user.following.count()
    following_count.short_description = 'Following'

admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)