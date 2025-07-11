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