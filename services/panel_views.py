from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

from accounts.mixins import panel_required
from .models import Service


@panel_required
def service_list(request):
    services = Service.objects.all().order_by('order')
    return render(request, 'panel/services/list.html', {'services': services})


@panel_required
def service_create(request):
    if request.method == 'POST':
        return _save_service(request, instance=None)
    return render(request, 'panel/services/form.html', {'service': None})


@panel_required
def service_edit(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        return _save_service(request, instance=service)
    return render(request, 'panel/services/form.html', {'service': service})


def _save_service(request, instance):
    name        = request.POST.get('name', '').strip()
    description = request.POST.get('description', '').strip()
    price       = request.POST.get('price', '0')
    duration    = request.POST.get('duration_minutes', '60')
    is_active   = request.POST.get('is_active') == 'on'
    image       = request.FILES.get('image')

    if not name:
        messages.error(request, 'Название обязательно.')
        return redirect('/panel/services/')

    if instance is None:
        instance = Service()
        # Порядок — следующий после последнего
        last = Service.objects.order_by('order').last()
        instance.order = (last.order + 1) if last else 0

    instance.name             = name
    instance.description      = description
    instance.price            = price
    instance.duration_minutes = int(duration)
    instance.is_active        = is_active

    if image:
        from portfolio.image_service import convert_to_webp_and_thumbnail
        main_path, _ = convert_to_webp_and_thumbnail(
            image,
            upload_to='services',
            thumb_upload_to='services/thumbnails',
        )
        instance.image = main_path

    instance.save()
    messages.success(request, f'Услуга «{instance.name}» сохранена.')
    return redirect('/panel/services/')


@panel_required
def service_delete(request, pk):
    if request.method != 'POST':
        return redirect('/panel/services/')
    service = get_object_or_404(Service, pk=pk)
    name = service.name
    service.delete()
    messages.success(request, f'Услуга «{name}» удалена.')
    return redirect('/panel/services/')


@panel_required
def service_toggle(request, pk):
    if request.method != 'POST':
        return redirect('/panel/services/')
    service = get_object_or_404(Service, pk=pk)
    service.is_active = not service.is_active
    service.save()
    status = 'активирована' if service.is_active else 'деактивирована'
    messages.success(request, f'Услуга {status}.')
    return redirect('/panel/services/')


@panel_required
@require_POST
def service_reorder(request):
    try:
        data = json.loads(request.body)
        order = data.get('order', [])
        for index, pk in enumerate(order):
            Service.objects.filter(pk=pk).update(order=index)
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})