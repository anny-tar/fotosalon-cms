from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from accounts.mixins import panel_required
from .models import FeedbackMessage


@panel_required
def feedback_list(request):
    messages_qs = FeedbackMessage.objects.all()

    is_read = request.GET.get('is_read')
    if is_read == '0':
        messages_qs = messages_qs.filter(is_read=False)
    elif is_read == '1':
        messages_qs = messages_qs.filter(is_read=True)

    from django.core.paginator import Paginator
    paginator = Paginator(messages_qs, 20)
    page = request.GET.get('page', 1)
    messages_page = paginator.get_page(page)

    context = {
        'messages': messages_page,
        'is_read': is_read,
        'unread_count': FeedbackMessage.objects.filter(is_read=False).count(),
    }
    return render(request, 'panel/feedback/list.html', context)


@panel_required
def feedback_detail(request, pk):
    msg = get_object_or_404(FeedbackMessage, pk=pk)
    if not msg.is_read:
        msg.is_read = True
        msg.save()
    return render(request, 'panel/feedback/detail.html', {'msg': msg})


@panel_required
def feedback_mark_read(request, pk):
    if request.method != 'POST':
        return redirect('/panel/feedback/')
    msg = get_object_or_404(FeedbackMessage, pk=pk)
    msg.is_read = True
    msg.save()
    messages.success(request, 'Сообщение отмечено как прочитанное.')
    return redirect('/panel/feedback/')


@panel_required
def feedback_delete(request, pk):
    if request.method != 'POST':
        return redirect('/panel/feedback/')
    msg = get_object_or_404(FeedbackMessage, pk=pk)
    msg.delete()
    messages.success(request, 'Сообщение удалено.')
    return redirect('/panel/feedback/')