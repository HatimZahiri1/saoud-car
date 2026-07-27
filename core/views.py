from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Car, ContactMessage, Review


# ============================================
#  PAGES PUBLIQUES
# ============================================

def home(request):
    """Page d'accueil avec hero section et aperçu des véhicules."""
    featured_cars = Car.objects.filter(is_available=True, featured=True)[:6]

    approved_reviews = Review.objects.filter(is_approved=True)[:6]

    context = {
        'featured_cars': featured_cars,
        'reviews': approved_reviews,
        'page_title': 'SAOUD CAR — Location de Voitures à Ben Slimane',
    }
    return render(request, 'core/home.html', context)


def cars(request):
    """Page catalogue des véhicules avec filtrage."""
    category = request.GET.get('category', '')
    if category:
        vehicles = Car.objects.filter(is_available=True, category=category)
    else:
        vehicles = Car.objects.filter(is_available=True)

    context = {
        'vehicles': vehicles,
        'categories': Car.CATEGORY_CHOICES,
        'selected_category': category,
        'page_title': 'Nos Véhicules — SAOUD CAR',
    }
    return render(request, 'core/cars.html', context)


def about(request):
    """Page à propos de l'entreprise."""
    context = {
        'page_title': 'À Propos — SAOUD CAR',
    }
    return render(request, 'core/about.html', context)


def contact(request):
    """Page de contact avec formulaire."""
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        subject = request.POST.get('subject', '')
        message_text = request.POST.get('message', '')

        if name and email and subject and message_text:
            ContactMessage.objects.create(
                name=name,
                email=email,
                phone=phone,
                subject=subject,
                message=message_text,
            )
            messages.success(request, 'Votre message a été envoyé avec succès ! Nous vous répondrons dans les plus brefs délais.')
            return redirect('core:contact')
        else:
            messages.error(request, 'Veuillez remplir tous les champs obligatoires.')

    context = {
        'page_title': 'Contact — SAOUD CAR',
    }
    return render(request, 'core/contact.html', context)


def submit_review(request):
    """Soumettre un avis client."""
    if request.method == 'POST':
        name = request.POST.get('name', '')
        city = request.POST.get('city', '')
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '')

        if name and comment and 1 <= rating <= 5:
            Review.objects.create(
                name=name,
                city=city,
                rating=rating,
                comment=comment,
                is_approved=False,
            )
            messages.success(request, 'Merci pour votre avis ! Il sera publié après validation.')
            return redirect('core:home')
        else:
            messages.error(request, 'Veuillez remplir tous les champs obligatoires.')

    return redirect('core:home')


# ============================================
#  DASHBOARD ADMIN PERSONNALISÉ
# ============================================

def admin_dashboard(request):
    """Page d'accueil du dashboard admin."""
    total_cars = Car.objects.count()
    available_cars = Car.objects.filter(is_available=True).count()
    featured_cars = Car.objects.filter(featured=True).count()
    total_reviews = Review.objects.count()
    pending_reviews = Review.objects.filter(is_approved=False).count()
    total_messages = ContactMessage.objects.count()
    unread_messages = ContactMessage.objects.filter(is_read=False).count()

    context = {
        'total_cars': total_cars,
        'available_cars': available_cars,
        'featured_cars': featured_cars,
        'total_reviews': total_reviews,
        'pending_reviews': pending_reviews,
        'total_messages': total_messages,
        'unread_messages': unread_messages,
        'recent_reviews': Review.objects.all()[:5],
        'recent_messages': ContactMessage.objects.all()[:5],
    }
    return render(request, 'core/admin/dashboard.html', context)


def admin_cars(request):
    """Liste des voitures dans l'admin."""
    all_cars = Car.objects.all()
    context = {'all_cars': all_cars}
    return render(request, 'core/admin/cars_list.html', context)


