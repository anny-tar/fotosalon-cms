from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from accounts.mixins import admin_required
from .models import (
    SiteSettings, ContactInfo, SmtpSettings,
    SectionTemplate, PageSection
)


@admin_required
def settings_view(request):
    settings_obj = SiteSettings.objects.first()
    if request.method == 'POST':
        site_name = request.POST.get('site_name', '').strip()
        meta_title = request.POST.get('meta_title', '').strip()
        meta_description = request.POST.get('meta_description', '').strip()
        logo = request.FILES.get('logo')

        if not settings_obj:
            settings_obj = SiteSettings()

        settings_obj.site_name = site_name
        settings_obj.meta_title = meta_title
        settings_obj.meta_description = meta_description

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
    contact = ContactInfo.objects.first()
    if request.method == 'POST':
        if not contact:
            contact = ContactInfo()

        contact.address = request.POST.get('address', '').strip()
        contact.phone = request.POST.get('phone', '').strip()
        contact.email = request.POST.get('email', '').strip()
        contact.working_hours = request.POST.get('working_hours', '').strip()
        contact.map_lat = request.POST.get('map_lat') or None
        contact.map_lng = request.POST.get('map_lng') or None
        contact.save()
        messages.success(request, 'Контактные данные сохранены.')
        return redirect('/panel/settings/contact/')

    return render(request, 'panel/settings/contact.html', {'contact': contact})


@admin_required
def smtp_settings(request):
    smtp = SmtpSettings.objects.first()
    if request.method == 'POST':
        if not smtp:
            smtp = SmtpSettings()

        smtp.host = request.POST.get('host', '').strip()
        smtp.port = int(request.POST.get('port', 587))
        smtp.username = request.POST.get('username', '').strip()
        smtp.from_email = request.POST.get('from_email', '').strip()
        smtp.use_tls = request.POST.get('use_tls') == 'on'

        password = request.POST.get('password', '').strip()
        if password:
            # Простое шифрование через base64
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
        page = request.POST.get('page', 'home')
        template_id = request.POST.get('template')
        order = request.POST.get('order', 0)
        content = request.POST.get('content', '{}')

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
        section.order = int(request.POST.get('order', 0))
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