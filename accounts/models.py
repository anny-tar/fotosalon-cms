from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Пользователь'
    )
    notify_bookings = models.BooleanField(
        default=True,
        verbose_name='Уведомления о новых заявках'
    )
    notify_reviews = models.BooleanField(
        default=True,
        verbose_name='Уведомления о новых отзывах'
    )

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f'Профиль {self.user.username}'


class UserActionLog(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Пользователь'
    )
    action = models.TextField(verbose_name='Действие')
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время'
    )

    class Meta:
        verbose_name = 'Запись журнала действий'
        verbose_name_plural = 'Журнал действий'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} — {self.action[:50]}'