from logging import getLogger
from rest_framework import serializers

from domain.models.city_model import CityModel

logger = getLogger(__name__)


class ReadCitySerializer(serializers.ModelSerializer):
    class Meta:
        model = CityModel
        fields = [
            "id",
            "name"
        ]
