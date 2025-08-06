from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import EventCategory, Event, EventRegistration, EventComment, EventLike, EventView, EventReminder

@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'color', 'order', 'is_active', 'event_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    list_editable = ['order', 'is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']

    def event_count(self, obj):
        return obj.events.count()
    event_count.short_description = 'Events'

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'organizer', 'category', 'event_type', 'start_date', 'end_date', 'status', 'featured', 'current_participants', 'max_participants', 'is_free', 'views']
    list_filter = ['status', 'event_type', 'category', 'access_level', 'is_free', 'featured', 'start_date', 'created_at']
    list_editable = ['status', 'featured']
    search_fields = ['title', 'description', 'organizer__username', 'venue_name', 'city']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views', 'current_participants', 'registrations_count', 'created_at', 'updated_at']
    filter_horizontal = []
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'short_description', 'event_type', 'category', 'access_level')
        }),
        ('Location', {
            'fields': ('venue_name', 'address', 'city', 'region', 'coordinates')
        }),
        ('Timing', {
            'fields': ('start_date', 'start_time', 'end_date', 'end_time', 'registration_deadline')
        }),
        ('Capacity & Registration', {
            'fields': ('max_participants', 'current_participants', 'is_registration_required')
        }),
        ('Pricing', {
            'fields': ('is_free', 'price', 'currency')
        }),
        ('Organizer', {
            'fields': ('organizer', 'contact_email', 'contact_phone', 'website')
        }),
        ('Content', {
            'fields': ('featured_image', 'additional_images', 'attachments'),
            'classes': ('collapse',)
        }),
        ('Status & Metadata', {
            'fields': ('status', 'featured', 'meta_title', 'meta_description')
        }),
        ('Statistics', {
            'fields': ('views', 'registrations_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('organizer', 'category')

    def save_model(self, request, obj, form, change):
        if not change:  # New event
            obj.organizer = request.user
        super().save_model(request, obj, form, change)

    actions = ['publish_events', 'unpublish_events', 'feature_events', 'unfeature_events', 'cancel_events']

    def publish_events(self, request, queryset):
        updated = queryset.update(status='PUBLISHED')
        self.message_user(request, f'{updated} events were successfully published.')
    publish_events.short_description = "Publish selected events"

    def unpublish_events(self, request, queryset):
        updated = queryset.update(status='DRAFT')
        self.message_user(request, f'{updated} events were successfully unpublished.')
    unpublish_events.short_description = "Unpublish selected events"

    def feature_events(self, request, queryset):
        updated = queryset.update(featured=True)
        self.message_user(request, f'{updated} events were successfully featured.')
    feature_events.short_description = "Feature selected events"

    def unfeature_events(self, request, queryset):
        updated = queryset.update(featured=False)
        self.message_user(request, f'{updated} events were successfully unfeatured.')
    unfeature_events.short_description = "Unfeature selected events"

    def cancel_events(self, request, queryset):
        updated = queryset.update(status='CANCELLED')
        self.message_user(request, f'{updated} events were successfully cancelled.')
    cancel_events.short_description = "Cancel selected events"

class EventRegistrationInline(admin.TabularInline):
    model = EventRegistration
    extra = 0
    readonly_fields = ['user', 'registration_date', 'status']
    fields = ['user', 'status', 'attended', 'payment_status', 'registration_date']

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'status', 'registration_date', 'attended', 'payment_status', 'payment_amount']
    list_filter = ['status', 'attended', 'payment_status', 'registration_date', 'event__category']
    list_editable = ['status', 'attended', 'payment_status']
    search_fields = ['event__title', 'user__username', 'emergency_contact']
    readonly_fields = ['event', 'user', 'registration_date', 'created_at', 'updated_at']
    ordering = ['-registration_date']

    fieldsets = (
        ('Registration Details', {
            'fields': ('event', 'user', 'status', 'registration_date', 'attended', 'attendance_date')
        }),
        ('Additional Information', {
            'fields': ('dietary_restrictions', 'special_requirements', 'emergency_contact', 'emergency_phone')
        }),
        ('Payment', {
            'fields': ('payment_status', 'payment_amount', 'payment_date')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['confirm_registrations', 'mark_attended', 'mark_no_show', 'process_payments']

    def confirm_registrations(self, request, queryset):
        updated = queryset.update(status='CONFIRMED')
        self.message_user(request, f'{updated} registrations were successfully confirmed.')
    confirm_registrations.short_description = "Confirm selected registrations"

    def mark_attended(self, request, queryset):
        updated = queryset.update(status='ATTENDED', attended=True)
        self.message_user(request, f'{updated} registrations were marked as attended.')
    mark_attended.short_description = "Mark as attended"

    def mark_no_show(self, request, queryset):
        updated = queryset.update(status='NO_SHOW')
        self.message_user(request, f'{updated} registrations were marked as no show.')
    mark_no_show.short_description = "Mark as no show"

    def process_payments(self, request, queryset):
        updated = queryset.update(payment_status='PAID')
        self.message_user(request, f'{updated} payments were processed.')
    process_payments.short_description = "Process payments"

@admin.register(EventComment)
class EventCommentAdmin(admin.ModelAdmin):
    list_display = ['event', 'author', 'content_preview', 'is_approved', 'is_reply', 'created_at']
    list_filter = ['is_approved', 'created_at', 'event__category']
    list_editable = ['is_approved']
    search_fields = ['content', 'author__username', 'event__title']
    readonly_fields = ['event', 'author', 'parent', 'created_at', 'updated_at']
    ordering = ['-created_at']

    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'

    def is_reply(self, obj):
        return obj.parent is not None
    is_reply.boolean = True
    is_reply.short_description = 'Is Reply'

    actions = ['approve_comments', 'disapprove_comments']

    def approve_comments(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} comments were successfully approved.')
    approve_comments.short_description = "Approve selected comments"

    def disapprove_comments(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} comments were successfully disapproved.')
    disapprove_comments.short_description = "Disapprove selected comments"

@admin.register(EventLike)
class EventLikeAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'created_at']
    list_filter = ['created_at', 'event__category']
    search_fields = ['event__title', 'user__username']
    readonly_fields = ['event', 'user', 'created_at']
    ordering = ['-created_at']

@admin.register(EventView)
class EventViewAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'ip_address', 'created_at']
    list_filter = ['created_at', 'event__category']
    search_fields = ['event__title', 'user__username', 'ip_address']
    readonly_fields = ['event', 'user', 'ip_address', 'user_agent', 'created_at']
    ordering = ['-created_at']

@admin.register(EventReminder)
class EventReminderAdmin(admin.ModelAdmin):
    list_display = ['registration', 'reminder_type', 'scheduled_time', 'status', 'sent_at']
    list_filter = ['status', 'reminder_type', 'scheduled_time', 'created_at']
    search_fields = ['registration__event__title', 'registration__user__username']
    readonly_fields = ['registration', 'reminder_type', 'scheduled_time', 'status', 'sent_at', 'created_at']
    ordering = ['scheduled_time']

    actions = ['mark_sent', 'mark_failed']

    def mark_sent(self, request, queryset):
        updated = queryset.update(status='SENT')
        self.message_user(request, f'{updated} reminders were marked as sent.')
    mark_sent.short_description = "Mark as sent"

    def mark_failed(self, request, queryset):
        updated = queryset.update(status='FAILED')
        self.message_user(request, f'{updated} reminders were marked as failed.')
    mark_failed.short_description = "Mark as failed"
