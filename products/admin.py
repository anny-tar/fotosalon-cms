from django.contrib import admin
from .models import ProductCategory, Product


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'article', 'name', 'category',
        'price', 'quantity', 'is_active', 'is_in_stock'
    )
    list_filter = ('category', 'is_active')
    search_fields = ('article', 'name')