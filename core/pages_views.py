import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages

from accounts.mixins import admin_required
from .models import PageSection, SiteSettings


PAGE_CHOICES = {
    'home':  'Главная страница',
    'about': 'О нас',
}

SECTION_TYPES = {
    'banner':         'Баннер',
    'services_grid':  'Сетка услуг',
    'products_grid':  'Сетка товаров',
    'portfolio':      'Портфолио',
    'reviews_block':  'Отзывы',
    'news_preview':   'Превью новостей',
    'text_block':     'Текстовый блок',
    'image_text':     'Изображение + текст',
    'cta':            'Призыв к действию',
    'promo':          'Акция',
    'faq':            'Вопросы и ответы',
    'table_block':    'Таблица',
    'person_block':   'О человеке / команде',
}


@admin_required
def pages_list(request):
    """Список страниц с конструктором."""
    pages = []
    for slug, name in PAGE_CHOICES.items():
        count = PageSection.objects.filter(page=slug).count()
        active = PageSection.objects.filter(page=slug, is_active=True).count()
        pages.append({
            'slug': slug,
            'name': name,
            'count': count,
            'active': active,
        })
    return render(request, 'panel/pages/list.html', {'pages': pages})


@admin_required
def sections_list(request, page):
    """Список секций конкретной страницы."""
    if page not in PAGE_CHOICES:
        return redirect('/panel/pages/')

    sections = PageSection.objects.filter(
        page=page
    ).order_by('order')

    context = {
        'page_slug': page,
        'page_name': PAGE_CHOICES[page],
        'sections': sections,
        'section_types': SECTION_TYPES,
    }
    return render(request, 'panel/pages/sections.html', context)


@admin_required
def section_create(request, page):
    if request.method != 'POST':
        return redirect(f'/panel/pages/{page}/sections/')

    section_type = request.POST.get('section_type')
    if section_type not in SECTION_TYPES:
        messages.error(request, 'Неверный тип секции.')
        return redirect(f'/panel/pages/{page}/sections/')

    last = PageSection.objects.filter(page=page).order_by('order').last()
    order = (last.order + 1) if last else 0

    # Получаем шаблон с таким именем
    from .models import SectionTemplate
    template, _ = SectionTemplate.objects.get_or_create(
        template_name=section_type,
        defaults={'name': SECTION_TYPES[section_type]}
    )

    section = PageSection.objects.create(
        page=page,
        template=template,
        order=order,
        content={},
        draft_content={},
        is_active=True,
    )

    messages.success(request, f'Секция «{SECTION_TYPES[section_type]}» добавлена.')
    return redirect(f'/panel/pages/sections/{section.pk}/edit/')


@admin_required
def section_edit(request, pk):
    section = get_object_or_404(PageSection, pk=pk)

    if request.method == 'POST':
        # Публикуем черновик как основной контент
        content_raw = request.POST.get('content', '{}')
        is_active   = request.POST.get('is_active') == 'on'
        try:
            section.content = json.loads(content_raw)
        except Exception:
            section.content = {}
        section.draft_content = {}
        section.is_active = is_active
        section.save()
        messages.success(request, 'Секция сохранена.')
        return redirect(f'/panel/pages/{section.page}/sections/')

    template_name = section.template.template_name
    context = {
        'section': section,
        'template_name': template_name,
        'section_type_name': SECTION_TYPES.get(template_name, template_name),
    }
    return render(request, 'panel/pages/section_edit.html', context)


@admin_required
def section_delete(request, pk):
    if request.method != 'POST':
        return redirect('/panel/pages/')
    section = get_object_or_404(PageSection, pk=pk)
    page = section.page
    section.delete()
    messages.success(request, 'Секция удалена.')
    return redirect(f'/panel/pages/{page}/sections/')


@admin_required
def section_toggle(request, pk):
    if request.method != 'POST':
        return redirect('/panel/pages/')
    section = get_object_or_404(PageSection, pk=pk)
    section.is_active = not section.is_active
    section.save()
    return redirect(f'/panel/pages/{section.page}/sections/')


@admin_required
@require_POST
def section_draft_save(request, pk):
    """Сохраняет черновик — посетители не видят изменений."""
    section = get_object_or_404(PageSection, pk=pk)
    content_raw = request.POST.get('content', '{}')
    try:
        section.draft_content = json.loads(content_raw)
    except Exception:
        section.draft_content = {}
    section.save()

    preview_url = f'/{section.page}/?preview=1#section-{section.pk}'
    return JsonResponse({'ok': True, 'preview_url': preview_url})


