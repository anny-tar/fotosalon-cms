from django.contrib import admin
from .models import NewsCategory, News, NewsPhoto


class NewsPhotoInline(admin.TabularInline):
    model = NewsPhoto
    extra = 1
    fields = ('image', 'order')


@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'published_at', 'is_published')
    list_filter = ('is_published', 'category')
    inlines = [NewsPhotoInline]