from django.db import models
from domain.models.base_model import BaseModel


class PropertyModel(BaseModel):
    id = models.AutoField(primary_key=True)
    lot_size = models.FloatField(null=True, verbose_name="Lot Size")
    floor_size = models.FloatField(null=True, verbose_name="Floor Size")
    building_size = models.FloatField(null=True, verbose_name="Building Size")
    num_bedrooms = models.IntegerField(
        default=0,
        verbose_name="Number of Bedrooms"
    )
    num_bathrooms = models.IntegerField(
        default=0,
        verbose_name="Number of Bathrooms"
    )
    num_carspaces = models.IntegerField(
        default=0,
        verbose_name="Number of Car Spaces"
    )
    address_line1 = models.CharField(
        max_length=255,
        null=True,
        verbose_name="Address Line 1"
    )
    address_line2 = models.CharField(
        max_length=255,
        null=True,
        verbose_name="Address Line 2"
    )
    city = models.ForeignKey(
        "domain.CityModel",
        null=True,
        related_name="city",
        on_delete=models.SET_NULL,
        verbose_name="City"
    )
    region = models.CharField(
        max_length=200,
        null=True,
        db_index=True,
        verbose_name="Region"
    )
    central_business_district = models.BooleanField(
        default=False,
        verbose_name="Central Business District"
    )
    longitude = models.FloatField(null=True, verbose_name="Longitude")
    latitude = models.FloatField(null=True, verbose_name="Latitude")
    year_built = models.IntegerField(null=True, verbose_name="Year Built")
    description = models.TextField(null=True, verbose_name="Description")

    def __str__(self) -> str:
        return str(self.id)

    class Meta:
        db_table = "properties"
        verbose_name = "Property"
        verbose_name_plural = "Properties"
        ordering = ["-id"]
