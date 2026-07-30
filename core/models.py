from django.db import models
from django.utils import timezone
import datetime


# ============================================
#  MODÈLE MARQUE
# ============================================
class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom de la marque")
    logo = models.ImageField(upload_to='brands/', blank=True, null=True, verbose_name="Logo")
    country = models.CharField(max_length=100, blank=True, verbose_name="Pays d'origine")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Marque"
        verbose_name_plural = "Marques"
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def car_count(self):
        return self.cars.count()


# ============================================
#  MODÈLE VOITURE (Modifié)
# ============================================
class Car(models.Model):
    CATEGORY_CHOICES = [
        ('economique', 'Économique'),
        ('confort', 'Confort'),
        ('premium', 'Premium'),
        ('suv', 'SUV'),
    ]

    name = models.CharField(max_length=100, verbose_name="Nom du véhicule")
    brand = models.CharField(max_length=50, verbose_name="Marque (texte)")
    brand_ref = models.ForeignKey(
        Brand, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='cars', verbose_name="Marque"
    )
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
    license_plate = models.CharField(max_length=20, blank=True, verbose_name="Immatriculation")
    year = models.PositiveIntegerField(null=True, blank=True, verbose_name="Année")
    mileage = models.PositiveIntegerField(default=0, verbose_name="Kilométrage")
    color = models.CharField(max_length=50, blank=True, verbose_name="Couleur")
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
        return f"{self.get_brand_display()} {self.name}"

    def get_brand_display(self):
        """Returns the brand name from FK if available, else the text field."""
        if self.brand_ref:
            return self.brand_ref.name
        return self.brand

    def get_image_url(self):
        """Returns the image URL, preferring uploaded image over URL field."""
        if self.image:
            return self.image.url
        return self.image_url or ''


# ============================================
#  MODÈLE CLIENT
# ============================================
class Client(models.Model):
    full_name = models.CharField(max_length=200, verbose_name="Nom complet")
    cin = models.CharField(max_length=20, unique=True, verbose_name="CIN")
    drivers_license = models.CharField(max_length=50, blank=True, verbose_name="Permis de conduire")
    phone = models.CharField(max_length=20, verbose_name="Téléphone")
    email = models.EmailField(blank=True, verbose_name="Email")
    address = models.TextField(blank=True, verbose_name="Adresse")
    city = models.CharField(max_length=100, blank=True, verbose_name="Ville")
    cin_front = models.ImageField(upload_to='clients/cin/', blank=True, null=True, verbose_name="CIN Recto")
    cin_back = models.ImageField(upload_to='clients/cin/', blank=True, null=True, verbose_name="CIN Verso")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['full_name']

    def __str__(self):
        return f"{self.full_name} ({self.cin})"

    @property
    def total_rentals(self):
        return self.contracts.count()

    @property
    def total_spent(self):
        return sum(c.total_amount for c in self.contracts.filter(status='termine') if c.total_amount)


