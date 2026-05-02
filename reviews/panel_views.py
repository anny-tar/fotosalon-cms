from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from accounts.mixins import panel_required
from .models import Review, ReviewReply


@panel_required
def review_list(request):
    reviews = Review.objects.all()

    status = request.GET.get('status', 'pending')
    if status == 'pending':
        reviews = reviews.filter(is_approved=False, is_hidden=False)
    elif status == 'approved':
        reviews = reviews.filter(is_approved=True)
    elif status == 'hidden':
        reviews = reviews.filter(is_hidden=True)

    from django.core.paginator import Paginator
    paginator = Paginator(reviews, 20)
    page = request.GET.get('page', 1)
    reviews_page = paginator.get_page(page)

    context = {
        'reviews': reviews_page,
        'current_status': status,
        'pending_count': Review.objects.filter(is_approved=False, is_hidden=False).count(),
    }
    return render(request, 'panel/reviews/list.html', context)


@panel_required
def review_approve(request, pk):
    if request.method != 'POST':
        return redirect('/panel/reviews/')
    review = get_object_or_404(Review, pk=pk)
    review.is_approved = True
    review.is_hidden = False
    review.approved_by = request.user
    review.save()
    messages.success(request, 'Отзыв одобрен.')
    return redirect('/panel/reviews/')


@panel_required
def review_hide(request, pk):
    if request.method != 'POST':
        return redirect('/panel/reviews/')
    review = get_object_or_404(Review, pk=pk)
    review.is_hidden = True
    review.is_approved = False
    review.save()
    messages.success(request, 'Отзыв скрыт.')
    return redirect('/panel/reviews/')


@panel_required
def review_delete(request, pk):
    if request.method != 'POST':
        return redirect('/panel/reviews/')
    review = get_object_or_404(Review, pk=pk)
    review.delete()
    messages.success(request, 'Отзыв удалён.')
    return redirect('/panel/reviews/')


@panel_required
def review_reply(request, pk):
    if request.method != 'POST':
        return redirect('/panel/reviews/')
    review = get_object_or_404(Review, pk=pk)
    text = request.POST.get('text', '').strip()
    if not text:
        messages.error(request, 'Текст ответа не может быть пустым.')
        return redirect('/panel/reviews/')

    # Один ответ на отзыв — обновляем если уже есть
    ReviewReply.objects.update_or_create(
        review=review,
        defaults={'text': text, 'author': request.user},
    )
    messages.success(request, 'Ответ сохранён.')
    return redirect('/panel/reviews/')