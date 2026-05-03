from .models import SiteSettings, ContactItem
from reviews.models import Review
from feedback.models import FeedbackMessage
from bookings.models import Booking


def panel_context(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return {}

    return {
        'site_settings': SiteSettings.objects.first(),
        'pending_reviews_count': Review.objects.filter(
            is_approved=False, is_hidden=False
        ).count(),
        'unread_feedback_count': FeedbackMessage.objects.filter(
            is_read=False
        ).count(),
        'pending_bookings_count': Booking.objects.filter(
            status=Booking.STATUS_NEW
        ).count(),
    }