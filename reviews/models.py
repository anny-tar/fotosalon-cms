from django.db import models
from django.contrib.auth.models import User


class Review(models.Model):
    author_name = models.CharField(
        max_length=255,
        verbose_name='Имя автора'
    )
    text = models.TextField(
        verbose_name='Текст отзыва'
    )
    rating = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name='Оценка (1–5)'
    )
    is_approved = models.BooleanField(
        default=False,
        verbose_name='Одобрен'
    )
    is_hidden = models.BooleanField(
        default=False,
        verbose_name='Скрыт'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата отправки'
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Одобрен пользователем'
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.author_name} — {self.created_at.strftime("%d.%m.%Y")}'


class ReviewReply(models.Model):
    review = models.OneToOneField(
        Review,
        on_delete=models.CASCADE,
        related_name='reply',
        verbose_name='Отзыв'
    )
    text = models.TextField(
        verbose_name='Текст ответа'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Автор ответа'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата ответа'
    )

    class Meta:
        verbose_name = 'Ответ на отзыв'
        verbose_name_plural = 'Ответы на отзывы'

    def __str__(self):
        return f'Ответ на отзыв {self.review}'