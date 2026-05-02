from django.contrib import admin
from .models import UserProfile, UserActionLog


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'notify_bookings', 'notify_reviews')


@admin.register(UserActionLog)
class UserActionLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'created_at')
    readonly_fields = ('user', 'action', 'created_at')