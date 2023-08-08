from django.db import models
from trash_app.models import Organizations

# Create your models here.


class ClientsIpAddresses(models.Model):
    ip = models.CharField(max_length=100, verbose_name="Ip-адрес")

    def __str__(self) -> str:
        return self.ip

    class Meta:
        verbose_name = "Ip-адрес"
        verbose_name_plural = "Ip-адреса"


class Coordinates(models.Model):
    coordinates = models.ForeignKey(
        Organizations,
        on_delete=models.CASCADE,
        related_name="organizations_coordinates",
        verbose_name="Координаты организации",
    )

    latitude_coordinate = models.FloatField("Широта (координата)")
    longitude_coordinate = models.FloatField("Долгота (координата)")

    def __str__(self) -> str:
        return str(self.coordinates)

    class Meta:
        verbose_name = "Координата"
        verbose_name_plural = "Координаты"
        ordering = ["id"]
