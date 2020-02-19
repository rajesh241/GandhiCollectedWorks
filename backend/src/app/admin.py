from django.contrib import admin
from .models import Article

class ArticleModelAdmin(admin.ModelAdmin):
    """Model Adminf or class Location"""
    list_display = ["id", "volume_number", "chapter_number", "title", "posted"]
    list_filter = ["volume_number"]
    search_fields = ["title"]
admin.site.register(Article, ArticleModelAdmin)
