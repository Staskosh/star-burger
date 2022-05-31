# Generated by Django 3.2 on 2022-05-31 07:21

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0045_auto_20220530_0725'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Unprocessed', 'Необработанный'), ('In_procces', 'В работе'), ('Сompleted', 'Завершен')], default='Unprocessed', max_length=15, verbose_name='Статус заказа'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Стоимость позиции заказа'),
        ),
    ]
