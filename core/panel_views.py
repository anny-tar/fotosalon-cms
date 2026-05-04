from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

from accounts.mixins import admin_required
from .models import (
    SiteSettings, ContactItem, SmtpSettings,
    SectionTemplate, PageSection
)


@admin_required
def settings_view(request):
    settings_obj = SiteSettings.objects.first()
    if request.method == 'POST':
        if not settings_obj:
            settings_obj = SiteSettings()

        settings_obj.site_name            = request.POST.get('site_name', '').strip()
        settings_obj.slogan               = request.POST.get('slogan', '').strip()
        settings_obj.meta_title           = request.POST.get('meta_title', '').strip()
        settings_obj.meta_description     = request.POST.get('meta_description', '').strip()
        settings_obj.color_primary        = request.POST.get('color_primary', '#2563eb')
        settings_obj.color_primary_dark   = request.POST.get('color_primary_dark', '#1d4ed8')
        settings_obj.color_accent         = request.POST.get('color_accent', '#f59e0b')
        settings_obj.color_bg             = request.POST.get('color_bg', '#f9fafb')
        settings_obj.color_card           = request.POST.get('color_card', '#ffffff')
        settings_obj.color_text           = request.POST.get('color_text', '#111827')
        settings_obj.color_text_secondary = request.POST.get('color_text_secondary', '#6b7280')
        settings_obj.color_header_text    = request.POST.get('color_header_text', '#ffffff')
        settings_obj.color_footer_text    = request.POST.get('color_footer_text', '#e5e7eb')

        logo = request.FILES.get('logo')
        if logo:
            from portfolio.image_service import convert_to_webp_and_thumbnail
            main_path, _ = convert_to_webp_and_thumbnail(
                logo,
                upload_to='site',
                thumb_upload_to='site/thumbnails',
            )
            settings_obj.logo = main_path

        settings_obj.save()
        messages.success(request, 'Настройки сайта сохранены.')
        return redirect('/panel/settings/')

    return render(request, 'panel/settings/general.html', {
        'settings': settings_obj
    })


@admin_required
def contact_settings(request):
    items = ContactItem.objects.all().order_by('order', 'type')
    return render(request, 'panel/settings/contact.html', {'items': items})


@admin_required
def contact_create(request):
    if request.method == 'POST':
        item_type = request.POST.get('type')
        label     = request.POST.get('label', '').strip()
        value     = request.POST.get('value', '').strip()

        if not label or not value:
            messages.error(request, 'Заполните описание и значение.')
            return redirect('/panel/settings/contact/')

        last = ContactItem.objects.order_by('order').last()
        order = (last.order + 1) if last else 0

        ContactItem.objects.create(
            type=item_type,
            label=label,
            value=value,
            order=order,
            is_active=True,
        )
        messages.success(request, 'Контакт добавлен.')
    return redirect('/panel/settings/contact/')


@admin_required
def contact_edit(request, pk):
    item = get_object_or_404(ContactItem, pk=pk)
    if request.method == 'POST':
        item.type  = request.POST.get('type', item.type)
        item.label = request.POST.get('label', '').strip()
        item.value = request.POST.get('value', '').strip()
        item.save()
        messages.success(request, 'Контакт обновлён.')
        return redirect('/panel/settings/contact/')
    return render(request, 'panel/settings/contact_edit.html', {
        'item': item,
        'type_choices': ContactItem.TYPE_CHOICES,
    })


@admin_required
def contact_delete(request, pk):
    if request.method != 'POST':
        return redirect('/panel/settings/contact/')
    item = get_object_or_404(ContactItem, pk=pk)
    item.delete()
    messages.success(request, 'Контакт удалён.')
    return redirect('/panel/settings/contact/')


@admin_required
def contact_toggle(request, pk):
    if request.method != 'POST':
        return redirect('/panel/settings/contact/')
    item = get_object_or_404(ContactItem, pk=pk)
    item.is_active = not item.is_active
    item.save()
    return redirect('/panel/settings/contact/')


@admin_required
@require_POST
def contact_reorder(request):
    try:
        data  = json.loads(request.body)
        order = data.get('order', [])
        for index, pk in enumerate(order):
            ContactItem.objects.filter(pk=pk).update(order=index)
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})


