from django.db import models
from django.utils import timezone
import datetime
import uuid


# ============================================
#  MODÈLE MARQUE
# ============================================
class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom de la marque")
    logo = models.ImageField(upload_to='brands/', blank=True, null=True, verbose_name="Logo")
    logo_url = models.URLField(blank=True, verbose_name="URL du Logo")
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

    def get_logo_url(self):
        """Returns the logo URL, preferring uploaded image over URL field."""
        if self.logo:
            try:
                return self.logo.url
            except ValueError:
                return self.logo_url or ''
        return self.logo_url or ''


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
    expected_return_date = models.DateField(null=True, blank=True, verbose_name="Date de retour prévue")
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
    GENDER_CHOICES = [
        ('homme', 'Homme'),
        ('femme', 'Femme'),
    ]

    # Informations personnelles
    full_name = models.CharField(max_length=200, verbose_name="Nom complet")
    first_name = models.CharField(max_length=100, blank=True, verbose_name="Prénom")
    last_name = models.CharField(max_length=100, blank=True, verbose_name="Nom")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, verbose_name="Genre")
    birth_date = models.DateField(blank=True, null=True, verbose_name="Date de naissance")
    nationality = models.CharField(max_length=100, blank=True, default="Marocaine", verbose_name="Nationalité")

    # Pièces d'identité & Permis
    cin = models.CharField(max_length=20, unique=True, verbose_name="N° CIN")
    cin_expiry = models.DateField(blank=True, null=True, verbose_name="Valable jusqu'au (CIN)")
    passport_number = models.CharField(max_length=50, blank=True, verbose_name="N° Passeport")
    passport_expiry = models.DateField(blank=True, null=True, verbose_name="Valable jusqu'au (Passeport)")
    drivers_license = models.CharField(max_length=50, blank=True, verbose_name="N° Permis")
    license_delivered = models.DateField(blank=True, null=True, verbose_name="Délivré le")

    # Coordonnées
    phone = models.CharField(max_length=20, verbose_name="Téléphone")
    email = models.EmailField(blank=True, verbose_name="Email")
    address = models.TextField(blank=True, verbose_name="Adresse")
    city = models.CharField(max_length=100, blank=True, verbose_name="Ville")
    country = models.CharField(max_length=100, blank=True, default="Maroc", verbose_name="Pays")

    # Pièces jointes
    cin_front = models.ImageField(upload_to='clients/cin/', blank=True, null=True, verbose_name="CIN Recto")
    cin_back = models.ImageField(upload_to='clients/cin/', blank=True, null=True, verbose_name="CIN Verso")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['full_name']

    def __str__(self):
        return f"{self.full_name} ({self.cin})"

    def save(self, *args, **kwargs):
        # Auto-fill full_name from first_name + last_name if they are set
        if self.first_name and self.last_name:
            self.full_name = f"{self.last_name} {self.first_name}"
        super().save(*args, **kwargs)

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

    # Signatures
    director_signature = models.ImageField(upload_to='signatures/', blank=True, null=True, verbose_name="Signature directeur")
    client_signature = models.ImageField(upload_to='signatures/', blank=True, null=True, verbose_name="Signature client")
    signature_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, verbose_name="Token de signature")
    client_signed_at = models.DateTimeField(blank=True, null=True, verbose_name="Date signature client")

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


# ============================================
#  MODÈLE PARAMÈTRES AGENCE
# ============================================

DEFAULT_CONDITIONS = """Article 1 – État du véhicule
Le véhicule est remis au locataire en parfait état de marche.
Le locataire doit vérifier immédiatement l’état du véhicule ainsi que les accessoires fournis (roue de secours, outils, etc.).
Le véhicule doit être restitué dans le même état que celui constaté lors de la remise.

Le locataire doit :
Ne faire aucune modification au véhicule.
Retourner le véhicule propre.
Respecter la limite de 200 km par jour, sauf accord contraire.
S’assurer que le compteur reste lisible et intact.
Tout dommage non signalé lors du retour sera à la charge du locataire.

Article 2 – Utilisation du véhicule
La location est personnelle et non transmissible.
Le locataire s’engage à :
Utiliser le véhicule uniquement pour ses besoins personnels.
Respecter le code de la route.
Ne permettre la conduite qu’aux conducteurs autorisés et mentionnés au contrat.
Il est strictement interdit de :
Transporter des marchandises contre rémunération.
Utiliser le véhicule pour des courses, rallyes ou compétitions.
Transporter des objets dangereux.
Utiliser le véhicule pour pousser un autre véhicule.
Faire du remorquage.
Toute utilisation contraire engage la responsabilité totale du locataire.

Article 3 – Carburant et lubrifiants
Le carburant est entièrement à la charge du locataire.
Le locataire doit contrôler régulièrement :
Les niveaux d’huile
Le liquide de frein
Le liquide de refroidissement
Les frais de graissage et d’entretien courant sont à la charge du locataire.
Il devra fournir des factures justifiant les opérations effectuées (avec indication du kilométrage).

Article 4 – Entretien et réparations
Les réparations dues à l’usure normale sont à la charge du loueur.
Les réparations dues à une mauvaise utilisation, un accident ou une négligence sont à la charge du locataire.
Le locataire ne peut effectuer aucune réparation sans autorisation préalable du loueur, sauf en cas d’urgence.
Toute immobilisation du véhicule causée par une mauvaise utilisation entraîne une indemnité.

Article 5 – Assurance et accident
L’assurance couvre :
Les dommages causés au véhicule conformément au contrat.
La responsabilité civile obligatoire.
Le locataire reste responsable :
Des dommages résultant d’une mauvaise utilisation.
Des vols causés par négligence (véhicule non fermé, clés laissées à l’intérieur).
Des objets personnels transportés.
En cas d’accident :
Le locataire doit informer immédiatement la société.
Remplir un constat amiable.
Fournir les coordonnées des témoins éventuels.

Article 6 – Règlement – Prépaiement – Prolongation
Le prépaiement sert uniquement à réserver la location.
Toute prolongation doit être validée et réglée auprès de la société.
Les frais supplémentaires (carburant, retards, dommages, jours ajoutés) sont à la charge du locataire.
La société se réserve le droit de récupérer le véhicule à tout moment en cas de non-respect du contrat.

Article 7 – Documents du véhicule
Le locataire doit restituer :
La carte grise
L’assurance
Les clés
Les documents du véhicule
En cas de perte, les frais de duplicata seront à la charge du locataire.

Article 8 – Responsabilité
Le locataire est responsable :
De toute amende ou infraction commise durant la location.
Des dommages causés au véhicule non couverts par l’assurance.
De la perte d’objets ou d’accessoires fournis.

Article 9 – Juridiction
En cas de litige, les tribunaux compétents seront ceux du lieu de signature du contrat."""

