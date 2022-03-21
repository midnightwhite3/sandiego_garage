from django.db import models
from django.conf import settings
from shortuuid.django_fields import ShortUUIDField
from django.core.validators import MinLengthValidator, MinValueValidator, MaxValueValidator
import datetime
from django.utils.translation import gettext_lazy as _
# Create your models here.

class CarMake(models.Model):
    car_make = models.CharField(max_length=30, verbose_name=_('Make'))

    def __str__(self):
        return f"{self.car_make}"

class CarModel(models.Model):
    make = models.ForeignKey(CarMake, max_length=30, verbose_name='Make', on_delete=models.CASCADE)
    make_name = models.CharField(max_length=30)
    model_name = models.CharField(max_length=30, verbose_name='Model')

    def __str__(self):
        return self.model_name

class Client(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    client_name = models.CharField(max_length=40, verbose_name=_('Name'))
    phone_number = models.CharField(_('Phone number'),max_length=9, null=True, blank=True)
    uuid = ShortUUIDField(length=12, max_length=20, editable=False, unique=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.client_name

    class Meta:
        ordering = ('-id',)


class Car(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    FUEL = (
        ('', '---------'),
        ('Gasoline', _('Gasoline')),
        ('Diesel', 'Diesel'),
        ('Electric', _('Electric')),
        ('Hybrid', _('Hybrid')),
        ('PB+LPG', 'PB+LPG')
    )
    
    client = models.ForeignKey(Client,on_delete=models.CASCADE, verbose_name=_('Client'))
    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE, verbose_name=_('Car make'))
    car_model = models.ForeignKey(CarModel, on_delete=models.CASCADE, verbose_name=_('Car model'))
    year = models.IntegerField(_('Year'),default=None, null=True, blank=True, validators=[
        MinValueValidator(1950, _("Enter a valid year.")), MaxValueValidator(2050, "Enter a valid year.")])
    fuel_type = models.CharField(_('Fuel type'),max_length=15, choices=FUEL, default=None, null=True, blank=True)
    engine = models.CharField(_('Engine'),null=True, blank=True, max_length=15)
    vin = models.CharField(max_length=17, blank=True, null=True, validators=[
        MinLengthValidator(17, _("This VIN number is too short."))])
    extra_info = models.TextField(max_length=300, verbose_name=_('Remarks'), null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    uuid = ShortUUIDField(length=12, max_length=20, editable=False, unique=True)

    def __str__(self):
        return f"{self.client} | {self.car_make} {self.car_model}"
    
    class Meta:
        ordering = ('-date_updated',)
    

class Service(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    service_name = models.CharField(max_length=100, verbose_name=_('Service'), default=None)
    service_price = models.DecimalField(_('Service price'),max_digits=20, decimal_places=2, default=None)
    date_added = models.DateField(default=datetime.date.today)

    def __str__(self):
        return self.service_name

    def save(self, *args, **kwargs):
        """Update parent model date_updated field whenever child object is added/edited"""
        self.car.save(update_fields=['date_updated'])
        super(Service, self).save(*args, **kwargs)


class CarPart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    car_part = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Part'))
    part_price = models.DecimalField(_('Part price'),max_digits=20, decimal_places=2, null=True, blank=True)
    pdate_added = models.DateField(default=datetime.date.today)

    def __str__(self):
        return f"Part: {self.car_part}  Price: {self.part_price}"
    