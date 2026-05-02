from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from accounts.mixins import panel_required
from .models import Service


@panel_required
def service_list(request):
    services = Service.objects.all()
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
    name = request.POST.get('name', '').strip()
    description = request.POST.get('description', '').strip()
    price = request.POST.get('price', '0')
    duration = request.POST.get('duration_minutes', '60')
    is_active = request.POST.get('is_active') == 'on'
    order = request.POST.get('order', '0')
    image = request.FILES.get('image')

    if not name:
        messages.error(request, 'Название обязательно.')
        return redirect('/panel/services/')

    if instance is None:
        instance = Service()

    instance.name = name
    instance.description = description
    instance.price = price
    instance.duration_minutes = int(duration)
    instance.is_active = is_active
    instance.order = int(order)

    if image:
        from portfolio.image_service import convert_to_webp_and_thumbnail
        main_path, thumb_path = convert_to_webp_and_thumbnail(
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