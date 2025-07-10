from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import random

from lands.models import Land
from farming.models import FarmingProject
from marketplace.models import CropListing, Order
from payments.models import RevenueShare

User = get_user_model()

class Command(BaseCommand):
    help = 'Load sample data for FarmCom'

    def handle(self, *args, **options):
        self.stdout.write('Loading sample data...')
        
        # Create sample users
        users = self.create_sample_users()
        
        # Create sample lands
        lands = self.create_sample_lands(users)
        
        # Create sample farming projects
        projects = self.create_sample_projects(lands, users)
        
        # Create sample marketplace listings
        listings = self.create_sample_listings(projects)
        
        # Create sample orders
        self.create_sample_orders(listings, users)
        
        # Create sample revenue shares
        self.create_sample_revenue_shares(projects)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully loaded sample data!')
        )

    def create_sample_users(self):
        users = []
        
        # Create different types of users
        user_data = [
            ('kwame_landowner', 'kwame@example.com', 'LANDOWNER', 'Kwame Asante', '+233-24-123-4567', 'Kumasi, Ashanti Region', 'Experienced landowner with 500+ acres'),
            ('akua_farmer', 'akua@example.com', 'FARMER', 'Akua Mensah', '+233-20-234-5678', 'Tamale, Northern Region', 'Professional farmer with 15 years experience'),
            ('kofi_worker', 'kofi@example.com', 'WORKER', 'Kofi Addo', '+233-26-345-6789', 'Sunyani, Bono Region', 'Skilled farm worker specializing in organic farming'),
            ('efua_investor', 'efua@example.com', 'INVESTOR', 'Efua Osei', '+233-27-456-7890', 'Accra, Greater Accra Region', 'Agricultural investor looking for sustainable projects'),
            ('yaw_student', 'yaw@example.com', 'STUDENT', 'Yaw Boateng', '+233-54-567-8901', 'Cape Coast, Central Region', 'Agricultural student learning modern farming techniques'),
        ]
        
        for username, email, user_type, full_name, phone, location, bio in user_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'user_type': user_type,
                    'first_name': full_name.split()[0],
                    'last_name': full_name.split()[1],
                    'phone': phone,
                    'location': location,
                    'bio': bio,
                    'skills': 'Organic farming, Crop rotation, Sustainable agriculture',
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'Created user: {username}')
            users.append(user)
        
        return users

    def create_sample_lands(self, users):
        lands = []
        
        land_data = [
            ('Kumasi Cocoa Farm', 'Kumasi, Ashanti Region', 150.5, 'Fertile farmland with excellent drainage for cocoa cultivation', 'Cocoa, Plantain, Cassava', 'Loam', 'Well water'),
            ('Tamale Rice Fields', 'Tamale, Northern Region', 200.0, 'Irrigated fields perfect for rice and maize cultivation', 'Rice, Maize, Groundnuts', 'Clay loam', 'River access'),
            ('Sunyani Palm Plantation', 'Sunyani, Bono Region', 300.0, 'Large plantation with oil palm and food crops', 'Oil Palm, Cassava, Yam', 'Silt loam', 'Pond and well'),
            ('Cape Coast Vegetable Farm', 'Cape Coast, Central Region', 75.0, 'Small family farm with organic certification', 'Tomatoes, Peppers, Garden Eggs', 'Sandy loam', 'Rainwater collection'),
            ('Accra Pineapple Estate', 'Accra, Greater Accra Region', 500.0, 'Premium agricultural land with modern infrastructure', 'Pineapple, Mango, Papaya', 'Rich loam', 'Irrigation system'),
        ]
        
        for title, location, size, description, preferred_crops, soil_type, water_source in land_data:
            land, created = Land.objects.get_or_create(
                title=title,
                defaults={
                    'owner': random.choice([u for u in users if u.user_type == 'LANDOWNER']),
                    'location': location,
                    'size': size,
                    'description': description,
                    'preferred_crops': preferred_crops,
                    'soil_type': soil_type,
                    'water_source': water_source,
                    'is_available': True,
                }
            )
            if created:
                self.stdout.write(f'Created land: {title}')
            lands.append(land)
        
        return lands

    def create_sample_projects(self, lands, users):
        projects = []
        
        project_data = [
            ('Cocoa Harvest 2024', 'ACTIVE', 'Cocoa', 15000.0, 16000.0),
            ('Organic Vegetable Garden', 'ACTIVE', 'Tomatoes, Peppers, Garden Eggs', 5000.0, None),
            ('Rice Cultivation Project', 'PLANNING', 'Rice', 8000.0, None),
            ('Maize Harvest Season', 'HARVESTED', 'Maize', 12000.0, 11500.0),
            ('Mixed Crop Farm', 'ACTIVE', 'Cassava, Yam, Plantain', 20000.0, None),
        ]
        
        for i, (crops, status, crop_types, estimated_yield, actual_yield) in enumerate(project_data):
            project, created = FarmingProject.objects.get_or_create(
                land=lands[i % len(lands)],
                crops=crop_types,
                defaults={
                    'manager': random.choice([u for u in users if u.user_type == 'FARMER']),
                    'start_date': date.today() - timedelta(days=random.randint(30, 180)),
                    'end_date': date.today() + timedelta(days=random.randint(30, 90)) if status != 'HARVESTED' else date.today() - timedelta(days=random.randint(1, 30)),
                    'status': status,
                    'estimated_yield': estimated_yield,
                    'actual_yield': actual_yield,
                }
            )
            if created:
                # Add workers
                workers = [u for u in users if u.user_type in ['WORKER', 'STUDENT']]
                project.workers.set(random.sample(workers, min(2, len(workers))))
                self.stdout.write(f'Created project: {crops}')
            projects.append(project)
        
        return projects

    def create_sample_listings(self, projects):
        listings = []
        
        for project in projects:
            if project.status == 'HARVESTED' and project.actual_yield:
                listing, created = CropListing.objects.get_or_create(
                    project=project,
                    defaults={
                        'price_per_unit': Decimal(random.uniform(2.0, 8.0)).quantize(Decimal('0.01')),
                        'available_quantity': Decimal(str(project.actual_yield)) * Decimal('0.8'),  # 80% available for sale
                        'is_organic': random.choice([True, False]),
                        'harvest_date': project.end_date or date.today(),
                    }
                )
                if created:
                    self.stdout.write(f'Created listing: {project.crops}')
                listings.append(listing)
        
        return listings

    def create_sample_orders(self, listings, users):
        buyers = [u for u in users if u.user_type in ['INVESTOR', 'FARMER']]
        
        for listing in listings:
            if random.choice([True, False]):  # 50% chance of having orders
                order, created = Order.objects.get_or_create(
                    listing=listing,
                    buyer=random.choice(buyers),
                    defaults={
                        'quantity': listing.available_quantity * Decimal(str(random.uniform(0.1, 0.5))),
                        'status': random.choice(['PENDING', 'PAID', 'DELIVERED']),
                        'delivery_address': f'{random.choice(buyers).location}',
                    }
                )
                if created:
                    self.stdout.write(f'Created order for {listing.project.crops}')

    def create_sample_revenue_shares(self, projects):
        for project in projects:
            if project.status == 'HARVESTED' and project.actual_yield:
                revenue_share, created = RevenueShare.objects.get_or_create(
                    project=project,
                    defaults={
                        'landowner_share': Decimal('30.0'),
                        'workers_share': Decimal('25.0'),
                        'manager_share': Decimal('20.0'),
                        'investor_share': Decimal('15.0'),
                        'platform_share': Decimal('10.0'),
                        'total_amount': Decimal(str(project.actual_yield)) * Decimal(str(random.uniform(3.0, 6.0))),
                    }
                )
                if created:
                    self.stdout.write(f'Created revenue share for {project.crops}') 