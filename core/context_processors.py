from .models import Review, ContactMessage


def admin_counts(request):
    """Provides counts for admin sidebar badges."""
    if request.path.startswith('/admin/'):
        return {
            'pending_reviews_count': Review.objects.filter(is_approved=False).count(),
            'unread_messages_count': ContactMessage.objects.filter(is_read=False).count(),
            'active_page': _get_active_page(request.path),
        }
    return {}


def _get_active_page(path):
    """Determine active sidebar page from URL path."""
    if '/admin/voitures' in path:
        return 'cars'
    elif '/admin/avis' in path:
        return 'reviews'
    elif '/admin/messages' in path:
        return 'messages'
    return 'dashboard'
