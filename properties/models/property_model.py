from django.db import models
from domain.models.base_model import BaseModel


class PropertyModel(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    building_name = models.CharField(
        null=True,
        blank=True,
        max_length=200,
        verbose_name="Building Name"
    )
    subdivision_name = models.CharField(
        null=True,
        blank=True,
        max_length=200,
        verbose_name="Subdivision Name"
    )
    address = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name="Address"
    )
    lot_size = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Lot Size"
    )
    floor_size = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Floor Size"
    )
    building_size = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Building Size"
    )
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
    city = models.ForeignKey(
        "domain.CityModel",
        null=True,
        blank=True,
        related_name="city",
        on_delete=models.SET_NULL,
        verbose_name="City"
    )
    longitude = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Longitude"
    )
    latitude = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Latitude"
    )
    image_url = models.URLField(
        null=True,
        blank=True,
        verbose_name="Image URL"
    )
    indoor_features = models.JSONField(
        default=list,
        null=True,
        blank=True,
        verbose_name="Indoor Features"
    )
    outdoor_features = models.JSONField(
        default=list,
        null=True,
        blank=True,
        verbose_name="Outdoor Features"
    )
    other_features = models.JSONField(
        default=list,
        null=True,
        blank=True,
        verbose_name="Other Features"
    )
    description = models.TextField(
        null=True,
        blank=True,
        db_index=False,
        verbose_name="Description"
    )
    markdown = models.TextField(
        null=True,
        blank=True,
        verbose_name="Markdown"
    )
    metadata = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Other Details"
    )

    def __str__(self) -> str:
        if self.building_name or self.subdivision_name:
            return self.building_name if self.building_name else self.subdivision_name
        return str(self.id)

    class Meta:
        db_table = "properties"
        verbose_name = "Property"
        verbose_name_plural = "Properties"
        ordering = ["-id"]
