from django.http import HttpResponse
from .models import SiteSettings


def home(request):
    return HttpResponse('Публичная часть сайта — в разработке')


def theme_css(request):
    settings = SiteSettings.objects.first()

    if settings:
        primary = settings.color_primary
        primary_dark = settings.color_primary_dark
        accent = settings.color_accent
        bg = settings.color_bg
        text = settings.color_text
    else:
        primary = '#2563eb'
        primary_dark = '#1d4ed8'
        accent = '#f59e0b'
        bg = '#f9fafb'
        text = '#111827'

    css = f""":root {{
    --primary: {primary};
    --primary-dark: {primary_dark};
    --accent: {accent};
    --color-bg: {bg};
    --color-text: {text};
}}
"""
    return HttpResponse(css, content_type='text/css')