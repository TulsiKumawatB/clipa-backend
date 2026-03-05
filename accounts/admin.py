from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    """
    Custom User Admin with extra fields
    """
    list_display = ('id', 'username', 'email', 'bio', 'created_at')
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

# Register the custom user model
admin.site.register(User, CustomUserAdmin)