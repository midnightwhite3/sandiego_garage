# Generated by Django 3.2.8 on 2022-02-13 16:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('san_diego', '0009_auto_20220213_1640'),
    ]

    operations = [
        migrations.RenameField(
            model_name='carpart',
            old_name='date_added',
            new_name='pdate_added',
        ),
    ]
