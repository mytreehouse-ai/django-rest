from django.contrib import admin
from .models.property_model import PropertyModel


@admin.register(PropertyModel)
class PropertyModelAdmin(admin.ModelAdmin):
    list_display = (
        "id", "lot_size", "floor_size", "building_size", "num_bedrooms",
        "num_bathrooms", "num_carspaces", "address_line1", "address_line2",
        "city", "region", "central_business_district", "longitude", "latitude",
        "year_built", "description", "created_at", "updated_at"
    )
    search_fields = (
        "address_line1", "address_line2", "city__name", "description"
    )
