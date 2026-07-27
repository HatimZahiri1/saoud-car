from django.db import models


class Car(models.Model):
    CATEGORY_CHOICES = [
        ('economique', 'Économique'),
        ('confort', 'Confort'),
        ('premium', 'Premium'),
        ('suv', 'SUV'),
    ]

    name = models.CharField(max_length=100, verbose_name="Nom du véhicule")
    brand = models.CharField(max_length=50, verbose_name="Marque")
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default='economique', verbose_name="Catégorie"
    )
    price_per_day = models.DecimalField(
        max_digits=8, decimal_places=2, verbose_name="Prix par jour (MAD)"
    )
    seats = models.PositiveIntegerField(default=5, verbose_name="Nombre de places")
    transmission = models.CharField(
        max_length=20,
        choices=[('manuelle', 'Manuelle'), ('automatique', 'Automatique')],
        default='manuelle',
        verbose_name="Transmission",
    )
    fuel_type = models.CharField(
        max_length=20,
        choices=[('essence', 'Essence'), ('diesel', 'Diesel'), ('hybride', 'Hybride')],
        default='diesel',
        verbose_name="Carburant",
    )
    is_available = models.BooleanField(default=True, verbose_name="Disponible")
    featured = models.BooleanField(default=False, verbose_name="Affiché en page d'accueil")
    image = models.ImageField(upload_to='cars/', blank=True, null=True, verbose_name="Photo du véhicule")
    image_url = models.URLField(blank=True, verbose_name="URL de l'image (ancien)")
    description = models.TextField(blank=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Voiture"
        verbose_name_plural = "Voitures"
        ordering = ['price_per_day']

    def __str__(self):
        return f"{self.brand} {self.name}"

    def get_image_url(self):
        """Returns the image URL, preferring uploaded image over URL field."""
        if self.image:
            return self.image.url
        return self.image_url or ''


class Review(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom du client")
    city = models.CharField(max_length=100, blank=True, verbose_name="Ville")
    rating = models.PositiveIntegerField(
        default=5,
        verbose_name="Note",
        help_text="Note de 1 à 5 étoiles"
    )
    comment = models.TextField(verbose_name="Commentaire")
    is_approved = models.BooleanField(default=False, verbose_name="Approuvé")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Avis client"
        verbose_name_plural = "Avis clients"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {'⭐' * self.rating}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom complet")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    subject = models.CharField(max_length=200, verbose_name="Sujet")
    message = models.TextField(verbose_name="Message")
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False, verbose_name="Lu")

    class Meta:
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.subject}"
