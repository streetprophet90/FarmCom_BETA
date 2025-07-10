from django.urls import path
from . import views

urlpatterns = [
    path('', views.LandListView.as_view(), name='land_list'),
    path('add/', views.AddLandView.as_view(), name='add_land'),
    path('<int:pk>/', views.land_detail, name='land_detail'),
    # Add more URL patterns as needed
]