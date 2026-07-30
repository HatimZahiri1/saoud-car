from core.models import Car, Brand

def populate_brands():
    # Récupérer toutes les marques uniques (en ignorant la casse si possible, mais on va juste prendre distinct)
    unique_brands = Car.objects.values_list('brand', flat=True).distinct()
    
    print("Marques trouvées dans les véhicules :", list(unique_brands))
    
    for brand_name in unique_brands:
        if brand_name and brand_name.strip():
            b_name = brand_name.strip()
            # Créer la marque si elle n'existe pas
            brand_obj, created = Brand.objects.get_or_create(name=b_name)
            if created:
                print(f"✅ Nouvelle marque créée : {b_name}")
            else:
                print(f"ℹ️ La marque {b_name} existe déjà.")
            
            # Lier les voitures existantes à cette nouvelle marque
            cars_to_update = Car.objects.filter(brand=brand_name, brand_ref__isnull=True)
            count = cars_to_update.update(brand_ref=brand_obj)
            if count > 0:
                print(f"   -> {count} voiture(s) liée(s) à la marque {b_name}")

populate_brands()
