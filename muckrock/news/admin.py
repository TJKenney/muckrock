"""
Admin registration for news models
"""

from django import forms
from django.contrib import admin

from epiceditor.widgets import AdminEpicEditorWidget

from muckrock.news.models import Article, Photo

class ArticleAdminForm(forms.ModelForm):
    """Form with EpicEditor"""

    body = forms.CharField(widget=AdminEpicEditorWidget(themes={'editor': 'epic-light-2.css',
                                                                'preview': 'preview-light.css'}))
    
    class Meta:
        # pylint: disable=R0903
        model = Article

class ArticleAdmin(admin.ModelAdmin):
    """Model Admin for a news article"""
    # pylint: disable=R0904

    form = ArticleAdminForm
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('title', 'author', 'pub_date', 'publish')
    list_filter = ['pub_date']
    date_hierarchy = 'pub_date'
    search_fields = ['title', 'body']

admin.site.register(Article, ArticleAdmin)
admin.site.register(Photo)

