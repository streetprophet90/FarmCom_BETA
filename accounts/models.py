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