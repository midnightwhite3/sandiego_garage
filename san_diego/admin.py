from django.contrib import admin

from .models import Car, CarMake, CarModel, Client, Service, CarPart
# Register your models here.

admin.site.register(CarMake)
admin.site.register(CarModel)
admin.site.register(Client)


class ServiceAdmin(admin.ModelAdmin):
    list_display = [
        'car',
        'user',
        'service_name',
        'service_price',
        'date_added',
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


class CarPartAdmin(admin.ModelAdmin):
    list_display = [
        'car',
        'user',
        'car_part',
        'part_price',
        'pdate_added',
    ]


admin.site.register(CarPart, CarPartAdmin)
admin.site.register(Car, CarAdmin)
admin.site.register(Service, ServiceAdmin)