from django.contrib import admin
from .models import Review, ReviewReply


class ReviewReplyInline(admin.StackedInline):
    model = ReviewReply
    extra = 0
    max_num = 1


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author_name', 'rating', 'is_approved', 'is_hidden', 'created_at')
    list_filter = ('is_approved', 'is_hidden')
    inlines = [ReviewReplyInline]