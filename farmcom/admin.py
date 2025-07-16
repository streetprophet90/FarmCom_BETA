from django.contrib import admin
from .models import CommunityNews

@admin.register(CommunityNews)
class CommunityNewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at', 'is_active', 'created_by')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('title', 'content')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_active',)
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change) 