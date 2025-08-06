from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q, Count, F
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import Article, Category, Tag, Comment, ArticleLike, ArticleView, Bookmark
from .forms import ArticleForm, CommentForm, ReplyForm, ArticleSearchForm, BookmarkForm
from accounts.notification_utils import create_enhanced_notification

User = get_user_model()

class ArticleListView(ListView):
    """Display list of published articles with search and filtering"""
    model = Article
    template_name = 'knowledge_base/article_list.html'
    context_object_name = 'articles'
    paginate_by = 12

    def get_queryset(self):
        queryset = Article.objects.filter(
            status='PUBLISHED',
            published_at__lte=timezone.now()
        ).select_related('author', 'category').prefetch_related('tags')
        
        # Apply search and filters
        form = ArticleSearchForm(self.request.GET)
        if form.is_valid():
            query = form.cleaned_data.get('query')
            category = form.cleaned_data.get('category')
            difficulty = form.cleaned_data.get('difficulty')
            tags = form.cleaned_data.get('tags')
            search_in = form.cleaned_data.get('search_in')
            sort_by = form.cleaned_data.get('sort_by')
            featured_only = form.cleaned_data.get('featured_only')
            
            # Search functionality
            if query:
                if search_in == 'title':
                    queryset = queryset.filter(title__icontains=query)
                elif search_in == 'content':
                    queryset = queryset.filter(content__icontains=query)
                elif search_in == 'author':
                    queryset = queryset.filter(author__username__icontains=query)
                else:  # all
                    queryset = queryset.filter(
                        Q(title__icontains=query) |
                        Q(content__icontains=query) |
                        Q(author__username__icontains=query) |
                        Q(excerpt__icontains=query)
                    )
            
            # Filters
            if category:
                queryset = queryset.filter(category=category)
            
            if difficulty:
                queryset = queryset.filter(difficulty=difficulty)
            
            if tags:
                queryset = queryset.filter(tags__in=tags).distinct()
            
            if featured_only:
                queryset = queryset.filter(featured=True)
            
            # Sorting
            if sort_by == 'oldest':
                queryset = queryset.order_by('published_at')
            elif sort_by == 'popular':
                queryset = queryset.order_by('-likes', '-views')
            elif sort_by == 'views':
                queryset = queryset.order_by('-views')
            elif sort_by == 'likes':
                queryset = queryset.order_by('-likes')
            else:  # newest
                queryset = queryset.order_by('-published_at')
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ArticleSearchForm(self.request.GET)
        context['categories'] = Category.objects.filter(is_active=True)
        context['featured_articles'] = Article.objects.filter(
            status='PUBLISHED',
            featured=True,
            published_at__lte=timezone.now()
        ).select_related('author', 'category')[:6]
        context['popular_tags'] = Tag.objects.annotate(
            article_count=Count('articles')
        ).filter(article_count__gt=0).order_by('-article_count')[:10]
        return context

class ArticleDetailView(DetailView):
    """Display individual article with comments and related articles"""
    model = Article
    template_name = 'knowledge_base/article_detail.html'
    context_object_name = 'article'

    def get_queryset(self):
        return Article.objects.filter(
            status='PUBLISHED',
            published_at__lte=timezone.now()
        ).select_related('author', 'category').prefetch_related('tags', 'comments__author')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.get_object()
        
        # Track view
        if self.request.user.is_authenticated:
            ArticleView.objects.get_or_create(
                article=article,
                user=self.request.user,
                defaults={'ip_address': self.request.META.get('REMOTE_ADDR')}
            )
        else:
            ArticleView.objects.get_or_create(
                article=article,
                ip_address=self.request.META.get('REMOTE_ADDR'),
                defaults={'user_agent': self.request.META.get('HTTP_USER_AGENT', '')}
            )
        
        # Increment view count
        article.increment_views()
        
        # Get approved comments
        context['comments'] = article.comments.filter(is_approved=True, parent=None)
        context['comment_form'] = CommentForm(article=article, user=self.request.user)
        
        # Related articles
        context['related_articles'] = Article.objects.filter(
            status='PUBLISHED',
            category=article.category,
            published_at__lte=timezone.now()
        ).exclude(id=article.id)[:4]
        
        # Check if user has liked/bookmarked
        if self.request.user.is_authenticated:
            context['user_liked'] = ArticleLike.objects.filter(
                article=article, user=self.request.user
            ).exists()
            context['user_bookmarked'] = Bookmark.objects.filter(
                article=article, user=self.request.user
            ).exists()
        
        return context

