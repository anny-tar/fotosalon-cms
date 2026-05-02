from django.http import HttpResponse
from .models import SiteSettings


def home(request):
    return HttpResponse('Публичная часть сайта — в разработке')


def theme_css(request):
    s = SiteSettings.objects.first()

    if s:
        primary          = s.color_primary
        primary_dark     = s.color_primary_dark
        accent           = s.color_accent
        bg               = s.color_bg
        card             = s.color_card
        text             = s.color_text
        text_secondary   = s.color_text_secondary
        header_text      = s.color_header_text
        footer_text      = s.color_footer_text
    else:
        primary          = '#2563eb'
        primary_dark     = '#1d4ed8'
        accent           = '#f59e0b'
        bg               = '#f9fafb'
        card             = '#ffffff'
        text             = '#111827'
        text_secondary   = '#6b7280'
        header_text      = '#ffffff'
        footer_text      = '#e5e7eb'

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