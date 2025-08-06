from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class EventCategory(models.Model):
    """Categories for organizing events"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome icon class")
    color = models.CharField(max_length=20, default="primary", help_text="Bootstrap color class")
    order = models.IntegerField(default=0, help_text="Display order")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Event Categories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('events:category_detail', kwargs={'slug': self.slug})

class Event(models.Model):
    """Events for the community calendar"""
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PUBLISHED', 'Published'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    ]
    
    TYPE_CHOICES = [
        ('WORKSHOP', 'Workshop'),
        ('SEMINAR', 'Seminar'),
        ('TRAINING', 'Training'),
        ('MEETUP', 'Community Meetup'),
        ('CONFERENCE', 'Conference'),
        ('EXHIBITION', 'Exhibition'),
        ('COMPETITION', 'Competition'),
        ('OTHER', 'Other'),
    ]
    
    ACCESS_CHOICES = [
        ('PUBLIC', 'Public'),
        ('REGISTERED', 'Registered Users Only'),
        ('INVITE_ONLY', 'Invite Only'),
        ('PAID', 'Paid Event'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    short_description = models.TextField(blank=True, help_text="Brief description for listings")
    
    # Event Details
    event_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='WORKSHOP')
    category = models.ForeignKey(EventCategory, on_delete=models.CASCADE, related_name='events')
    access_level = models.CharField(max_length=20, choices=ACCESS_CHOICES, default='PUBLIC')
    
    # Location
    venue_name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    coordinates = models.CharField(max_length=50, blank=True, help_text="Latitude,Longitude")
    
    # Timing
    start_date = models.DateField()
    start_time = models.TimeField()
    end_date = models.DateField()
    end_time = models.TimeField()
    
    # Capacity and Registration
    max_participants = models.PositiveIntegerField(null=True, blank=True)
    current_participants = models.PositiveIntegerField(default=0)
    registration_deadline = models.DateTimeField(null=True, blank=True)
    is_registration_required = models.BooleanField(default=True)
    
    # Pricing
    is_free = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='GHS')
    
    # Organizer
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    
    # Content
    featured_image = models.ImageField(upload_to='events/images/', blank=True)
    additional_images = models.JSONField(default=list, blank=True)
    attachments = models.JSONField(default=list, blank=True)
    
    # Status and Metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    featured = models.BooleanField(default=False, help_text="Featured events appear prominently")
    
    # Statistics
    views = models.PositiveIntegerField(default=0)
    registrations_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-start_date', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.status == 'PUBLISHED' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('events:event_detail', kwargs={'slug': self.slug})

    def is_upcoming(self):
        """Check if event is in the future"""
        now = timezone.now()
        event_start = timezone.make_aware(
            timezone.datetime.combine(self.start_date, self.start_time)
        )
        return event_start > now

    def is_ongoing(self):
        """Check if event is currently happening"""
        now = timezone.now()
        event_start = timezone.make_aware(
            timezone.datetime.combine(self.start_date, self.start_time)
        )
        event_end = timezone.make_aware(
            timezone.datetime.combine(self.end_date, self.end_time)
        )
        return event_start <= now <= event_end

    def is_past(self):
        """Check if event has ended"""
        now = timezone.now()
        event_end = timezone.make_aware(
            timezone.datetime.combine(self.end_date, self.end_time)
        )
        return event_end < now

    def is_full(self):
        """Check if event is at capacity"""
        if self.max_participants is None:
            return False
        return self.current_participants >= self.max_participants

    def can_register(self):
        """Check if registration is still open"""
        if not self.is_registration_required:
            return True
        if self.is_full():
            return False
        if self.registration_deadline and timezone.now() > self.registration_deadline:
            return False
        return self.status == 'PUBLISHED' and self.is_upcoming()

    def increment_views(self):
        """Increment view count"""
        self.views += 1
        self.save(update_fields=['views'])

class EventRegistration(models.Model):
    """Track event registrations"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('ATTENDED', 'Attended'),
        ('NO_SHOW', 'No Show'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Registration Details
    registration_date = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False)
    attendance_date = models.DateTimeField(null=True, blank=True)
    
    # Additional Information
    dietary_restrictions = models.TextField(blank=True)
    special_requirements = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    emergency_phone = models.CharField(max_length=20, blank=True)
    
    # Payment
    payment_status = models.CharField(max_length=20, default='PENDING', choices=[
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('REFUNDED', 'Refunded'),
    ])
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['event', 'user']
        ordering = ['-registration_date']

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"

    def save(self, *args, **kwargs):
        # Update event participant count
        if self.pk is None:  # New registration
            self.event.current_participants += 1
            self.event.save(update_fields=['current_participants'])
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Decrease event participant count
        self.event.current_participants = max(0, self.event.current_participants - 1)
        self.event.save(update_fields=['current_participants'])
        super().delete(*args, **kwargs)

class EventComment(models.Model):
    """Comments on events"""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    content = models.TextField()
    is_approved = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.event.title}"

    def is_reply(self):
        """Check if this comment is a reply to another comment"""
        return self.parent is not None

class EventLike(models.Model):
    """Track event likes by users"""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='user_likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_events')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['event', 'user']

    def __str__(self):
        return f"{self.user.username} likes {self.event.title}"

class EventView(models.Model):
    """Track event views by users"""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='user_views')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='viewed_events', null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['event', 'user', 'ip_address']

    def __str__(self):
        return f"View of {self.event.title} by {self.user.username if self.user else 'Anonymous'}"

class EventReminder(models.Model):
    """Event reminders for registered users"""
    REMINDER_CHOICES = [
        ('1_HOUR', '1 Hour Before'),
        ('1_DAY', '1 Day Before'),
        ('1_WEEK', '1 Week Before'),
        ('1_MONTH', '1 Month Before'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('FAILED', 'Failed'),
    ]

    registration = models.ForeignKey(EventRegistration, on_delete=models.CASCADE, related_name='reminders')
    reminder_type = models.CharField(max_length=20, choices=REMINDER_CHOICES)
    scheduled_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['registration', 'reminder_type']
        ordering = ['scheduled_time']

    def __str__(self):
        return f"Reminder for {self.registration.event.title} - {self.reminder_type}"