class AgencyInfo(models.Model):
    name = models.CharField(max_length=100, default="SAOUD CAR", verbose_name="Raison Sociale")
    email = models.EmailField(default="saoud88000@gmail.com", verbose_name="Email")
    phone_mobile = models.CharField(max_length=20, default="+212661395495", verbose_name="Téléphone mobile")
    phone_fixed = models.CharField(max_length=20, default="+212523290058", verbose_name="Téléphone fixe")
    address = models.TextField(default="Citee Lalla Meriem Bloc B N 185", verbose_name="Adresse")
    city = models.CharField(max_length=50, default="BENSLIMANE", verbose_name="Ville")
    zip_code = models.CharField(max_length=20, default="13000", verbose_name="Code postal")
    country = models.CharField(max_length=50, default="Maroc", verbose_name="Pays")
    website = models.CharField(max_length=100, blank=True, verbose_name="Site Web")
    
    # Infos Légales
    ice = models.CharField(max_length=50, default="000058659000023", verbose_name="ICE")
    patente = models.CharField(max_length=50, default="39715439", verbose_name="Patente")
    rc = models.CharField(max_length=50, default="2713", verbose_name="RC")
    if_tax = models.CharField(max_length=50, default="40 39 14 74", verbose_name="IF")
    cnss = models.CharField(max_length=50, default="8744080", verbose_name="CNSS")
    tva = models.PositiveIntegerField(default=20, verbose_name="TVA (%)")

    # Identité Visuelle et Contrat
    conditions_generales = models.TextField(default=DEFAULT_CONDITIONS, verbose_name="Conditions Générales")
    logo = models.ImageField(upload_to='agency/', blank=True, null=True, verbose_name="Logo")
    stamp = models.ImageField(upload_to='agency/', blank=True, null=True, verbose_name="Cachet")
    show_stamp_on_contract = models.BooleanField(default=True, verbose_name="Afficher Sur le Contrat")
    show_stamp_on_invoice = models.BooleanField(default=True, verbose_name="Afficher Sur la Facture")

    class Meta:
        verbose_name = "Informations de l'agence"
        verbose_name_plural = "Informations de l'agence"

    def __str__(self):
        return self.name

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(id=1)
        return obj


# ============================================
#  MODÈLE VIDANGE (ENTRETIEN)
# ============================================
class Maintenance(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='maintenances', verbose_name="Voiture")
    date = models.DateField(default=timezone.now, verbose_name="Date")
    current_mileage = models.PositiveIntegerField(verbose_name="Kilométrage actuel")
    next_mileage = models.PositiveIntegerField(verbose_name="Prochaine vidange (Km)")
    cost = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="Coût (MAD)")
    notes = models.TextField(blank=True, verbose_name="Notes / Observations")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Vidange / Entretien"
        verbose_name_plural = "Vidanges / Entretiens"
        ordering = ['-date']

    def __str__(self):
        return f"Vidange - {self.car} ({self.date})"


# ============================================
#  MODÈLE RÉSERVATION
# ============================================
class Reservation(models.Model):
    STATUS_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirmee', 'Confirmée'),
        ('annulee', 'Annulée'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='reservations', verbose_name="Client")
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='reservations', verbose_name="Voiture")
    start_date = models.DateField(verbose_name="Date de début")
    end_date = models.DateField(verbose_name="Date de fin")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_attente', verbose_name="Statut")
    notes = models.TextField(blank=True, verbose_name="Notes / Observations")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Réservation"
        verbose_name_plural = "Réservations"
        ordering = ['-created_at']

    def __str__(self):
        return f"Réservation {self.id} — {self.client.full_name} ({self.car})"
