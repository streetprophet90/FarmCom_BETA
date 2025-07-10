from django.urls import path
from . import views

urlpatterns = [
    path('revenue-shares/', views.revenue_share_list, name='revenue_share_list'),
    # Add more URL patterns as needed
] 