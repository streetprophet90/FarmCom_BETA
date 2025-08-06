from django import forms
from django.contrib.auth import get_user_model
from .models import Article, Comment, Category, Tag, Bookmark

User = get_user_model()

class ArticleForm(forms.ModelForm):
    """Form for creating and editing articles"""
    
    class Meta:
        model = Article
        fields = [
            'title', 'content', 'excerpt', 'category', 'tags', 
            'status', 'difficulty', 'featured', 'meta_title', 'meta_description'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter article title...'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 15,
                'placeholder': 'Write your article content here...'
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Brief summary of the article...'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'tags': forms.SelectMultiple(attrs={
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'difficulty': forms.Select(attrs={
                'class': 'form-control'
            }),
            'featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'meta_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'SEO title (optional)'
            }),
            'meta_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'SEO description (optional)'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make tags field more user-friendly
        self.fields['tags'].widget.attrs.update({
            'data-placeholder': 'Select tags...',
            'multiple': 'multiple'
        })

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content.strip()) < 100:
            raise forms.ValidationError("Article content must be at least 100 characters long.")
        return content

    def clean_excerpt(self):
        excerpt = self.cleaned_data.get('excerpt')
        if excerpt and len(excerpt.strip()) < 20:
            raise forms.ValidationError("Excerpt must be at least 20 characters long.")
        return excerpt

class CommentForm(forms.ModelForm):
    """Form for adding comments to articles"""
    
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Write your comment here...'
            })
        }

    def __init__(self, *args, **kwargs):
        self.article = kwargs.pop('article', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content.strip()) < 10:
            raise forms.ValidationError("Comment must be at least 10 characters long.")
        return content

    def save(self, commit=True):
        comment = super().save(commit=False)
        if self.article:
            comment.article = self.article
        if self.user:
            comment.author = self.user
        if commit:
            comment.save()
        return comment

class ReplyForm(CommentForm):
    """Form for replying to comments"""
    
    def __init__(self, *args, **kwargs):
        self.parent_comment = kwargs.pop('parent_comment', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        comment = super().save(commit=False)
        if self.parent_comment:
            comment.parent = self.parent_comment
        if commit:
            comment.save()
        return comment

class ArticleSearchForm(forms.Form):
    """Form for searching articles"""
    
    SEARCH_CHOICES = [
        ('title', 'Title'),
        ('content', 'Content'),
        ('author', 'Author'),
        ('all', 'All Fields'),
    ]
    
    SORT_CHOICES = [
        ('newest', 'Newest First'),
        ('oldest', 'Oldest First'),
        ('popular', 'Most Popular'),
        ('views', 'Most Viewed'),
        ('likes', 'Most Liked'),
    ]
    
    query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search articles...'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    difficulty = forms.ChoiceField(
        choices=[('', 'All Levels')] + Article.DIFFICULTY_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control',
            'data-placeholder': 'Select tags...'
        })
    )
    
    search_in = forms.ChoiceField(
        choices=SEARCH_CHOICES,
        initial='all',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        initial='newest',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    featured_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

class BookmarkForm(forms.ModelForm):
    """Form for bookmarking articles"""
    
    class Meta:
        model = Bookmark
        fields = []

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.article = kwargs.pop('article', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        bookmark, created = Bookmark.objects.get_or_create(
            user=self.user,
            article=self.article
        )
        return bookmark

class CategoryForm(forms.ModelForm):
    """Form for creating and editing categories"""
    
    class Meta:
        model = Category
        fields = ['name', 'description', 'icon', 'color', 'order', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Category name...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Category description...'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Font Awesome icon class (e.g., fas fa-seedling)'
            }),
            'color': forms.Select(attrs={
                'class': 'form-control'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add color choices
        self.fields['color'].choices = [
            ('primary', 'Primary (Blue)'),
            ('secondary', 'Secondary (Gray)'),
            ('success', 'Success (Green)'),
            ('danger', 'Danger (Red)'),
            ('warning', 'Warning (Yellow)'),
            ('info', 'Info (Cyan)'),
            ('light', 'Light'),
            ('dark', 'Dark'),
        ]

class TagForm(forms.ModelForm):
    """Form for creating and editing tags"""
    
    class Meta:
        model = Tag
        fields = ['name', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tag name...'
            }),
            'color': forms.Select(attrs={
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add color choices
        self.fields['color'].choices = [
            ('secondary', 'Secondary (Gray)'),
            ('primary', 'Primary (Blue)'),
            ('success', 'Success (Green)'),
            ('danger', 'Danger (Red)'),
            ('warning', 'Warning (Yellow)'),
            ('info', 'Info (Cyan)'),
            ('light', 'Light'),
            ('dark', 'Dark'),
        ] 