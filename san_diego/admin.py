from django.contrib import admin

from .models import Car, CarMake, CarModel, Client, Service, CarParts
# Register your models here.

admin.site.register(CarMake)
admin.site.register(CarModel)
admin.site.register(Client)

class PartsInLine(admin.TabularInline):
    model = CarParts


class ServiceAdmin(admin.ModelAdmin):
    inlines = [PartsInLine]
    extra = 0
    list_display = [
        'car',
        'user',
        'service_name',
        'service_price',
    ]


class CarAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'client',
        'car_make',
        'car_model',
        'year',
    ]
    readonly_fields = ['user', 'date_added', 'date_updated']
    raw_id_fields = ['user']

admin.site.register(Car, CarAdmin)
admin.site.register(Service, ServiceAdmin)