# Generated by Django 5.2.4 on 2025-07-09 09:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        ('farming', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CropListing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price_per_unit', models.DecimalField(decimal_places=2, max_digits=10)),
                ('available_quantity', models.DecimalField(decimal_places=2, max_digits=10)),
                ('is_organic', models.BooleanField(default=False)),
                ('harvest_date', models.DateField()),
                ('listing_date', models.DateTimeField(auto_now_add=True)),
                ('project', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='farming.farmingproject')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=12)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('PAID', 'Paid'), ('DELIVERED', 'Delivered'), ('CANCELLED', 'Cancelled')], default='PENDING', max_length=20)),
                ('order_date', models.DateTimeField(auto_now_add=True)),
                ('delivery_address', models.TextField()),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.user')),
                ('listing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='marketplace.croplisting')),
            ],
        ),
    ]
