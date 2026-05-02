from django.shortcuts import render
from django.http import JsonResponse
from .models import PortfolioPhoto, PortfolioGenre
from core.models import SiteSettings, ContactInfo


def _base_context():
    return {
        'site_settings': SiteSettings.objects.first(),
        'contact': ContactInfo.objects.first(),
    }


def portfolio_list(request):
    genres = PortfolioGenre.objects.all()
    genre_slug = request.GET.get('genre')

    photos = PortfolioPhoto.objects.filter(is_active=True)
    if genre_slug:
        photos = photos.filter(genre__slug=genre_slug)

    # AJAX запрос — возвращаем JSON
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = [
            {
                'id': p.id,
                'thumbnail': f'/media/{p.thumbnail}',
                'image': f'/media/{p.image_watermarked or p.image}',
                'filename': p.filename,
                'genre': p.genre.name,
            }
            for p in photos
        ]
        return JsonResponse({'photos': data})

    ctx = _base_context()
    ctx['genres'] = genres
    ctx['photos'] = photos
    ctx['current_genre'] = genre_slug
    return render(request, 'public/portfolio.html', ctx)