# ============================================
#  MODÈLE CONTRAT DE LOCATION
# ============================================
class RentalContract(models.Model):
    STATUS_CHOICES = [
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
        ('annule', 'Annulé'),
    ]

    contract_number = models.CharField(max_length=20, unique=True, verbose_name="N° de contrat", editable=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='contracts', verbose_name="Client")
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='contracts', verbose_name="Voiture")
    start_date = models.DateField(verbose_name="Date de début")
    end_date = models.DateField(verbose_name="Date de fin")
    price_per_day = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Prix par jour (MAD)")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant total (MAD)")
    deposit = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="Caution (MAD)")
    km_start = models.PositiveIntegerField(default=0, verbose_name="Km au départ")
    km_end = models.PositiveIntegerField(null=True, blank=True, verbose_name="Km au retour")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_cours', verbose_name="Statut")
    notes = models.TextField(blank=True, verbose_name="Notes / Observations")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Contrat de location"
        verbose_name_plural = "Contrats de location"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.contract_number} — {self.client.full_name}"

    @property
    def duration_days(self):
        """Calculates the rental duration in days."""
        if self.start_date and self.end_date:
            delta = self.end_date - self.start_date
            return max(delta.days, 1)
        return 0

    def save(self, *args, **kwargs):
        if not self.contract_number:
            self.contract_number = self._generate_contract_number()
        if self.start_date and self.end_date and self.price_per_day:
            self.total_amount = self.duration_days * self.price_per_day
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_contract_number():
        """Generates a unique contract number like SC-2026-0001."""
        year = timezone.now().year
        prefix = f"SC-{year}-"
        last_contract = RentalContract.objects.filter(
            contract_number__startswith=prefix
        ).order_by('-contract_number').first()

        if last_contract:
            last_num = int(last_contract.contract_number.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"{prefix}{new_num:04d}"


# ============================================
#  MODÈLE VISITE TECHNIQUE
# ============================================
class TechnicalInspection(models.Model):
    RESULT_CHOICES = [
        ('favorable', 'Favorable'),
        ('defavorable', 'Défavorable'),
    ]

    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='inspections', verbose_name="Voiture")
    inspection_date = models.DateField(verbose_name="Date de la visite")
    expiry_date = models.DateField(verbose_name="Date d'expiration")
    result = models.CharField(max_length=20, choices=RESULT_CHOICES, default='favorable', verbose_name="Résultat")
    center_name = models.CharField(max_length=200, blank=True, verbose_name="Centre de contrôle")
    cost = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="Coût (MAD)")
    document = models.FileField(upload_to='inspections/', blank=True, null=True, verbose_name="Document scanné")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Visite technique"
        verbose_name_plural = "Visites techniques"
        ordering = ['-expiry_date']

    def __str__(self):
        return f"Visite — {self.car} ({self.expiry_date})"

    @property
    def status(self):
        """Returns the status of the inspection."""
        today = datetime.date.today()
        if self.expiry_date < today:
            return 'expired'
        elif self.expiry_date <= today + datetime.timedelta(days=30):
            return 'expiring_soon'
        return 'valid'

    @property
    def status_label(self):
        labels = {
            'expired': 'Expiré',
            'expiring_soon': 'Expire bientôt',
            'valid': 'Valide',
        }
        return labels.get(self.status, '')


# ============================================
#  MODÈLE ASSURANCE
# ============================================
class Insurance(models.Model):
    TYPE_CHOICES = [
        ('tous_risques', 'Tous risques'),
        ('tiers', 'Tiers'),
        ('tiers_plus', 'Tiers+'),
        ('autre', 'Autre'),
    ]

    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='insurances', verbose_name="Voiture")
    company = models.CharField(max_length=200, verbose_name="Compagnie d'assurance")
    insurance_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='tous_risques', verbose_name="Type")
    policy_number = models.CharField(max_length=50, blank=True, verbose_name="N° de police")
    start_date = models.DateField(verbose_name="Date de début")
    expiry_date = models.DateField(verbose_name="Date d'expiration")
    annual_premium = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Prime annuelle (MAD)")
    document = models.FileField(upload_to='insurances/', blank=True, null=True, verbose_name="Document scanné")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Assurance"
        verbose_name_plural = "Assurances"
        ordering = ['-expiry_date']

    def __str__(self):
        return f"{self.company} — {self.car} ({self.get_insurance_type_display()})"

    @property
    def status(self):
        """Returns the status of the insurance."""
        today = datetime.date.today()
        if self.expiry_date < today:
            return 'expired'
        elif self.expiry_date <= today + datetime.timedelta(days=30):
            return 'expiring_soon'
        return 'valid'

    @property
    def status_label(self):
        labels = {
            'expired': 'Expiré',
            'expiring_soon': 'Expire bientôt',
            'valid': 'Valide',
        }
        return labels.get(self.status, '')


# ============================================
#  MODÈLE AVIS CLIENT
# ============================================
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


# ============================================
#  MODÈLE MESSAGE DE CONTACT
# ============================================
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