class CategoryDetailView(ListView):
    """Display articles by category"""
    model = Article
    template_name = 'knowledge_base/category_detail.html'
    context_object_name = 'articles'
    paginate_by = 12

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'], is_active=True)
        return Article.objects.filter(
            category=self.category,
            status='PUBLISHED',
            published_at__lte=timezone.now()
        ).select_related('author').prefetch_related('tags').order_by('-published_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context

class TagDetailView(ListView):
    """Display articles by tag"""
    model = Article
    template_name = 'knowledge_base/tag_detail.html'
    context_object_name = 'articles'
    paginate_by = 12

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        return Article.objects.filter(
            tags=self.tag,
            status='PUBLISHED',
            published_at__lte=timezone.now()
        ).select_related('author', 'category').prefetch_related('tags').order_by('-published_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        return context

class ArticleCreateView(LoginRequiredMixin, CreateView):
    """Create new article"""
    model = Article
    form_class = ArticleForm
    template_name = 'knowledge_base/article_form.html'
    success_url = reverse_lazy('knowledge_base:article_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        
        # Create notification for new article
        if form.instance.status == 'PUBLISHED':
            create_enhanced_notification(
                user=self.request.user,
                notification_type='Article Published',
                title=f'Article "{form.instance.title}" published',
                message=f'Your article "{form.instance.title}" has been published successfully.',
                related_object=form.instance
            )
        
        messages.success(self.request, 'Article created successfully!')
        return response

class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update existing article"""
    model = Article
    form_class = ArticleForm
    template_name = 'knowledge_base/article_form.html'

    def test_func(self):
        article = self.get_object()
        return self.request.user == article.author or self.request.user.is_superuser

    def get_success_url(self):
        return self.object.get_absolute_url()

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Article updated successfully!')
        return response

class ArticleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete article"""
    model = Article
    template_name = 'knowledge_base/article_confirm_delete.html'
    success_url = reverse_lazy('knowledge_base:article_list')

    def test_func(self):
        article = self.get_object()
        return self.request.user == article.author or self.request.user.is_superuser

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Article deleted successfully!')
        return super().delete(request, *args, **kwargs)

@login_required
@require_POST
def like_article(request, article_id):
    """Like/unlike an article"""
    article = get_object_or_404(Article, id=article_id)
    like, created = ArticleLike.objects.get_or_create(
        article=article, user=request.user
    )
    
    if created:
        article.likes += 1
        article.save()
        liked = True
    else:
        like.delete()
        article.likes = max(0, article.likes - 1)
        article.save()
        liked = False
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': liked,
            'likes_count': article.likes
        })
    
    return HttpResponseRedirect(article.get_absolute_url())

@login_required
@require_POST
def bookmark_article(request, article_id):
    """Bookmark/unbookmark an article"""
    article = get_object_or_404(Article, id=article_id)
    bookmark, created = Bookmark.objects.get_or_create(
        article=article, user=request.user
    )
    
    if not created:
        bookmark.delete()
        bookmarked = False
    else:
        bookmarked = True
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'bookmarked': bookmarked})
    
    return HttpResponseRedirect(article.get_absolute_url())

@login_required
def add_comment(request, article_id):
    """Add comment to article"""
    article = get_object_or_404(Article, id=article_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST, article=article, user=request.user)
        if form.is_valid():
            comment = form.save()
            
            # Create notification for article author
            if comment.author != article.author:
                create_enhanced_notification(
                    user=article.author,
                    notification_type='New Comment',
                    title=f'New comment on "{article.title}"',
                    message=f'{comment.author.username} commented on your article.',
                    related_object=comment
                )
            
            messages.success(request, 'Comment added successfully!')
            return redirect(article.get_absolute_url())
    else:
        form = CommentForm(article=article, user=request.user)
    
    return render(request, 'knowledge_base/article_detail.html', {
        'article': article,
        'comment_form': form
    })

