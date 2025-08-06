from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Category, Tag, Article, Comment, ArticleLike, ArticleView, Bookmark

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'color', 'order', 'is_active', 'article_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    list_editable = ['order', 'is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']

    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = 'Articles'

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color', 'article_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']

    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = 'Articles'

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ['author', 'created_at']
    fields = ['author', 'content', 'is_approved', 'created_at']

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'difficulty', 'featured', 'views', 'likes', 'published_at', 'created_at']
    list_filter = ['status', 'difficulty', 'featured', 'category', 'tags', 'created_at', 'published_at']
    list_editable = ['status', 'featured']
    search_fields = ['title', 'content', 'excerpt', 'author__username', 'category__name']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views', 'likes', 'shares', 'created_at', 'updated_at']
    filter_horizontal = ['tags']
    inlines = [CommentInline]
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'content', 'excerpt')
        }),
        ('Metadata', {
            'fields': ('author', 'category', 'tags', 'status', 'difficulty', 'featured')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('views', 'likes', 'shares'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'category').prefetch_related('tags')

    def save_model(self, request, obj, form, change):
        if not change:  # New article
            obj.author = request.user
        super().save_model(request, obj, form, change)

    actions = ['publish_articles', 'unpublish_articles', 'feature_articles', 'unfeature_articles']

    def publish_articles(self, request, queryset):
        updated = queryset.update(status='PUBLISHED')
        self.message_user(request, f'{updated} articles were successfully published.')
    publish_articles.short_description = "Publish selected articles"

    def unpublish_articles(self, request, queryset):
        updated = queryset.update(status='DRAFT')
        self.message_user(request, f'{updated} articles were successfully unpublished.')
    unpublish_articles.short_description = "Unpublish selected articles"

    def feature_articles(self, request, queryset):
        updated = queryset.update(featured=True)
        self.message_user(request, f'{updated} articles were successfully featured.')
    feature_articles.short_description = "Feature selected articles"

    def unfeature_articles(self, request, queryset):
        updated = queryset.update(featured=False)
        self.message_user(request, f'{updated} articles were successfully unfeatured.')
    unfeature_articles.short_description = "Unfeature selected articles"

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['article', 'author', 'content_preview', 'is_approved', 'is_reply', 'created_at']
    list_filter = ['is_approved', 'created_at', 'article__category']
    list_editable = ['is_approved']
    search_fields = ['content', 'author__username', 'article__title']
    readonly_fields = ['article', 'author', 'parent', 'created_at', 'updated_at']
    ordering = ['-created_at']

    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'

    def is_reply(self, obj):
        return obj.parent is not None
    is_reply.boolean = True
    is_reply.short_description = 'Is Reply'

    actions = ['approve_comments', 'disapprove_comments']

    def approve_comments(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} comments were successfully approved.')
    approve_comments.short_description = "Approve selected comments"

    def disapprove_comments(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} comments were successfully disapproved.')
    disapprove_comments.short_description = "Disapprove selected comments"

@admin.register(ArticleLike)
class ArticleLikeAdmin(admin.ModelAdmin):
    list_display = ['article', 'user', 'created_at']
    list_filter = ['created_at', 'article__category']
    search_fields = ['article__title', 'user__username']
    readonly_fields = ['article', 'user', 'created_at']
    ordering = ['-created_at']

@admin.register(ArticleView)
class ArticleViewAdmin(admin.ModelAdmin):
    list_display = ['article', 'user', 'ip_address', 'created_at']
    list_filter = ['created_at', 'article__category']
    search_fields = ['article__title', 'user__username', 'ip_address']
    readonly_fields = ['article', 'user', 'ip_address', 'user_agent', 'created_at']
    ordering = ['-created_at']

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'article', 'created_at']
    list_filter = ['created_at', 'article__category']
    search_fields = ['user__username', 'article__title']
    readonly_fields = ['user', 'article', 'created_at']
    ordering = ['-created_at']
