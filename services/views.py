from django.shortcuts import render
from .models import Service
from core.models import SiteSettings, ContactInfo


def _base_context():
    return {
        'site_settings': SiteSettings.objects.first(),
        'contact': ContactInfo.objects.first(),
    }


def service_list(request):
    services = Service.objects.filter(is_active=True).order_by('order')
    ctx = _base_context()
    ctx['services'] = services
    selected = request.GET.get('service')
    ctx['selected_service'] = selected
    return render(request, 'public/services.html', ctx)