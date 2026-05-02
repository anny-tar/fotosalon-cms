from django.db import models


class Service(models.Model):
    name = models.CharField(
        max_length=500,
        verbose_name='Название услуги'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена'
    )
    duration_minutes = models.PositiveIntegerField(
        verbose_name='Продолжительность (минуты)'
    )
    image = models.ImageField(
        upload_to='services/',
        blank=True,
        null=True,
        verbose_name='Фото'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активна'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Порядок'
    )

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name