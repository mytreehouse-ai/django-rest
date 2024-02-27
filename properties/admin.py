from django.contrib import admin

from .models.property_model import PropertyModel
from .models.property_type_model import PropertyTypeModel
from .models.listing_type_model import ListingTypeModel
from .models.property_status_model import PropertyStatusModel


@admin.register(PropertyModel)
class PropertyModelAdmin(admin.ModelAdmin):
    list_display = (
        "id", "building_name", "subdivision_name", "lot_size", "floor_size",
        "building_size", "num_bedrooms", "num_bathrooms", "num_carspaces",
        "address_line1", "address_line2", "city", "region",
        "central_business_district", "longitude", "latitude", "year_built",
        "description", "created_at", "updated_at"
    )
    search_fields = (
        "building_name", "subdivision_name", "address_line1", "address_line2",
        "city__name", "description"
    )


@admin.register(PropertyTypeModel)
class PropertyTypeModelAdmin(admin.ModelAdmin):
    list_display = ("id", "description")
    search_fields = ("description",)


@admin.register(ListingTypeModel)
class ListingTypeModelAdmin(admin.ModelAdmin):
    list_display = ("id", "description")
    search_fields = ("description",)


@admin.register(PropertyStatusModel)
class PropertyStatusModelAdmin(admin.ModelAdmin):
    list_display = ("id", "description")
    search_fields = ("description",)
