from django.db import models
from django.contrib.auth.models import User
from services.models import Service


class WorkingSlot(models.Model):
    date = models.DateField(
        verbose_name='Дата'
    )
    time_start = models.TimeField(
        verbose_name='Начало'
    )
    time_end = models.TimeField(
        verbose_name='Конец'
    )
    is_blocked = models.BooleanField(
        default=False,
        verbose_name='Заблокирован'
    )
    block_reason = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Причина блокировки'
    )

    class Meta:
        verbose_name = 'Временной слот'
        verbose_name_plural = 'Временные слоты'
        ordering = ['date', 'time_start']
        unique_together = ['date', 'time_start']

    def __str__(self):
        return f'{self.date} {self.time_start}–{self.time_end}'

    @property
    def is_booked(self):
        """Слот занят подтверждённой или новой заявкой."""
        return self.bookings.filter(
            status__in=['new', 'awaiting_call', 'confirmed']
        ).exists()

    @property
    def is_available(self):
        return not self.is_blocked and not self.is_booked


class Booking(models.Model):
    STATUS_NEW = 'new'
    STATUS_AWAITING_CALL = 'awaiting_call'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_DONE = 'done'
    STATUS_CANCELLED = 'cancelled'
    STATUS_NO_SHOW = 'no_show'

    STATUS_CHOICES = [
        (STATUS_NEW, 'Новая'),
        (STATUS_AWAITING_CALL, 'Ожидает звонка'),
        (STATUS_CONFIRMED, 'Подтверждена'),
        (STATUS_DONE, 'Выполнена'),
        (STATUS_CANCELLED, 'Отменена'),
        (STATUS_NO_SHOW, 'Не пришёл'),
    ]

    # Статусы при смене которых клиент может быть уведомлён
    NOTIFY_STATUSES = [STATUS_CONFIRMED, STATUS_CANCELLED]

    client_name = models.CharField(
        max_length=255,
        verbose_name='Имя клиента'
    )
    client_phone = models.CharField(
        max_length=50,
        verbose_name='Телефон клиента'
    )
    client_email = models.EmailField(
        verbose_name='Email клиента'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        verbose_name='Услуга'
    )
    slot = models.ForeignKey(
        WorkingSlot,
        on_delete=models.PROTECT,
        related_name='bookings',
        verbose_name='Слот'
    )
    comment = models.TextField(
        blank=True,
        verbose_name='Комментарий клиента'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NEW,
        verbose_name='Статус'
    )
    manager_note = models.TextField(
        blank=True,
        verbose_name='Примечание менеджера'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.client_name} — {self.service.name} ({self.slot})'


class BookingHistory(models.Model):
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name='Заявка'
    )
    old_status = models.CharField(
        max_length=20,
        choices=Booking.STATUS_CHOICES,
        verbose_name='Старый статус'
    )
    new_status = models.CharField(
        max_length=20,
        choices=Booking.STATUS_CHOICES,
        verbose_name='Новый статус'
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Изменил'
    )
    changed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата изменения'
    )
    client_notified = models.BooleanField(
        default=False,
        verbose_name='Клиент уведомлён'
    )

    class Meta:
        verbose_name = 'История статуса заявки'
        verbose_name_plural = 'История статусов заявок'
        ordering = ['-changed_at']

    def __str__(self):
        return (
            f'Заявка #{self.booking.id}: '
            f'{self.old_status} → {self.new_status}'
        )