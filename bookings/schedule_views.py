from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from datetime import date, timedelta, datetime

from accounts.mixins import panel_required
from .models import WorkingSlot, Booking


@panel_required
def schedule_grid(request):
    """Сетка расписания — неделя или выбранная дата."""
    # Определяем начало недели
    week_offset = int(request.GET.get('week', 0))
    today = date.today()
    monday = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    week_days = [monday + timedelta(days=i) for i in range(7)]

    # Все слоты за эту неделю
    slots = WorkingSlot.objects.filter(
        date__gte=monday,
        date__lte=monday + timedelta(days=6)
    ).order_by('date', 'time_start')

    # Группируем слоты по дате
    slots_by_date = {}
    for day in week_days:
        slots_by_date[day] = []
    for slot in slots:
        if slot.date in slots_by_date:
            slots_by_date[slot.date].append(slot)

    context = {
        'week_days': week_days,
        'slots_by_date': slots_by_date,
        'week_offset': week_offset,
        'prev_week': week_offset - 1,
        'next_week': week_offset + 1,
        'today': today,
    }
    return render(request, 'panel/schedule/grid.html', context)


@panel_required
def slot_create(request):
    """Создание одного слота."""
    if request.method == 'POST':
        slot_date = request.POST.get('date')
        time_start = request.POST.get('time_start')
        time_end = request.POST.get('time_end')

        if not all([slot_date, time_start, time_end]):
            messages.error(request, 'Заполните все поля.')
            return redirect('/panel/schedule/')

        # Проверяем уникальность
        exists = WorkingSlot.objects.filter(
            date=slot_date,
            time_start=time_start
        ).exists()

        if exists:
            messages.error(request, f'Слот на {slot_date} в {time_start} уже существует.')
            return redirect('/panel/schedule/')

        WorkingSlot.objects.create(
            date=slot_date,
            time_start=time_start,
            time_end=time_end,
        )
        messages.success(request, f'Слот {slot_date} {time_start}–{time_end} создан.')
        return redirect('/panel/schedule/')

    return redirect('/panel/schedule/')


@panel_required
def slot_toggle_block(request, pk):
    """Заблокировать / разблокировать слот."""
    if request.method != 'POST':
        return redirect('/panel/schedule/')

    slot = get_object_or_404(WorkingSlot, pk=pk)
    reason = request.POST.get('block_reason', '').strip()

    if slot.is_blocked:
        slot.is_blocked = False
        slot.block_reason = ''
        messages.success(request, f'Слот {slot} разблокирован.')
    else:
        slot.is_blocked = True
        slot.block_reason = reason
        messages.success(request, f'Слот {slot} заблокирован.')

    slot.save()
    return redirect('/panel/schedule/')


@panel_required
def slot_delete(request, pk):
    """Удаление слота (только если не занят заявкой)."""
    if request.method != 'POST':
        return redirect('/panel/schedule/')

    slot = get_object_or_404(WorkingSlot, pk=pk)

    if slot.is_booked:
        messages.error(request, 'Нельзя удалить слот с активной заявкой.')
        return redirect('/panel/schedule/')

    slot.delete()
    messages.success(request, 'Слот удалён.')
    return redirect('/panel/schedule/')


@panel_required
def slots_generate(request):
    """Массовая генерация слотов на период."""
    if request.method == 'POST':
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')
        time_start = request.POST.get('time_start')
        time_end = request.POST.get('time_end')
        skip_weekends = request.POST.get('skip_weekends') == 'on'

        if not all([date_from, date_to, time_start, time_end]):
            messages.error(request, 'Заполните все поля.')
            return redirect('/panel/schedule/')

        start = date.fromisoformat(date_from)
        end = date.fromisoformat(date_to)

        if end < start:
            messages.error(request, 'Дата окончания раньше даты начала.')
            return redirect('/panel/schedule/')

        created = 0
        skipped = 0
        current = start
        while current <= end:
            if skip_weekends and current.weekday() >= 5:
                current += timedelta(days=1)
                continue

            exists = WorkingSlot.objects.filter(
                date=current,
                time_start=time_start
            ).exists()

            if not exists:
                WorkingSlot.objects.create(
                    date=current,
                    time_start=time_start,
                    time_end=time_end,
                )
                created += 1
            else:
                skipped += 1

            current += timedelta(days=1)

        messages.success(
            request,
            f'Создано слотов: {created}. Пропущено (уже существуют): {skipped}.'
        )
        return redirect('/panel/schedule/')

    return redirect('/panel/schedule/')