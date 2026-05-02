from django.contrib import admin
from .models import FeedbackMessage


@admin.register(FeedbackMessage)
class FeedbackMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at', 'is_read')
    list_filter = ('is_read',)
    readonly_fields = ('name', 'email', 'message', 'created_at')