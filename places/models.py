from django.db import models
from django.utils.timezone import now


class Place(models.Model):
    address = models.CharField(
        'Адрес',
        max_length=200,
        unique=True
    )
    lon = models.FloatField(
        'Долгота',
        null=True,
        blank=True
    )
    lat = models.FloatField(
        'Широта',
        null=True,
        blank=True
    )
    saved_at = models.DateTimeField(
        'Время сохранения места в дб',
        default=now,
        db_index=True
    )

    class Meta:
        verbose_name = 'место'
        verbose_name_plural = 'места'

    def __str__(self):
        return self.address
