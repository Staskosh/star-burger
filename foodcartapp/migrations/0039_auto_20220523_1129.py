# Generated by Django 3.2 on 2022-05-23 11:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0038_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='product',
        ),
        migrations.RemoveField(
            model_name='order',
            name='quantity',
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(verbose_name='Количество')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product', to='foodcartapp.product', verbose_name='продукт')),
            ],
            options={
                'verbose_name': 'пункт заказа',
                'verbose_name_plural': 'пункты заказа',
            },
        ),
    ]
