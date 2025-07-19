from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.views import send_email_notification

User = get_user_model()

class Command(BaseCommand):
    help = 'Test email notifications for superusers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email address to send test notification to',
        )

    def handle(self, *args, **options):
        # Get all superusers
        superusers = User.objects.filter(is_superuser=True)
        
        if not superusers.exists():
            self.stdout.write(
                self.style.ERROR('No superusers found in the system.')
            )
            return
        
        # If specific email provided, find that superuser
        if options['email']:
            try:
                superuser = User.objects.get(email=options['email'], is_superuser=True)
                superusers = [superuser]
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'No superuser found with email: {options["email"]}')
                )
                return
        
        # Send test notification to each superuser
        for superuser in superusers:
            self.stdout.write(f'Sending test email to: {superuser.email}')
            
            success = send_email_notification(
                user=superuser,
                notification_type='SYSTEM_MAINTENANCE',
                title='Test Email Notification',
                message='This is a test email notification to verify that the email system is working correctly. If you receive this email, the notification system is functioning properly.'
            )
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Test email sent successfully to {superuser.email}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'✗ Failed to send test email to {superuser.email}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Email notification test completed!')
        ) 