from django.shortcuts import render
from django.http import HttpResponse
from .models import SiteSettings, ContactInfo, PageSection


def theme_css(request):
    s = SiteSettings.objects.first()

    if s:
        primary        = s.color_primary
        primary_dark   = s.color_primary_dark
        accent         = s.color_accent
        bg             = s.color_bg
        card           = s.color_card
        text           = s.color_text
        text_secondary = s.color_text_secondary
        header_text    = s.color_header_text
        footer_text    = s.color_footer_text
    else:
        primary        = '#2563eb'
        primary_dark   = '#1d4ed8'
        accent         = '#f59e0b'
        bg             = '#f9fafb'
        card           = '#ffffff'
        text           = '#111827'
        text_secondary = '#6b7280'
        header_text    = '#ffffff'
        footer_text    = '#e5e7eb'

    css = f""":root {{
    --primary: {primary};
    --primary-dark: {primary_dark};
    --accent: {accent};
    --color-bg: {bg};
    --color-card: {card};
    --color-text: {text};
    --color-text-secondary: {text_secondary};
    --color-header-text: {header_text};
    --color-footer-text: {footer_text};
}}
"""
    return HttpResponse(css, content_type='text/css')


def _base_context(request):
    """Общий контекст для всех публичных страниц."""
    from services.models import Service
    return {
        'site_settings': SiteSettings.objects.first(),
        'contact': ContactInfo.objects.first(),
        'nav_services': Service.objects.filter(is_active=True)[:6],
    }


def home(request):
    sections = PageSection.objects.filter(
        page='home', is_active=True
    ).select_related('template').order_by('order')

    ctx = _base_context(request)
    ctx['sections'] = sections
    return render(request, 'public/home.html', ctx)


def about(request):
    sections = PageSection.objects.filter(
        page='about', is_active=True
    ).select_related('template').order_by('order')

    ctx = _base_context(request)
    ctx['sections'] = sections
    return render(request, 'public/about.html', ctx)


def contacts(request):
    from feedback.models import FeedbackMessage
    ctx = _base_context(request)

    if request.method == 'POST':
        name    = request.POST.get('name', '').strip()
        email   = request.POST.get('email', '').strip()
        message = request.POST.get('message', '').strip()

        if name and email and message:
            FeedbackMessage.objects.create(
                name=name, email=email, message=message
            )
            ctx['success'] = True
        else:
            ctx['error'] = 'Заполните все поля.'

    return render(request, 'public/contacts.html', ctx)