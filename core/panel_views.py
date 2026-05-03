from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

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
        order     = request.POST.get('order', 0)

        if not label or not value:
            messages.error(request, 'Заполните описание и значение.')
            return redirect('/panel/settings/contact/')

        ContactItem.objects.create(
            type=item_type,
            label=label,
            value=value,
            order=int(order),
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
        item.order = int(request.POST.get('order', 0))
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
    page = request.GET.get('page', 'home')
    sections = PageSection.objects.filter(page=page).select_related('template')
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
        order       = request.POST.get('order', 0)
        content     = request.POST.get('content', '{}')

        import json
        try:
            content_data = json.loads(content)
        except Exception:
            content_data = {}

        PageSection.objects.create(
            page=page,
            template_id=template_id,
            order=int(order),
            content=content_data,
            is_active=True,
        )
        messages.success(request, 'Секция добавлена.')
    return redirect('/panel/settings/sections/')


@admin_required
def section_edit(request, pk):
    section = get_object_or_404(PageSection, pk=pk)
    if request.method == 'POST':
        section.order     = int(request.POST.get('order', 0))
        section.is_active = request.POST.get('is_active') == 'on'

        import json
        content = request.POST.get('content', '{}')
        try:
            section.content = json.loads(content)
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
    section.delete()
    messages.success(request, 'Секция удалена.')
    return redirect('/panel/settings/sections/')


@admin_required
def section_toggle(request, pk):
    if request.method != 'POST':
        return redirect('/panel/settings/sections/')
    section = get_object_or_404(PageSection, pk=pk)
    section.is_active = not section.is_active
    section.save()
    return redirect('/panel/settings/sections/')