def admin_car_add(request):
    """Ajouter une voiture."""
    if request.method == 'POST':
        car = Car(
            name=request.POST.get('name', ''),
            brand=request.POST.get('brand', ''),
            category=request.POST.get('category', 'economique'),
            price_per_day=request.POST.get('price_per_day', 0),
            seats=request.POST.get('seats', 5),
            transmission=request.POST.get('transmission', 'manuelle'),
            fuel_type=request.POST.get('fuel_type', 'diesel'),
            is_available='is_available' in request.POST,
            featured='featured' in request.POST,
            description=request.POST.get('description', ''),
        )
        if request.FILES.get('image'):
            car.image = request.FILES['image']
        car.save()
        messages.success(request, f'Véhicule "{car.brand} {car.name}" ajouté avec succès !')
        return redirect('core:admin_cars')

    context = {
        'categories': Car.CATEGORY_CHOICES,
        'transmissions': [('manuelle', 'Manuelle'), ('automatique', 'Automatique')],
        'fuel_types': [('essence', 'Essence'), ('diesel', 'Diesel'), ('hybride', 'Hybride')],
    }
    return render(request, 'core/admin/car_form.html', context)


def admin_car_edit(request, car_id):
    """Modifier une voiture."""
    car = get_object_or_404(Car, id=car_id)

    if request.method == 'POST':
        car.name = request.POST.get('name', car.name)
        car.brand = request.POST.get('brand', car.brand)
        car.category = request.POST.get('category', car.category)
        car.price_per_day = request.POST.get('price_per_day', car.price_per_day)
        car.seats = request.POST.get('seats', car.seats)
        car.transmission = request.POST.get('transmission', car.transmission)
        car.fuel_type = request.POST.get('fuel_type', car.fuel_type)
        car.is_available = 'is_available' in request.POST
        car.featured = 'featured' in request.POST
        car.description = request.POST.get('description', '')
        if request.FILES.get('image'):
            car.image = request.FILES['image']
        car.save()
        messages.success(request, f'Véhicule "{car.brand} {car.name}" modifié avec succès !')
        return redirect('core:admin_cars')

    context = {
        'car': car,
        'categories': Car.CATEGORY_CHOICES,
        'transmissions': [('manuelle', 'Manuelle'), ('automatique', 'Automatique')],
        'fuel_types': [('essence', 'Essence'), ('diesel', 'Diesel'), ('hybride', 'Hybride')],
    }
    return render(request, 'core/admin/car_form.html', context)


def admin_car_delete(request, car_id):
    """Supprimer une voiture."""
    car = get_object_or_404(Car, id=car_id)
    name = f"{car.brand} {car.name}"
    car.delete()
    messages.success(request, f'Véhicule "{name}" supprimé avec succès !')
    return redirect('core:admin_cars')


def admin_car_toggle_featured(request, car_id):
    """Afficher ou masquer une voiture de la page d'accueil."""
    car = get_object_or_404(Car, id=car_id)
    car.featured = not car.featured
    car.save()
    status = "affiché en page d'accueil" if car.featured else "retiré de la page d'accueil"
    messages.success(request, f'"{car.brand} {car.name}" {status}.')
    return redirect('core:admin_cars')


def admin_reviews(request):
    """Liste des avis clients."""
    all_reviews = Review.objects.all()
    context = {'all_reviews': all_reviews}
    return render(request, 'core/admin/reviews_list.html', context)


def admin_review_approve(request, review_id):
    """Approuver un avis."""
    review = get_object_or_404(Review, id=review_id)
    review.is_approved = not review.is_approved
    review.save()
    status = "approuvé" if review.is_approved else "masqué"
    messages.success(request, f'Avis de "{review.name}" {status}.')
    return redirect('core:admin_reviews')


def admin_review_delete(request, review_id):
    """Supprimer un avis."""
    review = get_object_or_404(Review, id=review_id)
    name = review.name
    review.delete()
    messages.success(request, f'Avis de "{name}" supprimé.')
    return redirect('core:admin_reviews')


def admin_messages(request):
    """Liste des messages de contact."""
    all_messages = ContactMessage.objects.all()
    context = {'all_messages': all_messages}
    return render(request, 'core/admin/messages_list.html', context)


def admin_message_read(request, msg_id):
    """Marquer un message comme lu/non lu."""
    msg = get_object_or_404(ContactMessage, id=msg_id)
    msg.is_read = not msg.is_read
    msg.save()
    return redirect('core:admin_messages')


def admin_message_delete(request, msg_id):
    """Supprimer un message."""
    msg = get_object_or_404(ContactMessage, id=msg_id)
    msg.delete()
    messages.success(request, 'Message supprimé.')
    return redirect('core:admin_messages')
