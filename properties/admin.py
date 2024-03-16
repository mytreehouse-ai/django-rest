from django.contrib import admin

from .models.property_model import PropertyModel
from .models.property_listing_model import PropertyListingModel
from .models.property_type_model import PropertyTypeModel
from .models.listing_type_model import ListingTypeModel
from .models.property_status_model import PropertyStatusModel
from .models.price_history_model import PriceHistoryModel


@admin.register(PropertyListingModel)
class PropertyListingModelAdmin(admin.ModelAdmin):
    list_display = (
        "id", "listing_title", "listing_url", "price",
        "is_delisted", "is_active", "created_at", "updated_at"
    )
    search_fields = (
        "listing_title", "listing_url"
    )


@admin.register(PropertyModel)
class PropertyModelAdmin(admin.ModelAdmin):
    list_display = (
        "id", "building_name", "subdivision_name", "lot_size", "floor_size",
        "building_size", "num_bedrooms", "num_bathrooms", "num_carspaces",
        "address", "city", "longitude", "latitude", "image_url", "created_at",
        "updated_at"
    )
    search_fields = (
        "building_name", "subdivision_name", "address", "city__name", "description"
    )


@admin.register(PriceHistoryModel)
class PriceHistoryModelAdmin(admin.ModelAdmin):
    list_display = ("id", "price", "date_recorded", "created_at", "updated_at")
    search_fields = (
        "property_listing__listing_title",
        "property_listing__listing_url"
    )


@admin.register(PropertyTypeModel)
class PropertyTypeModelAdmin(admin.ModelAdmin):
    list_display = ("id", "description")
    search_fields = ("description",)


@admin.register(ListingTypeModel)
class ListingTypeModelAdmin(admin.ModelAdmin):
    list_display = ("id", "description", "slug")
    search_fields = ("description", "slug")


@admin.register(PropertyStatusModel)
class PropertyStatusModelAdmin(admin.ModelAdmin):
    list_display = ("id", "description", "slug")
    search_fields = ("description", "slug")
