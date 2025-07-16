from django.core.management.base import BaseCommand
from farmcom.models import CommunityNews
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create sample community news items'

    def handle(self, *args, **options):
        # Get the first superuser or create a default user
        try:
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                user = User.objects.first()
        except:
            user = None

        # Sample news items
        news_items = [
            {
                'title': 'FarmCom Launches New Dashboard!',
                'content': 'Monitor your progress and team with our new dashboards.',
                'is_active': True
            },
            {
                'title': 'Upcoming Community Event',
                'content': 'Join us for the annual FarmCom networking event this August.',
                'is_active': True
            },
            {
                'title': 'Tips for Sustainable Farming',
                'content': 'Check out our latest blog post on sustainable agriculture practices.',
                'is_active': True
            }
        ]

        created_count = 0
        for news_data in news_items:
            news, created = CommunityNews.objects.get_or_create(
                title=news_data['title'],
                defaults={
                    'content': news_data['content'],
                    'is_active': news_data['is_active'],
                    'created_by': user
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created news item: "{news.title}"')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'News item already exists: "{news.title}"')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} new news items')
        ) 