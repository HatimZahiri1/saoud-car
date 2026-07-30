from .models import Review, ContactMessage, RentalContract, TechnicalInspection, Insurance
import datetime


def admin_counts(request):
    """Provides counts for admin sidebar badges and alerts."""
    if request.path.startswith('/admin/'):
        today = datetime.date.today()
        alert_date = today + datetime.timedelta(days=30)

        # Count expiring items for alerts badge
        expiring_inspections = TechnicalInspection.objects.filter(expiry_date__lte=alert_date).count()
        expiring_insurances = Insurance.objects.filter(expiry_date__lte=alert_date).count()
        active_contracts = RentalContract.objects.filter(status='en_cours').count()

        return {
            'pending_reviews_count': Review.objects.filter(is_approved=False).count(),
            'unread_messages_count': ContactMessage.objects.filter(is_read=False).count(),
            'active_contracts_count': active_contracts,
            'alerts_count': expiring_inspections + expiring_insurances,
            'active_page': _get_active_page(request.path),
        }
    return {}


def _get_active_page(path):
    """Determine active sidebar page from URL path."""
    if '/admin/voitures' in path:
        return 'cars'
    elif '/admin/marques' in path:
        return 'brands'
    elif '/admin/clients' in path:
        return 'clients'
    elif '/admin/contrats' in path:
        return 'contracts'
    elif '/admin/visites' in path:
        return 'inspections'
    elif '/admin/assurances' in path:
        return 'insurances'
    elif '/admin/avis' in path:
        return 'reviews'
    elif '/admin/messages' in path:
        return 'messages'
    return 'dashboard'
