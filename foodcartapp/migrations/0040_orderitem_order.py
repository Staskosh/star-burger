# Generated by Django 3.2 on 2022-05-23 12:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0039_auto_20220523_1129'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='order',
            field=models.ForeignKey(default='1', on_delete=django.db.models.deletion.CASCADE, related_name='order', to='foodcartapp.order', verbose_name='заказ'),
            preserve_default=False,
        ),
    ]
