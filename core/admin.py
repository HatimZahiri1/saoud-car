from django.contrib import admin
from .models import Car, ContactMessage

admin.site.site_header = "Dashboard SAOUD CAR"
admin.site.site_title = "Administration SAOUD CAR"
admin.site.index_title = "Gestion du site SAOUD CAR"


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'price_per_day', 'is_available')
    list_filter = ('category', 'is_available', 'transmission', 'fuel_type')
    search_fields = ('name', 'brand')
    list_editable = ('is_available', 'price_per_day')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject')
    list_editable = ('is_read',)
    readonly_fields = ('created_at',)
