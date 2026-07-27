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
    path('admin/voitures/', views.admin_cars, name='admin_cars'),
    path('admin/voitures/ajouter/', views.admin_car_add, name='admin_car_add'),
    path('admin/voitures/<int:car_id>/modifier/', views.admin_car_edit, name='admin_car_edit'),
    path('admin/voitures/<int:car_id>/supprimer/', views.admin_car_delete, name='admin_car_delete'),
    path('admin/voitures/<int:car_id>/featured/', views.admin_car_toggle_featured, name='admin_car_toggle_featured'),
    path('admin/avis/', views.admin_reviews, name='admin_reviews'),
    path('admin/avis/<int:review_id>/approuver/', views.admin_review_approve, name='admin_review_approve'),
    path('admin/avis/<int:review_id>/supprimer/', views.admin_review_delete, name='admin_review_delete'),
    path('admin/messages/', views.admin_messages, name='admin_messages'),
    path('admin/messages/<int:msg_id>/lu/', views.admin_message_read, name='admin_message_read'),
    path('admin/messages/<int:msg_id>/supprimer/', views.admin_message_delete, name='admin_message_delete'),
]
