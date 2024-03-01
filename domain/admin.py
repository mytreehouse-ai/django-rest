from django.contrib import admin

from .models.city_model import CityModel


@admin.register(CityModel)
class CityModelModel(admin.ModelAdmin):
    list_display = (
        "id", "name", "created_at", "updated_at"
    )
    search_fields = ("name",)
