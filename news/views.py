from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import News, NewsCategory
from core.models import SiteSettings, ContactItem


def _base_context():
    return {
        'site_settings': SiteSettings.objects.first(),
        'contact_items': ContactItem.objects.filter(is_active=True).order_by('order'),
    }


def news_list(request):
    news = News.objects.filter(is_published=True).order_by('-published_at')

    category_slug = request.GET.get('category')
    if category_slug:
        news = news.filter(category__slug=category_slug)

    paginator = Paginator(news, 10)
    page = request.GET.get('page', 1)
    news_page = paginator.get_page(page)

    ctx = _base_context()
    ctx['news'] = news_page
    ctx['categories'] = NewsCategory.objects.all()
    ctx['current_category'] = category_slug
    return render(request, 'public/news_list.html', ctx)


def news_detail(request, pk):
    item = get_object_or_404(News, pk=pk, is_published=True)
    ctx = _base_context()
    ctx['item'] = item
    ctx['photos'] = item.photos.order_by('order')
    return render(request, 'public/news_detail.html', ctx)