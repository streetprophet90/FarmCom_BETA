from django.db import models
from django.contrib.auth.models import AbstractUser,Group, Permission


class User(AbstractUser):
    USER_TYPES = (
        ('LANDOWNER', 'Landowner'),
        ('FARMER', 'Professional Farmer'),
        ('WORKER', 'Farm Worker'),
        ('INVESTOR', 'Investor'),
        ('STUDENT', 'Student'),
    )

    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    phone = models.CharField(max_length=20)
    location = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    skills = models.CharField(max_length=200, blank=True)

    # Add these to resolve the clashes
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="accounts_user_groups",  # Custom related_name
        related_query_name="accounts_user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="accounts_user_permissions",  # Custom related_name
        related_query_name="accounts_user",
    )

    def __str__(self):
        return f"{self.get_user_type_display()}: {self.username}"

    # New: supervisor relationship for WORKERs (points to a FARMER)
    supervisor = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='supervised_workers',
        limit_choices_to={'user_type': 'FARMER'},
        help_text='The professional farmer supervising this worker (if applicable).'
    )

# New: ActivityLog model
class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=100)
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    confirmed = models.BooleanField(default=False)  # New: confirmation by farmer

    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

# New: ImageUpload model
class ImageUpload(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='image_uploads')
    image = models.ImageField(upload_to='user_uploads/')
    description = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.image.name} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

class Recommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    content = models.TextField()
    project = models.ForeignKey('farming.FarmingProject', on_delete=models.CASCADE, null=True, blank=True, related_name='recommendations')
    land = models.ForeignKey('lands.Land', on_delete=models.CASCADE, null=True, blank=True, related_name='recommendations')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        target = self.project or self.land
        return f"{self.user.username} on {target}: {self.content[:30]}..."

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('LAND_PENDING', 'Land Pending Approval'),
        ('PROJECT_PENDING', 'Project Pending Approval'),
        ('LAND_APPROVED', 'Land Approved'),
        ('LAND_REJECTED', 'Land Rejected'),
        ('PROJECT_APPROVED', 'Project Approved'),
        ('PROJECT_REJECTED', 'Project Rejected'),
        ('NEW_USER', 'New User Registration'),
        ('NEW_RECOMMENDATION', 'New Recommendation'),
        ('ACTIVITY_CONFIRMED', 'Activity Confirmed'),
        ('ACTIVITY_DISAPPROVED', 'Activity Disapproved'),
        ('NEW_ACTIVITY', 'New Activity Logged'),
        ('NEW_UPLOAD', 'New Image Upload'),
        ('PROJECT_UPDATE', 'Project Status Update'),
        ('TEAM_MESSAGE', 'Team Message'),
        ('TASK_ASSIGNED', 'Task Assigned'),
        ('TASK_COMPLETED', 'Task Completed'),
        ('WEATHER_ALERT', 'Weather Alert'),
        ('EQUIPMENT_ISSUE', 'Equipment Issue'),
        ('MARKETPLACE_ORDER', 'Marketplace Order'),
        ('PAYMENT_RECEIVED', 'Payment Received'),
        ('SYSTEM_MAINTENANCE', 'System Maintenance'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    related_object_id = models.IntegerField(null=True, blank=True)
    related_object_type = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notification_type} - {self.title}"

    def mark_as_read(self):
        self.is_read = True
        self.save()

class AdminAuditLog(models.Model):
    ACTION_TYPES = [
        ('APPROVE_LAND', 'Approve Land'),
        ('REJECT_LAND', 'Reject Land'),
        ('APPROVE_PROJECT', 'Approve Project'),
        ('REJECT_PROJECT', 'Reject Project'),
        ('DELETE_LAND', 'Delete Land'),
        ('DELETE_PROJECT', 'Delete Project'),
        ('DELETE_USER', 'Delete User'),
        ('DELETE_LISTING', 'Delete Listing'),
        ('DELETE_RECOMMENDATION', 'Delete Recommendation'),
        ('EDIT_LAND', 'Edit Land'),
        ('EDIT_PROJECT', 'Edit Project'),
        ('BULK_APPROVE_LANDS', 'Bulk Approve Lands'),
        ('BULK_REJECT_LANDS', 'Bulk Reject Lands'),
        ('BULK_APPROVE_PROJECTS', 'Bulk Approve Projects'),
        ('BULK_REJECT_PROJECTS', 'Bulk Reject Projects'),
    ]

    admin_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_actions')
    action_type = models.CharField(max_length=30, choices=ACTION_TYPES)
    target_object_type = models.CharField(max_length=50)
    target_object_id = models.IntegerField()
    target_object_name = models.CharField(max_length=200)
    details = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.admin_user.username} - {self.action_type} - {self.target_object_name}"