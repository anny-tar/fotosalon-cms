from django.db import models
from django.contrib.auth.models import User


class NewsCategory(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name='Название категории'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Slug'
    )

    class Meta:
        verbose_name = 'Категория новостей'
        verbose_name_plural = 'Категории новостей'

    def __str__(self):
        return self.name


class News(models.Model):
    title = models.CharField(
        max_length=500,
        verbose_name='Заголовок'
    )
    content = models.TextField(
        verbose_name='Текст новости'
    )
    category = models.ForeignKey(
        NewsCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Категория'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Автор'
    )
    published_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name='Опубликовано'
    )
    meta_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Meta title'
    )
    meta_description = models.TextField(
        blank=True,
        verbose_name='Meta description'
    )
    og_image = models.ImageField(
        upload_to='news/og/',
        blank=True,
        null=True,
        verbose_name='OG Image'
    )

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    def get_cover(self):
        """Возвращает первое фото новости как обложку."""
        first = self.photos.order_by('order').first()
        return first.thumbnail if first else None


class NewsPhoto(models.Model):
    news = models.ForeignKey(
        News,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name='Новость'
    )
    image = models.ImageField(
        upload_to='news/photos/',
        verbose_name='Фотография'
    )
    thumbnail = models.ImageField(
        upload_to='news/thumbnails/',
        blank=True,
        null=True,
        verbose_name='Миниатюра'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Порядок'
    )

    class Meta:
        verbose_name = 'Фотография новости'
        verbose_name_plural = 'Фотографии новости'
        ordering = ['order']

    def __str__(self):
        return f'Фото #{self.order} — {self.news.title}'