from django.contrib import admin
from .models import WorkingSlot, Booking, BookingHistory


class BookingHistoryInline(admin.TabularInline):
    model = BookingHistory
    extra = 0
    readonly_fields = ('old_status', 'new_status', 'changed_by', 'changed_at', 'client_notified')
    can_delete = False


@admin.register(WorkingSlot)
class WorkingSlotAdmin(admin.ModelAdmin):
    list_display = ('date', 'time_start', 'time_end', 'is_blocked', 'is_available')
    list_filter = ('date', 'is_blocked')
    ordering = ['date', 'time_start']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'client_name', 'client_phone', 'service',
        'slot', 'status', 'created_at'
    )
    list_filter = ('status', 'service')
    search_fields = ('client_name', 'client_phone', 'client_email')
    inlines = [BookingHistoryInline]
    readonly_fields = ('created_at', 'updated_at')


@admin.register(BookingHistory)
class BookingHistoryAdmin(admin.ModelAdmin):
    list_display = ('booking', 'old_status', 'new_status', 'changed_by', 'changed_at')
    readonly_fields = ('booking', 'old_status', 'new_status', 'changed_by', 'changed_at')