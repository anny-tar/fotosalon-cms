from django.contrib import admin
from .models import PortfolioGenre, PortfolioPhoto


@admin.register(PortfolioGenre)
class PortfolioGenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(PortfolioPhoto)
class PortfolioPhotoAdmin(admin.ModelAdmin):
    list_display = ('filename', 'genre', 'is_active', 'uploaded_at')
    list_filter = ('genre', 'is_active')