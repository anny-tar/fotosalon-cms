from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.models import User

from .mixins import panel_required, admin_required
from .models import UserProfile, UserActionLog


@admin_required
def user_list(request):
    users = User.objects.select_related('profile').filter(is_active=True)
    return render(request, 'panel/users/list.html', {'users': users})


@admin_required
def user_create(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        is_superuser = request.POST.get('is_superuser') == 'on'

        if not username or not password:
            messages.error(request, 'Логин и пароль обязательны.')
            return redirect('/panel/users/create/')

        if User.objects.filter(username=username).exists():
            messages.error(request, f'Пользователь «{username}» уже существует.')
            return redirect('/panel/users/create/')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_staff=True,
            is_superuser=is_superuser,
        )

        UserActionLog.objects.create(
            user=request.user,
            action=f'Создан пользователь «{username}»'
        )

        messages.success(request, f'Пользователь «{username}» создан.')
        return redirect('/panel/users/')

    return render(request, 'panel/users/form.html', {'edit_user': None})


@admin_required
def user_edit(request, pk):
    edit_user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        edit_user.first_name = request.POST.get('first_name', '').strip()
        edit_user.last_name = request.POST.get('last_name', '').strip()
        edit_user.email = request.POST.get('email', '').strip()
        edit_user.is_superuser = request.POST.get('is_superuser') == 'on'

        new_password = request.POST.get('password', '').strip()
        if new_password:
            edit_user.set_password(new_password)

        edit_user.save()

        # Настройки уведомлений
        profile = edit_user.profile
        profile.notify_bookings = request.POST.get('notify_bookings') == 'on'
        profile.notify_reviews = request.POST.get('notify_reviews') == 'on'
        profile.save()

        UserActionLog.objects.create(
            user=request.user,
            action=f'Изменён пользователь «{edit_user.username}»'
        )

        messages.success(request, 'Данные пользователя обновлены.')
        return redirect('/panel/users/')

    return render(request, 'panel/users/form.html', {'edit_user': edit_user})


@admin_required
def user_toggle(request, pk):
    if request.method != 'POST':
        return redirect('/panel/users/')
    edit_user = get_object_or_404(User, pk=pk)

    if edit_user == request.user:
        messages.error(request, 'Нельзя заблокировать самого себя.')
        return redirect('/panel/users/')

    edit_user.is_active = not edit_user.is_active
    edit_user.save()
    status = 'разблокирован' if edit_user.is_active else 'заблокирован'
    messages.success(request, f'Пользователь «{edit_user.username}» {status}.')
    return redirect('/panel/users/')


@admin_required
def action_log(request):
    log = UserActionLog.objects.select_related('user').all()

    from django.core.paginator import Paginator
    paginator = Paginator(log, 50)
    page = request.GET.get('page', 1)
    log_page = paginator.get_page(page)

    return render(request, 'panel/users/log.html', {'log': log_page})