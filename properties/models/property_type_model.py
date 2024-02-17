from django.db import models
from domain.models.base_model import BaseModel


class PropertyTypeModel(BaseModel):
    id = models.AutoField(primary_key=True)
    description = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Description"
    )

    def __str__(self) -> str:
        return self.description

    class Meta:
        db_table = "property_types"
        verbose_name = "Property type"
        verbose_name_plural = "Property types"
        ordering = ["-id"]