@login_required
def add_reply(request, comment_id):
    """Add reply to comment"""
    parent_comment = get_object_or_404(Comment, id=comment_id)
    article = parent_comment.article
    
    if request.method == 'POST':
        form = ReplyForm(request.POST, article=article, user=request.user, parent_comment=parent_comment)
        if form.is_valid():
            reply = form.save()
            
            # Create notification for parent comment author
            if reply.author != parent_comment.author:
                create_enhanced_notification(
                    user=parent_comment.author,
                    notification_type='New Reply',
                    title=f'New reply to your comment',
                    message=f'{reply.author.username} replied to your comment on "{article.title}".',
                    related_object=reply
                )
            
            messages.success(request, 'Reply added successfully!')
            return redirect(article.get_absolute_url())
    else:
        form = ReplyForm(article=article, user=request.user, parent_comment=parent_comment)
    
    return render(request, 'knowledge_base/article_detail.html', {
        'article': article,
        'reply_form': form,
        'parent_comment': parent_comment
    })

@login_required
def my_articles(request):
    """Display user's articles"""
    articles = Article.objects.filter(author=request.user).order_by('-created_at')
    paginator = Paginator(articles, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'knowledge_base/my_articles.html', {
        'page_obj': page_obj,
        'articles': page_obj
    })

@login_required
def my_bookmarks(request):
    """Display user's bookmarked articles"""
    bookmarks = Bookmark.objects.filter(user=request.user).select_related('article__author', 'article__category')
    paginator = Paginator(bookmarks, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'knowledge_base/my_bookmarks.html', {
        'page_obj': page_obj,
        'bookmarks': page_obj
    })

def search_articles(request):
    """Advanced search for articles"""
    form = ArticleSearchForm(request.GET)
    articles = []
    
    if form.is_valid() and any(form.cleaned_data.values()):
        articles = Article.objects.filter(
            status='PUBLISHED',
            published_at__lte=timezone.now()
        ).select_related('author', 'category').prefetch_related('tags')
        
        # Apply search filters
        query = form.cleaned_data.get('query')
        category = form.cleaned_data.get('category')
        difficulty = form.cleaned_data.get('difficulty')
        tags = form.cleaned_data.get('tags')
        search_in = form.cleaned_data.get('search_in')
        sort_by = form.cleaned_data.get('sort_by')
        featured_only = form.cleaned_data.get('featured_only')
        
        if query:
            if search_in == 'title':
                articles = articles.filter(title__icontains=query)
            elif search_in == 'content':
                articles = articles.filter(content__icontains=query)
            elif search_in == 'author':
                articles = articles.filter(author__username__icontains=query)
            else:
                articles = articles.filter(
                    Q(title__icontains=query) |
                    Q(content__icontains=query) |
                    Q(author__username__icontains=query) |
                    Q(excerpt__icontains=query)
                )
        
        if category:
            articles = articles.filter(category=category)
        
        if difficulty:
            articles = articles.filter(difficulty=difficulty)
        
        if tags:
            articles = articles.filter(tags__in=tags).distinct()
        
        if featured_only:
            articles = articles.filter(featured=True)
        
        # Sorting
        if sort_by == 'oldest':
            articles = articles.order_by('published_at')
        elif sort_by == 'popular':
            articles = articles.order_by('-likes', '-views')
        elif sort_by == 'views':
            articles = articles.order_by('-views')
        elif sort_by == 'likes':
            articles = articles.order_by('-likes')
        else:
            articles = articles.order_by('-published_at')
    
    paginator = Paginator(articles, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'knowledge_base/search_results.html', {
        'form': form,
        'page_obj': page_obj,
        'articles': page_obj,
        'search_performed': form.is_valid() and any(form.cleaned_data.values())
    })
