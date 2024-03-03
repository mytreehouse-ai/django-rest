from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin

from .models.user_model import User
from .models.city_model import CityModel

admin.site.register(User, UserAdmin)


@admin.register(CityModel)
class CityModelModel(admin.ModelAdmin):
    list_display = (
        "id", "name", "created_at", "updated_at"
    )
    search_fields = ("name",)
