from django.shortcuts import render, get_object_or_404
from .models import Product, ProductCategory
from core.models import SiteSettings, ContactItem


def _base_context():
    return {
        'site_settings': SiteSettings.objects.first(),
        'contact_items': ContactItem.objects.filter(is_active=True).order_by('order'),
    }


def product_list(request):
    products = Product.objects.filter(
        is_active=True, quantity__gt=0
    ).select_related('category').order_by('order')

    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)

    ctx = _base_context()
    ctx['products'] = products
    ctx['categories'] = ProductCategory.objects.all()
    ctx['current_category'] = category_slug
    return render(request, 'public/products.html', ctx)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True, quantity__gt=0)
    ctx = _base_context()
    ctx['product'] = product
    return render(request, 'public/product_detail.html', ctx)