@admin_required
@require_POST
def section_publish(request, pk):
    """Публикует черновик."""
    section = get_object_or_404(PageSection, pk=pk)
    if section.draft_content:
        section.content = section.draft_content
        section.draft_content = {}
        section.save()
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False, 'error': 'Нет черновика'})


@admin_required
@require_POST
def section_reorder(request):
    try:
        data  = json.loads(request.body)
        order = data.get('order', [])
        for index, pk in enumerate(order):
            PageSection.objects.filter(pk=pk).update(order=index)
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})


@admin_required
def section_preview(request):
    """Живое превью секции через AJAX — рендерит реальный шаблон."""
    template_name = request.POST.get('template_name', '')
    content_raw   = request.POST.get('content', '{}')

    try:
        content = json.loads(content_raw)
    except Exception:
        content = {}

    settings = SiteSettings.objects.first()

    # Подставляем переменные
    def replace_vars(text):
        if not text or not isinstance(text, str):
            return text
        return text.replace(
            '{site_name}', settings.site_name if settings else ''
        ).replace(
            '{slogan}', settings.slogan if settings else ''
        )

    content['title']    = replace_vars(content.get('title', ''))
    content['subtitle'] = replace_vars(content.get('subtitle', ''))

    # Создаём временный объект секции без обращения к БД
    section_obj          = PageSection.__new__(PageSection)
    section_obj.content  = content
    section_obj.pk       = None

    # Загружаем дополнительные данные для секции
    extra = _get_section_extra(template_name, content)

    template_path = f'public/sections/{template_name}.html'
    try:
        from django.template.loader import render_to_string
        section_html = render_to_string(template_path, {
            'section':       section_obj,
            'site_settings': settings,
            **extra,
        }, request=request)
    except Exception as e:
        section_html = f'<div style="padding:16px;color:#dc2626">Ошибка шаблона: {e}</div>'

    full_html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="/theme.css">
<link rel="stylesheet" href="/static/css/public.css">
<style>body{{margin:0;padding:0;}}</style>
</head>
<body>{section_html}</body>
</html>"""

    return HttpResponse(full_html)


def _get_section_extra(template_name, content):
    """Загружает дополнительные данные для рендеринга секции."""
    extra = {}

    if template_name == 'banner' and content.get('show_news'):
        from news.models import News
        extra['preview_news'] = News.objects.filter(
            is_published=True
        ).order_by('-published_at')[:3]

    elif template_name == 'services_grid':
        from services.models import Service
        service_ids = content.get('service_ids', [])
        if service_ids:
            extra['section_services'] = Service.objects.filter(
                pk__in=service_ids, is_active=True
            )
        else:
            extra['section_services'] = Service.objects.filter(
                is_active=True
            ).order_by('order')[:6]

    elif template_name == 'products_grid':
        from products.models import Product
        product_ids = content.get('product_ids', [])
        if product_ids:
            extra['section_products'] = Product.objects.filter(
                pk__in=product_ids, is_active=True, quantity__gt=0
            )
        else:
            extra['section_products'] = Product.objects.filter(
                is_active=True, quantity__gt=0
            ).order_by('order')[:6]

    elif template_name == 'portfolio':
        from portfolio.models import PortfolioPhoto
        genre_slug = content.get('genre_slug')
        count      = int(content.get('photo_count', 6))
        photos = PortfolioPhoto.objects.filter(is_active=True)
        if genre_slug:
            photos = photos.filter(genre__slug=genre_slug)
        extra['section_photos'] = photos.order_by('?')[:count]

    elif template_name == 'reviews_block':
        from reviews.models import Review
        count = int(content.get('review_count', 3))
        extra['section_reviews'] = Review.objects.filter(
            is_approved=True, is_hidden=False
        ).select_related('reply').order_by('-created_at')[:count]

    elif template_name == 'news_preview':
        from news.models import News
        count = int(content.get('news_count', 3))
        extra['section_news'] = News.objects.filter(
            is_published=True
        ).order_by('-published_at')[:count]

    return extra


@admin_required
@require_POST
def section_upload_image(request):
    image     = request.FILES.get('image')
    upload_to = request.POST.get('upload_to', 'sections')
    if not image:
        return JsonResponse({'error': 'Нет файла'}, status=400)
    from portfolio.image_service import convert_to_webp_and_thumbnail
    main_path, _ = convert_to_webp_and_thumbnail(
        image,
        upload_to=upload_to,
        thumb_upload_to=upload_to + '/thumbnails',
    )
    return JsonResponse({'path': main_path})