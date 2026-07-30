from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Pages publiques
    path('', views.home, name='home'),
    path('vehicules/', views.cars, name='cars'),
    path('a-propos/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('avis/', views.submit_review, name='submit_review'),

    # Dashboard admin personnalisé
    path('admin/', views.admin_dashboard, name='admin_dashboard'),

    # Voitures
    path('admin/voitures/', views.admin_cars, name='admin_cars'),
    path('admin/voitures/ajouter/', views.admin_car_add, name='admin_car_add'),
    path('admin/voitures/<int:car_id>/modifier/', views.admin_car_edit, name='admin_car_edit'),
    path('admin/voitures/<int:car_id>/supprimer/', views.admin_car_delete, name='admin_car_delete'),
    path('admin/voitures/<int:car_id>/featured/', views.admin_car_toggle_featured, name='admin_car_toggle_featured'),

    # Marques
    path('admin/marques/', views.admin_brands, name='admin_brands'),
    path('admin/marques/ajouter/', views.admin_brand_add, name='admin_brand_add'),
    path('admin/marques/<int:brand_id>/modifier/', views.admin_brand_edit, name='admin_brand_edit'),
    path('admin/marques/<int:brand_id>/supprimer/', views.admin_brand_delete, name='admin_brand_delete'),

    # Clients
    path('admin/clients/', views.admin_clients, name='admin_clients'),
    path('admin/clients/ajouter/', views.admin_client_add, name='admin_client_add'),
    path('admin/clients/<int:client_id>/modifier/', views.admin_client_edit, name='admin_client_edit'),
    path('admin/clients/<int:client_id>/supprimer/', views.admin_client_delete, name='admin_client_delete'),

    # Contrats
    path('admin/contrats/', views.admin_contracts, name='admin_contracts'),
    path('admin/contrats/ajouter/', views.admin_contract_add, name='admin_contract_add'),
    path('admin/contrats/<int:contract_id>/modifier/', views.admin_contract_edit, name='admin_contract_edit'),
    path('admin/contrats/<int:contract_id>/supprimer/', views.admin_contract_delete, name='admin_contract_delete'),
    path('admin/contrats/<int:contract_id>/pdf/', views.admin_contract_pdf, name='admin_contract_pdf'),
    path('admin/contrats/export/csv/', views.admin_contracts_export_csv, name='admin_contracts_export_csv'),
    path('admin/contrats/export/excel/', views.admin_contracts_export_excel, name='admin_contracts_export_excel'),

    # Visites techniques
    path('admin/visites/', views.admin_inspections, name='admin_inspections'),
    path('admin/visites/ajouter/', views.admin_inspection_add, name='admin_inspection_add'),
    path('admin/visites/<int:inspection_id>/modifier/', views.admin_inspection_edit, name='admin_inspection_edit'),
    path('admin/visites/<int:inspection_id>/supprimer/', views.admin_inspection_delete, name='admin_inspection_delete'),

    # Assurances
    path('admin/assurances/', views.admin_insurances, name='admin_insurances'),
    path('admin/assurances/ajouter/', views.admin_insurance_add, name='admin_insurance_add'),
    path('admin/assurances/<int:insurance_id>/modifier/', views.admin_insurance_edit, name='admin_insurance_edit'),
    path('admin/assurances/<int:insurance_id>/supprimer/', views.admin_insurance_delete, name='admin_insurance_delete'),

    # Avis
    path('admin/avis/', views.admin_reviews, name='admin_reviews'),
    path('admin/avis/<int:review_id>/approuver/', views.admin_review_approve, name='admin_review_approve'),
    path('admin/avis/<int:review_id>/supprimer/', views.admin_review_delete, name='admin_review_delete'),

    # Messages
    path('admin/messages/', views.admin_messages, name='admin_messages'),
    path('admin/messages/<int:msg_id>/lu/', views.admin_message_read, name='admin_message_read'),
    path('admin/messages/<int:msg_id>/supprimer/', views.admin_message_delete, name='admin_message_delete'),
]
