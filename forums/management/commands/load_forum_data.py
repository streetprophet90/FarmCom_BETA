from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

from forums.models import Category, Topic, Post

User = get_user_model()

class Command(BaseCommand):
    help = 'Load sample forum data for FarmCom'

    def handle(self, *args, **options):
        self.stdout.write('Loading sample forum data...')
        
        # Create forum categories
        categories = self.create_categories()
        
        # Create sample topics and posts
        self.create_sample_topics_and_posts(categories)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully loaded sample forum data!')
        )

    def create_categories(self):
        """Create forum categories"""
        categories_data = [
            {
                'name': 'Farming Techniques',
                'slug': 'farming-techniques',
                'description': 'Share and discuss various farming methods, best practices, and innovative techniques.'
            },
            {
                'name': 'Crop Management',
                'slug': 'crop-management',
                'description': 'Discussions about crop selection, planting, maintenance, and harvesting strategies.'
            },
            {
                'name': 'Market Trends',
                'slug': 'market-trends',
                'description': 'Stay updated with agricultural market prices, trends, and business opportunities.'
            },
            {
                'name': 'Equipment & Tools',
                'slug': 'equipment-tools',
                'description': 'Share information about farming equipment, tools, and machinery.'
            },
            {
                'name': 'Pest & Disease Control',
                'slug': 'pest-disease-control',
                'description': 'Discuss pest management, disease prevention, and treatment methods.'
            },
            {
                'name': 'Soil & Fertilizer',
                'slug': 'soil-fertilizer',
                'description': 'Learn about soil health, fertilization, and soil improvement techniques.'
            },
            {
                'name': 'Success Stories',
                'slug': 'success-stories',
                'description': 'Share your farming success stories and learn from others\' experiences.'
            },
            {
                'name': 'General Discussion',
                'slug': 'general-discussion',
                'description': 'General agricultural discussions and community chat.'
            }
        ]
        
        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        return categories

    def create_sample_topics_and_posts(self, categories):
        """Create sample topics and posts"""
        users = list(User.objects.all())
        if not users:
            self.stdout.write(self.style.WARNING('No users found. Please create users first.'))
            return
        
        topics_data = [
            {
                'title': 'Best practices for organic farming in Ghana',
                'content': 'I\'m interested in starting organic farming in the Ashanti region. What are the best practices for organic farming in Ghana? I\'m particularly interested in soil preparation and natural pest control methods.',
                'category_slug': 'farming-techniques'
            },
            {
                'title': 'Cocoa farming tips for beginners',
                'content': 'I\'m a new farmer looking to start cocoa farming. What are the essential things I need to know? From land preparation to harvesting, any advice would be greatly appreciated.',
                'category_slug': 'crop-management'
            },
            {
                'title': 'Current market prices for cassava',
                'content': 'What are the current market prices for cassava in different regions? I\'m planning to harvest next month and want to know the best markets to target.',
                'category_slug': 'market-trends'
            },
            {
                'title': 'Recommended tractors for small-scale farming',
                'content': 'I\'m looking to purchase a tractor for my 5-acre farm. What brands and models would you recommend for small-scale farming in Ghana?',
                'category_slug': 'equipment-tools'
            },
            {
                'title': 'Natural ways to control tomato pests',
                'content': 'My tomato plants are being attacked by pests. What are some effective natural methods to control them without using chemical pesticides?',
                'category_slug': 'pest-disease-control'
            },
            {
                'title': 'Improving soil fertility naturally',
                'content': 'My soil seems to be losing fertility. What are some natural ways to improve soil health and fertility? I prefer organic methods.',
                'category_slug': 'soil-fertilizer'
            },
            {
                'title': 'My successful maize farming story',
                'content': 'I want to share my experience with maize farming this season. I achieved a 30% increase in yield compared to last year. Here\'s what I did differently...',
                'category_slug': 'success-stories'
            },
            {
                'title': 'Weather patterns affecting farming this season',
                'content': 'Has anyone noticed unusual weather patterns this farming season? How is it affecting your crops? Let\'s discuss and share strategies.',
                'category_slug': 'general-discussion'
            }
        ]
        
        for topic_data in topics_data:
            category = next((cat for cat in categories if cat.slug == topic_data['category_slug']), categories[0])
            author = random.choice(users)
            
            topic = Topic.objects.create(
                category=category,
                title=topic_data['title'],
                content=topic_data['content'],
                author=author,
                created_at=timezone.now() - timedelta(days=random.randint(1, 30))
            )
            
            # Create some sample replies
            self.create_sample_posts(topic, users)
            
            self.stdout.write(f'Created topic: {topic.title}')
    
    def create_sample_posts(self, topic, users):
        """Create sample posts for a topic"""
        sample_replies = [
            'Great question! I\'ve been farming for 10 years and here\'s what I\'ve learned...',
            'I agree with the previous response. Additionally, you should consider...',
            'Thanks for sharing this information. It\'s very helpful for beginners like me.',
            'I have a different approach that has worked well for me...',
            'This is exactly what I needed to know. Thank you for the detailed explanation!',
            'I\'ve been facing similar issues. Let me share my experience...',
            'Excellent advice! I\'ll definitely try this method on my farm.',
            'I have a question about this approach. What about...',
            'This is very informative. I\'ve learned something new today.',
            'I\'ve been using this technique for years and it works wonders!'
        ]
        
        # Create 2-5 random replies
        num_replies = random.randint(2, 5)
        for i in range(num_replies):
            author = random.choice(users)
            if author != topic.author:  # Don't let topic author reply to their own topic
                Post.objects.create(
                    topic=topic,
                    author=author,
                    content=sample_replies[i % len(sample_replies)],
                    created_at=topic.created_at + timedelta(hours=random.randint(1, 48))
                ) 