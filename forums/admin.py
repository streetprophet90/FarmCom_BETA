from django.contrib import admin
from .models import Category, Topic, Post, PostLike, TopicSubscription, TopicRequest

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'get_topic_count', 'get_post_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'get_post_count', 'views', 'is_pinned', 'is_locked', 'created_at']
    list_filter = ['category', 'is_pinned', 'is_locked', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    list_editable = ['is_pinned', 'is_locked']
    ordering = ['-created_at']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['topic', 'author', 'is_solution', 'get_likes_count', 'created_at']
    list_filter = ['is_solution', 'created_at', 'topic__category']
    search_fields = ['content', 'author__username', 'topic__title']
    list_editable = ['is_solution']
    ordering = ['-created_at']

@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ['post', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['post__content', 'user__username']
    ordering = ['-created_at']

@admin.register(TopicSubscription)
class TopicSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['topic', 'user', 'created_at']
    list_filter = ['created_at', 'topic__category']
    search_fields = ['topic__title', 'user__username']
    ordering = ['-created_at']

@admin.register(TopicRequest)
class TopicRequestAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'category', 'status', 'created_at', 'days_old']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['title', 'description', 'user__username']
    list_editable = ['status']
    readonly_fields = ['created_at', 'days_old']
    actions = ['approve_requests', 'reject_requests']
    fieldsets = (
        ('Request Details', {
            'fields': ('user', 'category', 'title', 'description', 'reason')
        }),
        ('Admin Review', {
            'fields': ('status', 'admin_notes', 'reviewed_by', 'reviewed_at')
        }),
    )
    
    def days_old(self, obj):
        from django.utils import timezone
        delta = timezone.now().date() - obj.created_at.date()
        return f"{delta.days} days"
    days_old.short_description = 'Age'
    
    def approve_requests(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            status='APPROVED',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'{updated} topic request(s) were successfully approved.')
    approve_requests.short_description = "Approve selected topic requests"
    
    def reject_requests(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            status='REJECTED',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'{updated} topic request(s) were successfully rejected.')
    reject_requests.short_description = "Reject selected topic requests"
    
    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            obj.reviewed_by = request.user
            from django.utils import timezone
            obj.reviewed_at = timezone.now()
            
            # Send notification to the user who made the request
            from accounts.views import create_notification
            status_display = dict(TopicRequest.STATUS_CHOICES)[obj.status]
            
            if obj.status == 'APPROVED':
                notification_title = f"Topic Request Approved: {obj.title}"
                notification_message = f"Your topic request '{obj.title}' has been approved by {request.user.username}. The topic will be created soon."
                notification_type = 'TOPIC_REQUEST_APPROVED'
            elif obj.status == 'REJECTED':
                notification_title = f"Topic Request Rejected: {obj.title}"
                notification_message = f"Your topic request '{obj.title}' has been rejected by {request.user.username}. Reason: {obj.admin_notes or 'No reason provided'}"
                notification_type = 'TOPIC_REQUEST_REJECTED'
            else:
                notification_title = f"Topic Request Updated: {obj.title}"
                notification_message = f"Your topic request '{obj.title}' status has been updated to {status_display} by {request.user.username}."
                notification_type = 'TOPIC_REQUEST_UPDATED'
            
            create_notification(
                user=obj.user,
                title=notification_title,
                message=notification_message,
                notification_type=notification_type
            )
            
        super().save_model(request, obj, form, change)
