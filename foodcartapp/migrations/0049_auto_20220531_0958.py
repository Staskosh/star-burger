# Generated by Django 3.2 on 2022-05-31 09:58

from django.db import migrations


def add_called_at_delivered_at_to_orders(apps, schema_editor):
    Order = apps.get_model('foodcartapp', 'Order')
    for order in Order.objects.all().iterator():
        order.called_at = None
        order.delivered_at = None
        order.save()


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0048_auto_20220531_0948'),
    ]

    operations = [
        migrations.RunPython(add_called_at_delivered_at_to_orders),
    ]
