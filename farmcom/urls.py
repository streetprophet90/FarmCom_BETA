"""
URL configuration for farmco project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib.auth import logout
from django.shortcuts import redirect, render
from . import views
from accounts.views import custom_login, contact_support

def custom_logout(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('home')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('lands/', include('lands.urls')),
    path('farming/', include('farming.urls')),
    path('marketplace/', include('marketplace.urls')),
    path('forums/', include('forums.urls')),
    path('permissions/', include('user_permissions.urls')),
    path('login/', custom_login, name='login'),
    path('logout/', custom_logout, name='logout'),  # Add logout URL at root level
    path('contact/', contact_support, name='contact_support'),
    path('home/', views.logged_in_home, name='logged_in_home'),
    path('', views.home, name='home'),
    
    # FarmCom app URLs
    path('farmcom/', include('farmcom.app_urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
