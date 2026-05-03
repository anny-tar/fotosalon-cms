from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Review
from core.models import SiteSettings, ContactItem


def _base_context():
    return {
        'site_settings': SiteSettings.objects.first(),
        'contact_items': ContactItem.objects.filter(is_active=True).order_by('order'),
    }


def review_list(request):
    reviews = Review.objects.filter(
        is_approved=True, is_hidden=False
    ).select_related('reply').order_by('-created_at')

    if request.method == 'POST':
        author_name = request.POST.get('author_name', '').strip()
        text = request.POST.get('text', '').strip()
        rating = request.POST.get('rating') or None

        if not author_name or not text:
            messages.error(request, 'Заполните имя и текст отзыва.')
        else:
            Review.objects.create(
                author_name=author_name,
                text=text,
                rating=rating,
            )
            messages.success(
                request,
                'Спасибо! Ваш отзыв отправлен на модерацию.'
            )
            return redirect('/reviews/')

    ctx = _base_context()
    ctx['reviews'] = reviews
    return render(request, 'public/reviews.html', ctx)