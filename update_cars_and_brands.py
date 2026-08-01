import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saoudcar.settings')
django.setup()

from core.models import Car, Brand

def run():
    print("Mise à jour des Marques...")
    
    # S'assurer que les marques existent
    dacia, _ = Brand.objects.get_or_create(name="Dacia", defaults={'country': 'Roumanie'})
    renault, _ = Brand.objects.get_or_create(name="Renault", defaults={'country': 'France'})
    hyundai, _ = Brand.objects.get_or_create(name="Hyundai", defaults={'country': 'Corée du Sud'})
    
    # Liste des voitures de la photo
    cars_data = [
        {"name": "Duster", "brand_ref": dacia, "brand": "Dacia", "license_plate": "19858-A-58", "category": "economique"},
        {"name": "Logan G", "brand_ref": dacia, "brand": "Dacia", "license_plate": "19323-A-58", "category": "economique"},
        {"name": "Logan N", "brand_ref": dacia, "brand": "Dacia", "license_plate": "19324-A-58", "category": "economique"},
        {"name": "Sandero B", "brand_ref": dacia, "brand": "Dacia", "license_plate": "19467-A-58", "category": "economique"},
        {"name": "Sandero V", "brand_ref": dacia, "brand": "Dacia", "license_plate": "19461-A-58", "category": "economique"},
        {"name": "i10", "brand_ref": hyundai, "brand": "Hyundai", "license_plate": "20346-A-58", "category": "economique"},
        {"name": "Clio 5", "brand_ref": renault, "brand": "Renault", "license_plate": "19968-A-58", "category": "economique"},
    ]
    
    allowed_plates = [car['license_plate'] for car in cars_data]
    
    # Supprimer les voitures qui ne sont pas dans la liste (seulement si elles ont une plaque, ou les supprimer toutes sauf celles de la liste)
    # Pour faire propre, on va supprimer toutes les voitures qui n'ont pas une plaque figurant dans la liste.
    deleted, _ = Car.objects.exclude(license_plate__in=allowed_plates).delete()
    print(f"Voitures obsolètes supprimées : {deleted}")
    
    # Mettre à jour ou créer les voitures
    for c_data in cars_data:
        car, created = Car.objects.update_or_create(
            license_plate=c_data["license_plate"],
            defaults={
                "name": c_data["name"],
                "brand_ref": c_data["brand_ref"],
                "brand": c_data["brand"],
                "category": c_data["category"],
                # Mettre un prix par jour par défaut si la voiture est créée
                **({"price_per_day": 250.00} if Car.objects.filter(license_plate=c_data["license_plate"]).count() == 0 else {})
            }
        )
        if created:
            print(f"Ajouté : {car.brand} {car.name} ({car.license_plate})")
        else:
            print(f"Mis à jour : {car.brand} {car.name} ({car.license_plate})")

    print("Mise à jour terminée avec succès !")

if __name__ == "__main__":
    run()
