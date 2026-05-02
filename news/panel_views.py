from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from accounts.mixins import panel_required
from .models import News, NewsCategory, NewsPhoto


@panel_required
def news_list(request):
    news = News.objects.select_related('category', 'author').all()

    category_id = request.GET.get('category')
    is_published = request.GET.get('published')

    if category_id:
        news = news.filter(category_id=category_id)
    if is_published == '1':
        news = news.filter(is_published=True)
    elif is_published == '0':
        news = news.filter(is_published=False)

    from django.core.paginator import Paginator
    paginator = Paginator(news, 20)
    page = request.GET.get('page', 1)
    news_page = paginator.get_page(page)

    context = {
        'news': news_page,
        'categories': NewsCategory.objects.all(),
        'current_category': category_id,
        'is_published': is_published,
    }
    return render(request, 'panel/news/list.html', context)


@panel_required
def news_create(request):
    if request.method == 'POST':
        return _save_news(request, instance=None)
    context = {
        'news': None,
        'categories': NewsCategory.objects.all(),
    }
    return render(request, 'panel/news/form.html', context)


@panel_required
def news_edit(request, pk):
    news = get_object_or_404(News, pk=pk)
    if request.method == 'POST':
        return _save_news(request, instance=news)
    context = {
        'news': news,
        'categories': NewsCategory.objects.all(),
        'photos': news.photos.order_by('order'),
    }
    return render(request, 'panel/news/form.html', context)


def _save_news(request, instance):
    title = request.POST.get('title', '').strip()
    content = request.POST.get('content', '').strip()
    category_id = request.POST.get('category')
    is_published = request.POST.get('is_published') == 'on'
    meta_title = request.POST.get('meta_title', '').strip()
    meta_description = request.POST.get('meta_description', '').strip()
    photos = request.FILES.getlist('photos')

    if not title:
        messages.error(request, 'Заголовок обязателен.')
        return redirect('/panel/news/')

    if instance is None:
        instance = News()
        instance.author = request.user

    instance.title = title
    instance.content = content
    instance.category_id = category_id or None
    instance.is_published = is_published
    instance.meta_title = meta_title
    instance.meta_description = meta_description
    instance.save()

    # Сохраняем фотографии
    existing_count = instance.photos.count()
    for i, photo_file in enumerate(photos):
        from portfolio.image_service import convert_to_webp_and_thumbnail
        main_path, thumb_path = convert_to_webp_and_thumbnail(
            photo_file,
            upload_to='news/photos',
            thumb_upload_to='news/thumbnails',
        )
        NewsPhoto.objects.create(
            news=instance,
            image=main_path,
            thumbnail=thumb_path,
            order=existing_count + i,
        )

    messages.success(request, f'Новость «{instance.title}» сохранена.')
    return redirect('/panel/news/')


@panel_required
def news_delete(request, pk):
    if request.method != 'POST':
        return redirect('/panel/news/')
    news = get_object_or_404(News, pk=pk)
    title = news.title
    news.delete()
    messages.success(request, f'Новость «{title}» удалена.')
    return redirect('/panel/news/')


@panel_required
def news_photo_delete(request, pk):
    if request.method != 'POST':
        return redirect('/panel/news/')
    photo = get_object_or_404(NewsPhoto, pk=pk)
    news_pk = photo.news_id
    import os
    from django.conf import settings
    from pathlib import Path
    for field in [photo.image, photo.thumbnail]:
        if field:
            path = Path(settings.MEDIA_ROOT) / str(field)
            if path.exists():
                os.remove(path)
    photo.delete()
    messages.success(request, 'Фото удалено.')
    return redirect(f'/panel/news/{news_pk}/edit/')


@panel_required
def news_category_list(request):
    categories = NewsCategory.objects.all()
    return render(request, 'panel/news/categories.html', {'categories': categories})


@panel_required
def news_category_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        slug = request.POST.get('slug', '').strip()
        if not name or not slug:
            messages.error(request, 'Заполните все поля.')
            return redirect('/panel/news/categories/')
        if NewsCategory.objects.filter(slug=slug).exists():
            messages.error(request, f'Категория со slug «{slug}» уже существует.')
            return redirect('/panel/news/categories/')
        NewsCategory.objects.create(name=name, slug=slug)
        messages.success(request, f'Категория «{name}» создана.')
    return redirect('/panel/news/categories/')


@panel_required
def news_category_delete(request, pk):
    if request.method != 'POST':
        return redirect('/panel/news/categories/')
    category = get_object_or_404(NewsCategory, pk=pk)
    if category.news_set.exists():
        messages.error(request, 'Нельзя удалить категорию с новостями.')
        return redirect('/panel/news/categories/')
    category.delete()
    messages.success(request, 'Категория удалена.')
    return redirect('/panel/news/categories/')