# Generated by Django 3.2 on 2022-05-31 09:48
from datetime import datetime

from django.db import migrations


def add_registered_at_to_orders(apps, schema_editor):
    Order = apps.get_model('foodcartapp', 'Order')
    for order in Order.objects.all():
        order.registered_at = datetime.now()
        order.save()

class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0047_auto_20220531_0929'),
    ]

    operations = [
        migrations.RunPython(add_registered_at_to_orders),
    ]
