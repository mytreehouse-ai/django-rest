from django.db import models
from domain.models.base_model import BaseModel


class PropertyListingModel(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    listing_title = models.TextField(
        unique=True,
        verbose_name="Listing Title"
    )
    listing_url = models.URLField(
        unique=True,
        verbose_name="Listing URL"
    )
    estate = models.OneToOneField(
        "PropertyModel",
        null=True,
        related_name="estate_listing",
        on_delete=models.CASCADE,
        verbose_name="Estate"
    )
    property_type = models.ForeignKey(
        "PropertyTypeModel",
        null=True,
        blank=True,
        related_name="property_type",
        on_delete=models.CASCADE,
        verbose_name="Property Type"
    )
    listing_type = models.ForeignKey(
        "ListingTypeModel",
        null=True,
        blank=True,
        related_name="listing_type",
        on_delete=models.SET_NULL,
        verbose_name="Listing Type"
    )
    property_status = models.ForeignKey(
        "PropertyStatusModel",
        null=True,
        blank=True,
        related_name="property_status",
        on_delete=models.SET_NULL,
        verbose_name="Property Status"
    )
    price = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0.00,
        verbose_name="Price"
    )
    price_formatted = models.CharField(
        null=True,
        blank=True,
        max_length=200,
        verbose_name="Price Formatted"
    )
    is_delisted = models.BooleanField(
        default=False,
        verbose_name="Is Delisted"
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name="Is Active"
    )
    is_in_vector_table = models.BooleanField(
        default=False,
        verbose_name="Is In Vector Table"
    )
    vector_uuids = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Vector UUIDs"
    )

    def __str__(self) -> str:
        return self.listing_title

    class Meta:
        db_table = "property_listings"
        verbose_name = "Property listing"
        verbose_name_plural = "Property listings"
        ordering = ["-id"]
