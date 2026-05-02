from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from accounts.mixins import panel_required
from .models import PortfolioPhoto, PortfolioGenre
from .image_service import convert_to_webp_and_thumbnail, apply_watermark


@panel_required
def portfolio_list(request):
    genre_id = request.GET.get('genre')
    sort = request.GET.get('sort', 'asc')

    photos = PortfolioPhoto.objects.select_related('genre').all()

    if genre_id:
        photos = photos.filter(genre_id=genre_id)

    if sort == 'desc':
        photos = photos.order_by('-filename')
    else:
        photos = photos.order_by('filename')

    from django.core.paginator import Paginator
    paginator = Paginator(photos, 24)
    page = request.GET.get('page', 1)
    photos_page = paginator.get_page(page)

    context = {
        'photos': photos_page,
        'genres': PortfolioGenre.objects.all(),
        'current_genre': genre_id,
        'sort': sort,
    }
    return render(request, 'panel/portfolio/list.html', context)


@panel_required
def portfolio_upload(request):
    if request.method != 'POST':
        return redirect('/panel/portfolio/')

    genre_id = request.POST.get('genre')
    genre = get_object_or_404(PortfolioGenre, pk=genre_id)
    files = request.FILES.getlist('photos')

    if not files:
        messages.error(request, 'Выберите хотя бы один файл.')
        return redirect('/panel/portfolio/')

    created = 0
    conflicts = []

    for f in files:
        from pathlib import Path
        filename = Path(f.name).name

        # Проверка уникальности имени файла
        if PortfolioPhoto.objects.filter(filename=filename).exists():
            conflicts.append(filename)
            continue

        try:
            # Конвертация в WebP + миниатюра
            main_path, thumb_path = convert_to_webp_and_thumbnail(
                f,
                upload_to='portfolio/original',
                thumb_upload_to='portfolio/thumbnails',
            )

            # Водяной знак
            watermarked_path = apply_watermark(main_path)

            PortfolioPhoto.objects.create(
                genre=genre,
                image=main_path,
                image_watermarked=watermarked_path,
                thumbnail=thumb_path,
                filename=filename,
                is_active=True,
            )
            created += 1

        except Exception as e:
            messages.error(request, f'Ошибка при загрузке {filename}: {e}')

    if created:
        messages.success(request, f'Загружено фотографий: {created}.')
    if conflicts:
        names = ', '.join(conflicts)
        messages.warning(
            request,
            f'Файлы с такими именами уже существуют и пропущены: {names}'
        )

    return redirect('/panel/portfolio/')


@panel_required
def portfolio_toggle(request, pk):
    if request.method != 'POST':
        return redirect('/panel/portfolio/')
    photo = get_object_or_404(PortfolioPhoto, pk=pk)
    photo.is_active = not photo.is_active
    photo.save()
    status = 'активирована' if photo.is_active else 'деактивирована'
    messages.success(request, f'Фотография {status}.')
    return redirect('/panel/portfolio/')


@panel_required
def portfolio_delete(request, pk):
    if request.method != 'POST':
        return redirect('/panel/portfolio/')
    photo = get_object_or_404(PortfolioPhoto, pk=pk)

    # Удаляем физические файлы
    import os
    from django.conf import settings
    from pathlib import Path
    for field in [photo.image, photo.image_watermarked, photo.thumbnail]:
        if field:
            file_path = Path(settings.MEDIA_ROOT) / str(field)
            if file_path.exists():
                os.remove(file_path)

    photo.delete()
    messages.success(request, 'Фотография удалена.')
    return redirect('/panel/portfolio/')


@panel_required
def genre_list(request):
    genres = PortfolioGenre.objects.all()
    return render(request, 'panel/portfolio/genres.html', {'genres': genres})


@panel_required
def genre_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        slug = request.POST.get('slug', '').strip()
        if not name or not slug:
            messages.error(request, 'Заполните название и slug.')
            return redirect('/panel/portfolio/genres/')
        if PortfolioGenre.objects.filter(slug=slug).exists():
            messages.error(request, f'Жанр со slug «{slug}» уже существует.')
            return redirect('/panel/portfolio/genres/')
        PortfolioGenre.objects.create(name=name, slug=slug)
        messages.success(request, f'Жанр «{name}» создан.')
    return redirect('/panel/portfolio/genres/')


@panel_required
def genre_delete(request, pk):
    if request.method != 'POST':
        return redirect('/panel/portfolio/genres/')
    genre = get_object_or_404(PortfolioGenre, pk=pk)
    if genre.photos.exists():
        messages.error(request, 'Нельзя удалить жанр с фотографиями.')
        return redirect('/panel/portfolio/genres/')
    genre.delete()
    messages.success(request, 'Жанр удалён.')
    return redirect('/panel/portfolio/genres/')