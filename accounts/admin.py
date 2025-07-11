from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ActivityLog, ImageUpload

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'phone', 'location', 'bio', 'skills', 'supervisor'),
        }),
    )
    list_display = UserAdmin.list_display + ('user_type', 'phone', 'location', 'supervisor')
    search_fields = UserAdmin.search_fields + ('user_type', 'phone', 'location')

admin.site.register(User, CustomUserAdmin)

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp')
    search_fields = ('user__username', 'action', 'details')
    list_filter = ('action', 'timestamp')

@admin.register(ImageUpload)
class ImageUploadAdmin(admin.ModelAdmin):
    list_display = ('user', 'image', 'description', 'timestamp')
    search_fields = ('user__username', 'description')
    list_filter = ('timestamp',)
