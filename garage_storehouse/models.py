from django.db import models
from django.utils.translation import gettext_lazy as _
from san_diego.models import CarMake, CarModel
from django.conf import settings

# Create your models here.

class CarPart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='storehouse_carpart')
    part_name = models.CharField(max_length=50, verbose_name=_('Name'))
    part_id_number = models.CharField(max_length=20, null=True, blank=True, verbose_name=_('ID number'))
    car_make = models.ForeignKey(CarMake,on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Car make'))
    car_model = models.ForeignKey(CarModel, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Car model'))
    quantity = models.IntegerField(verbose_name=_('Quantity'))
    date_added = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)

    def __str__(self):
        return self.part_name


    class Meta:
        ordering = ('-date_updated',)
