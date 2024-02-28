from django.db import models
from domain.models.base_model import BaseModel


class PriceHistoryModel(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    property_listing = models.ForeignKey(
        "PropertyListingModel",
        related_name="price_histories",
        on_delete=models.CASCADE,
        verbose_name="Property Listing"
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Price"
    )
    date_recorded = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date Recorded"
    )

    def __str__(self) -> str:
        return f"{self.property_listing} - {self.price} on {self.date_recorded}"

    class Meta:
        db_table = "price_histories"
        verbose_name = "Price History"
        verbose_name_plural = "Price Histories"
        ordering = ["-date_recorded"]
