from django.db import models
from domain.models.base_model import BaseModel


class PropertyStatusModel(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    description = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Description"
    )
    slug = models.CharField(
        max_length=200,
        verbose_name="Slug",
        null=True,
        unique=True
    )

    def __str__(self) -> str:
        return self.description

    class Meta:
        db_table = "property_statuses"
        verbose_name = "Property status"
        verbose_name_plural = "Property statuses"
        ordering = ["-id"]
