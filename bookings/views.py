from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from .models import WorkingSlot, Booking
from services.models import Service
from core.models import SiteSettings, ContactItem

def _base_context():
    return {
        'site_settings': SiteSettings.objects.first(),
        'contact_items': ContactItem.objects.filter(is_active=True).order_by('order'),
    }


def booking_form(request):
    services = Service.objects.filter(is_active=True).order_by('order')
    selected_service = request.GET.get('service')

    if request.method == 'POST':
        client_name  = request.POST.get('client_name', '').strip()
        client_phone = request.POST.get('client_phone', '').strip()
        client_email = request.POST.get('client_email', '').strip()
        service_id   = request.POST.get('service')
        slot_id      = request.POST.get('slot')
        comment      = request.POST.get('comment', '').strip()

        errors = []
        if not client_name:  errors.append('Укажите имя.')
        if not client_phone: errors.append('Укажите телефон.')
        if not client_email: errors.append('Укажите email.')
        if not service_id:   errors.append('Выберите услугу.')
        if not slot_id:      errors.append('Выберите время.')

        if errors:
            ctx = _base_context()
            ctx.update({
                'services': services,
                'errors': errors,
                'post': request.POST,
            })
            return render(request, 'public/booking.html', ctx)

        try:
            service = Service.objects.get(pk=service_id, is_active=True)
            slot = WorkingSlot.objects.get(pk=slot_id, is_blocked=False)

            if not slot.is_available:
                messages.error(request, 'Этот слот уже занят. Выберите другое время.')
                return redirect('/booking/')

            booking = Booking.objects.create(
                client_name=client_name,
                client_phone=client_phone,
                client_email=client_email,
                service=service,
                slot=slot,
                comment=comment,
                status=Booking.STATUS_NEW,
            )

            # Уведомления
            _notify_new_booking(booking)

            return redirect('/booking/success/')

        except (Service.DoesNotExist, WorkingSlot.DoesNotExist):
            messages.error(request, 'Ошибка при создании записи. Попробуйте ещё раз.')
            return redirect('/booking/')

    ctx = _base_context()
    ctx.update({
        'services': services,
        'selected_service': selected_service,
    })
    return render(request, 'public/booking.html', ctx)


def get_slots(request):
    """AJAX — возвращает свободные слоты на выбранную дату."""
    date = request.GET.get('date')
    if not date:
        return JsonResponse({'slots': []})

    slots = WorkingSlot.objects.filter(
        date=date,
        is_blocked=False,
    ).order_by('time_start')

    data = []
    for slot in slots:
        if slot.is_available:
            data.append({
                'id': slot.id,
                'time': f'{slot.time_start.strftime("%H:%M")} – {slot.time_end.strftime("%H:%M")}',
            })

    return JsonResponse({'slots': data})


def booking_success(request):
    ctx = _base_context()
    return render(request, 'public/booking_success.html', ctx)


def _notify_new_booking(booking):
    """Отправляет email уведомления о новой заявке."""
    from django.core.mail import send_mail
    from django.conf import settings
    from accounts.models import UserProfile
    from django.contrib.auth.models import User

    subject = f'Новая заявка #{booking.id} — {booking.service.name}'
    body = (
        f'Новая заявка на запись!\n\n'
        f'Клиент: {booking.client_name}\n'
        f'Телефон: {booking.client_phone}\n'
        f'Email: {booking.client_email}\n'
        f'Услуга: {booking.service.name}\n'
        f'Дата: {booking.slot.date.strftime("%d.%m.%Y")}\n'
        f'Время: {booking.slot.time_start.strftime("%H:%M")}\n'
        f'Комментарий: {booking.comment or "—"}\n'
    )

    # Отправляем всем staff-пользователям у которых включены уведомления
    recipients = []
    for user in User.objects.filter(is_staff=True, is_active=True):
        try:
            if user.profile.notify_bookings:
                recipients.append(user.email)
        except Exception:
            pass

    if recipients:
        try:
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, recipients)
        except Exception:
            pass

    # Email клиенту
    try:
        send_mail(
            f'Ваша заявка принята — {booking.service.name}',
            (
                f'Здравствуйте, {booking.client_name}!\n\n'
                f'Ваша заявка принята. Мы свяжемся с вами для подтверждения.\n\n'
                f'Услуга: {booking.service.name}\n'
                f'Дата: {booking.slot.date.strftime("%d.%m.%Y")}\n'
                f'Время: {booking.slot.time_start.strftime("%H:%M")}\n'
            ),
            settings.DEFAULT_FROM_EMAIL,
            [booking.client_email],
        )
    except Exception:
        pass