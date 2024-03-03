from django.db import models
from domain.models.base_model import BaseModel


class CityModel(BaseModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name="Name"
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        db_table = "cities"
        verbose_name = "City"
        verbose_name_plural = "Cities"
        ordering = ["-id"]
        indexes = [
            models.Index(fields=['name'], name='name_idx'),
        ]
