# Generated by Django 3.2.8 on 2022-02-27 10:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('san_diego', '0026_alter_car_client'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='san_diego.client'),
        ),
    ]
