from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta

from .mixins import panel_required
from bookings.models import Booking
from reviews.models import Review
from services.models import Service
from products.models import Product
from feedback.models import FeedbackMessage
from django.db.models import F


@panel_required
def dashboard(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)

    # Счётчики
    new_bookings_today = Booking.objects.filter(
        created_at__date=today,
        status=Booking.STATUS_NEW
    ).count()

    bookings_this_month = Booking.objects.filter(
        created_at__date__gte=month_start
    ).count()

    pending_reviews = Review.objects.filter(
        is_approved=False,
        is_hidden=False
    ).count()

    active_services = Service.objects.filter(is_active=True).count()

    unread_feedback = FeedbackMessage.objects.filter(is_read=False).count()

    # График заявок за последние 30 дней
    period_days = int(request.GET.get('days', 30))
    period_start = today - timedelta(days=period_days - 1)

    chart_data = _get_chart_data(period_start, today)

    # Топ-3 услуги по числу заявок
    from django.db.models import Count
    top_services = (
        Service.objects
        .annotate(bookings_count=Count('booking'))
        .filter(bookings_count__gt=0)
        .order_by('-bookings_count')[:3]
    )

    # Товары с низким остатком
    low_stock = Product.objects.filter(
        quantity__lte=models.F('min_quantity')
    ).select_related('category')

    context = {
        'new_bookings_today': new_bookings_today,
        'bookings_this_month': bookings_this_month,
        'pending_reviews': pending_reviews,
        'active_services': active_services,
        'unread_feedback': unread_feedback,
        'chart_data': chart_data,
        'period_days': period_days,
        'top_services': top_services,
        'low_stock': low_stock,
    }
    return render(request, 'panel/dashboard.html', context)


def _get_chart_data(date_from, date_to):
    """Формирует данные для графика заявок по дням."""
    from django.db.models import Count
    from datetime import timedelta

    bookings_by_day = (
        Booking.objects
        .filter(created_at__date__gte=date_from, created_at__date__lte=date_to)
        .values('created_at__date')
        .annotate(count=Count('id'))
    )

    bookings_dict = {
        item['created_at__date']: item['count']
        for item in bookings_by_day
    }

    labels = []
    data = []
    current = date_from
    while current <= date_to:
        labels.append(current.strftime('%d.%m'))
        data.append(bookings_dict.get(current, 0))
        current += timedelta(days=1)

    return {'labels': labels, 'data': data}


def panel_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('panel:dashboard')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user and user.is_staff:
            login(request, user)
            return redirect('panel:dashboard')
        else:
            error = 'Неверный логин или пароль, либо нет доступа к панели.'

    return render(request, 'panel/login.html', {'error': error})


@login_required(login_url='/panel/login/')
def panel_logout(request):
    logout(request)
    return redirect('panel:login')