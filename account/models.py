from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
# Create your models here.

User._meta.get_field('email')._unique = True # This is for setting e-mail field of User model to unique

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    logo = models.ImageField(blank=True)
    company_name = models.CharField(max_length=40, blank=True)
    company_adress = models.CharField(max_length=60, blank=True)
    post_code_city = models.CharField(max_length=30, blank=True)
    phone_number = models.CharField(max_length=9, blank=True)
    nip = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return f"{self.user.username} profile."