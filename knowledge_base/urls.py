from django.urls import path
from . import views

app_name = 'knowledge_base'

urlpatterns = [
    # Article views
    path('', views.ArticleListView.as_view(), name='article_list'),
    path('article/<slug:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('article/new/', views.ArticleCreateView.as_view(), name='article_create'),
    path('article/<int:pk>/edit/', views.ArticleUpdateView.as_view(), name='article_update'),
    path('article/<int:pk>/delete/', views.ArticleDeleteView.as_view(), name='article_delete'),
    
    # Category and tag views
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('tag/<slug:slug>/', views.TagDetailView.as_view(), name='tag_detail'),
    
    # User interaction views
    path('article/<int:article_id>/like/', views.like_article, name='like_article'),
    path('article/<int:article_id>/bookmark/', views.bookmark_article, name='bookmark_article'),
    path('article/<int:article_id>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/reply/', views.add_reply, name='add_reply'),
    
    # User-specific views
    path('my-articles/', views.my_articles, name='my_articles'),
    path('my-bookmarks/', views.my_bookmarks, name='my_bookmarks'),
    
    # Search
    path('search/', views.search_articles, name='search_articles'),
] 