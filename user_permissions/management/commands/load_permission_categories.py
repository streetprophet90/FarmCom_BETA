from django.core.management.base import BaseCommand
from user_permissions.models import PermissionCategory

class Command(BaseCommand):
    help = 'Load default permission categories'

    def handle(self, *args, **options):
        categories = [
            {
                'name': 'Forum Management',
                'description': 'Permissions related to managing forum topics, posts, and categories'
            },
            {
                'name': 'User Management',
                'description': 'Permissions for managing user accounts, profiles, and user types'
            },
            {
                'name': 'Content Moderation',
                'description': 'Permissions for moderating content, approving/rejecting submissions'
            },
            {
                'name': 'Land Management',
                'description': 'Permissions for managing land listings and approvals'
            },
            {
                'name': 'Project Management',
                'description': 'Permissions for managing farming projects and approvals'
            },
            {
                'name': 'Analytics Access',
                'description': 'Permissions for accessing system analytics and reports'
            },
            {
                'name': 'Notification Management',
                'description': 'Permissions for managing system notifications and alerts'
            },
            {
                'name': 'Report Management',
                'description': 'Permissions for managing user reports and complaints'
            },
        ]

        created_count = 0
        for category_data in categories:
            category, created = PermissionCategory.objects.get_or_create(
                name=category_data['name'],
                defaults={
                    'description': category_data['description'],
                    'is_active': True
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created permission category: {category.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Permission category already exists: {category.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully loaded {created_count} new permission categories')
        ) 