@admin_required
def smtp_settings(request):
    smtp = SmtpSettings.objects.first()
    if request.method == 'POST':
        if not smtp:
            smtp = SmtpSettings()

        smtp.host       = request.POST.get('host', '').strip()
        smtp.port       = int(request.POST.get('port', 587))
        smtp.username   = request.POST.get('username', '').strip()
        smtp.from_email = request.POST.get('from_email', '').strip()
        smtp.use_tls    = True

        password = request.POST.get('password', '').strip()
        if password:
            import base64
            smtp.password = base64.b64encode(password.encode()).decode()

        smtp.save()
        messages.success(request, 'Настройки SMTP сохранены.')
        return redirect('/panel/settings/smtp/')

    return render(request, 'panel/settings/smtp.html', {'smtp': smtp})


@admin_required
def sections_list(request):
    page     = request.GET.get('page', 'home')
    sections = PageSection.objects.filter(page=page).select_related('template').order_by('order')
    templates = SectionTemplate.objects.all()

    context = {
        'sections': sections,
        'templates': templates,
        'current_page': page,
    }
    return render(request, 'panel/settings/sections.html', context)


@admin_required
def section_create(request):
    if request.method == 'POST':
        page        = request.POST.get('page', 'home')
        template_id = request.POST.get('template')

        last = PageSection.objects.filter(page=page).order_by('order').last()
        order = (last.order + 1) if last else 0

        import json as _json
        PageSection.objects.create(
            page=page,
            template_id=template_id,
            order=order,
            content={},
            is_active=True,
        )
        messages.success(request, 'Секция добавлена.')
    return redirect(f'/panel/settings/sections/?page={request.POST.get("page", "home")}')


@admin_required
def section_edit(request, pk):
    section = get_object_or_404(PageSection, pk=pk)
    if request.method == 'POST':
        section.is_active = request.POST.get('is_active') == 'on'

        import json as _json
        content = request.POST.get('content', '{}')
        try:
            section.content = _json.loads(content)
        except Exception:
            section.content = {}

        section.save()
        messages.success(request, 'Секция обновлена.')
        return redirect('/panel/settings/sections/')

    return render(request, 'panel/settings/section_form.html', {'section': section})


@admin_required
def section_delete(request, pk):
    if request.method != 'POST':
        return redirect('/panel/settings/sections/')
    section = get_object_or_404(PageSection, pk=pk)
    page = section.page
    section.delete()
    messages.success(request, 'Секция удалена.')
    return redirect(f'/panel/settings/sections/?page={page}')


@admin_required
def section_toggle(request, pk):
    if request.method != 'POST':
        return redirect('/panel/settings/sections/')
    section = get_object_or_404(PageSection, pk=pk)
    section.is_active = not section.is_active
    section.save()
    return redirect(f'/panel/settings/sections/?page={section.page}')


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

from django.views.decorators.http import require_POST as _require_POST

@admin_required
def section_preview(request):
    """Рендерит превью секции по переданным данным."""
    import json as _json
    template_name = request.POST.get('template_name', '')
    content_raw   = request.POST.get('content', '{}')

    try:
        content = _json.loads(content_raw)
    except Exception:
        content = {}

    # Подгружаем нужные данные для секции
    extra = {}
    if template_name == 'banner' and content.get('show_news'):
        from news.models import News
        extra['preview_news'] = News.objects.filter(
            is_published=True
        ).order_by('-published_at')[:3]

    from core.models import SiteSettings
    settings = SiteSettings.objects.first()

    # Подставляем переменные
    def replace_vars(text):
        if not text:
            return text
        replacements = {
            '{site_name}': settings.site_name if settings else '',
            '{slogan}':    settings.slogan if settings else '',
        }
        for k, v in replacements.items():
            text = text.replace(k, v or '')
        return text

    content['title']    = replace_vars(content.get('title', ''))
    content['subtitle'] = replace_vars(content.get('subtitle', ''))

    template_path = f'public/sections/{template_name}.html'
    try:
        return render(request, template_path, {
            'section': type('obj', (object,), {'content': content})(),
            'site_settings': settings,
            **extra,
        })
    except Exception as e:
        from django.http import HttpResponse
        return HttpResponse(f'<p style="color:red">Ошибка: {e}</p>')

@admin_required
@require_POST
def section_upload_image(request):
    image = request.FILES.get('image')
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