from django.db import models


class PortfolioGenre(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name='Название жанра'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Slug'
    )

    class Meta:
        verbose_name = 'Жанр портфолио'
        verbose_name_plural = 'Жанры портфолио'

    def __str__(self):
        return self.name


class PortfolioPhoto(models.Model):
    genre = models.ForeignKey(
        PortfolioGenre,
        on_delete=models.PROTECT,
        related_name='photos',
        verbose_name='Жанр'
    )
    image = models.ImageField(
        upload_to='portfolio/original/',
        verbose_name='Оригинал'
    )
    image_watermarked = models.ImageField(
        upload_to='portfolio/watermarked/',
        blank=True,
        null=True,
        verbose_name='С водяным знаком'
    )
    thumbnail = models.ImageField(
        upload_to='portfolio/thumbnails/',
        blank=True,
        null=True,
        verbose_name='Миниатюра'
    )
    filename = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Имя файла'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активна'
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата загрузки'
    )

    class Meta:
        verbose_name = 'Фотография портфолио'
        verbose_name_plural = 'Фотографии портфолио'
        ordering = ['filename']

    def __str__(self):
        return self.filename