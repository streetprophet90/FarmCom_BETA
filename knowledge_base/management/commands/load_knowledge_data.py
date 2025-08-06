from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from knowledge_base.models import Category, Tag, Article
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Load sample knowledge base data including categories, tags, and articles'

    def handle(self, *args, **options):
        self.stdout.write('Loading knowledge base sample data...')
        
        # Create categories
        categories_data = [
            {
                'name': 'Crop Farming',
                'description': 'Articles about growing various crops in Ghana',
                'icon': 'fas fa-seedling',
                'color': 'success',
                'order': 1
            },
            {
                'name': 'Livestock',
                'description': 'Animal husbandry and livestock management',
                'icon': 'fas fa-cow',
                'color': 'primary',
                'order': 2
            },
            {
                'name': 'Soil Management',
                'description': 'Soil health, fertility, and conservation',
                'icon': 'fas fa-mountain',
                'color': 'warning',
                'order': 3
            },
            {
                'name': 'Pest Control',
                'description': 'Managing pests and diseases in farming',
                'icon': 'fas fa-bug',
                'color': 'danger',
                'order': 4
            },
            {
                'name': 'Irrigation',
                'description': 'Water management and irrigation systems',
                'icon': 'fas fa-tint',
                'color': 'info',
                'order': 5
            },
            {
                'name': 'Marketing',
                'description': 'Selling produce and market strategies',
                'icon': 'fas fa-chart-line',
                'color': 'secondary',
                'order': 6
            }
        ]
        
        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            categories[cat_data['name']] = category
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Create tags
        tags_data = [
            {'name': 'Cocoa', 'color': 'success'},
            {'name': 'Maize', 'color': 'warning'},
            {'name': 'Rice', 'color': 'primary'},
            {'name': 'Cassava', 'color': 'secondary'},
            {'name': 'Organic', 'color': 'success'},
            {'name': 'Pesticides', 'color': 'danger'},
            {'name': 'Drip Irrigation', 'color': 'info'},
            {'name': 'Market', 'color': 'secondary'},
            {'name': 'Export', 'color': 'dark'},
            {'name': 'Youth Farming', 'color': 'primary'},
        ]
        
        tags = {}
        for tag_data in tags_data:
            tag, created = Tag.objects.get_or_create(
                name=tag_data['name'],
                defaults=tag_data
            )
            tags[tag_data['name']] = tag
            if created:
                self.stdout.write(f'Created tag: {tag.name}')
        
        # Get or create a superuser for articles
        try:
            author = User.objects.filter(is_superuser=True).first()
            if not author:
                author = User.objects.create_superuser(
                    username='admin',
                    email='admin@farmcom.com',
                    password='admin123'
                )
        except:
            author = User.objects.first()
        
        # Create sample articles
        articles_data = [
            {
                'title': 'Growing Cocoa in Ghana: A Complete Guide',
                'excerpt': 'Learn the essential techniques for successful cocoa farming in Ghana, from planting to harvesting.',
                'content': 'This comprehensive guide covers everything you need to know about cocoa farming in Ghana, including climate requirements, soil preparation, planting techniques, maintenance, pest control, harvesting, and marketing strategies.',
                'category': categories['Crop Farming'],
                'tags': [tags['Cocoa'], tags['Organic'], tags['Export']],
                'difficulty': 'INTERMEDIATE',
                'featured': True,
                'status': 'PUBLISHED',
                'published_at': timezone.now() - timedelta(days=5)
            },
            {
                'title': 'Modern Irrigation Techniques for Small-Scale Farmers',
                'excerpt': 'Discover cost-effective irrigation methods that can improve your crop yields and water efficiency.',
                'content': 'This guide explores modern irrigation techniques suitable for small-scale farmers in Ghana, including drip irrigation, sprinkler systems, and water management strategies.',
                'category': categories['Irrigation'],
                'tags': [tags['Drip Irrigation'], tags['Organic']],
                'difficulty': 'INTERMEDIATE',
                'featured': True,
                'status': 'PUBLISHED',
                'published_at': timezone.now() - timedelta(days=3)
            },
            {
                'title': 'Organic Pest Control Methods for Ghanaian Farmers',
                'excerpt': 'Learn natural and organic methods to control pests without harmful chemicals.',
                'content': 'This guide provides practical organic pest control techniques suitable for Ghanaian farming conditions, including biological control, botanical pesticides, and cultural methods.',
                'category': categories['Pest Control'],
                'tags': [tags['Organic'], tags['Pesticides']],
                'difficulty': 'BEGINNER',
                'featured': False,
                'status': 'PUBLISHED',
                'published_at': timezone.now() - timedelta(days=1)
            },
            {
                'title': 'Marketing Your Farm Produce: A Guide for Ghanaian Farmers',
                'excerpt': 'Learn effective marketing strategies to get the best prices for your agricultural products.',
                'content': 'This comprehensive guide covers market research, quality standards, pricing strategies, marketing channels, branding, and customer relationship management for Ghanaian farmers.',
                'category': categories['Marketing'],
                'tags': [tags['Market'], tags['Export'], tags['Youth Farming']],
                'difficulty': 'BEGINNER',
                'featured': False,
                'status': 'PUBLISHED',
                'published_at': timezone.now() - timedelta(hours=12)
            }
        ]
        
        for article_data in articles_data:
            # Create article
            article = Article.objects.create(
                title=article_data['title'],
                excerpt=article_data['excerpt'],
                content=article_data['content'],
                category=article_data['category'],
                difficulty=article_data['difficulty'],
                featured=article_data['featured'],
                status=article_data['status'],
                published_at=article_data['published_at'],
                author=author
            )
            
            # Add tags
            article.tags.set(article_data['tags'])
            
            self.stdout.write(f'Created article: {article.title}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully loaded knowledge base data:\n'
                f'- {len(categories)} categories\n'
                f'- {len(tags)} tags\n'
                f'- {len(articles_data)} articles'
            )
        ) 