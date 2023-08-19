from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=63, unique=True)

    class Meta:
        verbose_name_plural = "countries"

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=63)
    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        related_name="cities"
    )

    class Meta:
        verbose_name_plural = "cities"

    def __str__(self):
        return self.name
