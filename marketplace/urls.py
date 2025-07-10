from django.urls import path
from . import views

urlpatterns = [
    path('listings/', views.listing_list, name='listing_list'),
    path('orders/', views.order_list, name='order_list'),
    # Add more URL patterns as needed
] 