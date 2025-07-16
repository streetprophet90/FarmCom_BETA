from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ActivityLog, ImageUpload, Testimonial, BlogPost

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Profile', {'fields': ('phone', 'location', 'bio', 'skills', 'avatar')}),
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

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('user__username', 'content')
    actions = ['approve_testimonials']

    def approve_testimonials(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} testimonial(s) approved.")
    approve_testimonials.short_description = 'Approve selected testimonials'

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_approved', 'is_published', 'created_at')
    list_filter = ('is_approved', 'is_published', 'created_at')
    search_fields = ('title', 'author__username')
    actions = ['approve_posts', 'publish_posts', 'unpublish_posts']

    def approve_posts(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} post(s) approved.")
    approve_posts.short_description = 'Approve selected posts'

    def publish_posts(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(request, f"{updated} post(s) published.")
    publish_posts.short_description = 'Publish selected posts'

    def unpublish_posts(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f"{updated} post(s) unpublished.")
    unpublish_posts.short_description = 'Unpublish selected posts'
