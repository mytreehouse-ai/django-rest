from logging import getLogger
from django.utils import timezone
from django.db.models import Avg

from ..models.property_listing_model import PropertyListingModel
from ..models.property_model import PropertyModel
from ..models.listing_type_model import ListingTypeModel
from ..models.property_type_model import PropertyTypeModel
from domain.models.city_model import CityModel

logger = getLogger(__name__)


class PropertyValuationService:
    def _get_property_type_condominium(self):
        try:
            return PropertyTypeModel.objects.get(id=1)
        except PropertyTypeModel.DoesNotExist:
            return None

    def _get_city(self, city_id):
        try:
            return CityModel.objects.get(id=city_id)
        except CityModel.DoesNotExist:
            return None

    def _get_listing_type(self, listing_type_id):
        try:
            return ListingTypeModel.objects.get(id=listing_type_id)
        except ListingTypeModel.DoesNotExist:
            return None

    def condominium(self, floor_area: int, city_id: int, year_built: int):
        property_type_condominium = self._get_property_type_condominium()
        if not property_type_condominium:
            return {
                "detail": "Condominium property type not found"
            }

        city = self._get_city(city_id)
        if not city:
            return {
                "detail": "City not found"
            }

        listing_type_for_sale = self._get_listing_type(1)
        if not listing_type_for_sale:
            return {
                "detail": "Listing type for sale not found"
            }

        listing_type_for_rent = self._get_listing_type(2)
        if not listing_type_for_rent:
            return {
                "detail": "Listing type for rent not found"
            }

        CONDOMINIUM_LIFE_SPAN_IN_NUMBER_YEARS = 50
        current_year = timezone.now().year
        condominium_remaining_useful_life = (
            CONDOMINIUM_LIFE_SPAN_IN_NUMBER_YEARS - (
                current_year - year_built
            )
        ) / CONDOMINIUM_LIFE_SPAN_IN_NUMBER_YEARS

        # The following query calculates the average price of property listings for sale that match certain criteria:
        # - The price is greater than 1
        # - The property type is condominium
        # - The listing type is for sale
        # - The estate's floor area is within 80% to 120% of the specified floor area
        # - The estate is located in the specified city
        # The result is stored in a dictionary with the key 'average', which represents the average price.
        # To access the average price, use average_property_price_for_sale['average'].
        average_property_price_for_sale = PropertyListingModel.objects.filter(
            price__gt=1,
            property_type=property_type_condominium,
            listing_type=listing_type_for_sale,
            estate__floor_area__gte=floor_area * 0.8,
            estate__floor_area__lte=floor_area * 1.2,
            estate__city=city,
        ).aggregate(average=Avg('price'))

        # The following query calculates the average price of property listings for sale that match certain criteria:
        # - The price is greater than 1
        # - The property type is condominium
        # - The listing type is for rent
        # - The estate's floor area is within 80% to 120% of the specified floor area
        # - The estate is located in the specified city
        # The result is stored in a dictionary with the key 'average', which represents the average price.
        # To access the average price, use average_property_price_for_rent['average'].
        average_property_price_for_rent = PropertyListingModel.objects.filter(
            price__gt=1,
            property_type=property_type_condominium,
            listing_type=listing_type_for_rent,
            estate__floor_area__gte=floor_area * 0.8,
            estate__floor_area__lte=floor_area * 1.2,
            estate__city=city,
        ).aggregate(average=Avg('price'))

        for_sale_avg_price = average_property_price_for_sale.get("average", 0)
        for_rent_avg_price = average_property_price_for_rent.get("average", 0)

        if for_rent_avg_price == 0 and for_rent_avg_price == 0:
            return {
                "detail": "Your search criteria for condominium properties did not match any records in our database. Please adjust your search parameters and try again."
            }

        appraisal_value_for_sale_price_per_sqm = for_sale_avg_price / floor_area
        appraisal_value_for_rent_price_per_sqm = for_rent_avg_price / floor_area

        appraisal_value_for_sale_price = (
            floor_area * condominium_remaining_useful_life
        ) * appraisal_value_for_sale_price_per_sqm

        appraisal_value_for_rent_price = (
            floor_area * condominium_remaining_useful_life
        ) * appraisal_value_for_rent_price_per_sqm

        return {
            "for_sale_avg_price": for_sale_avg_price,
            "for_rent_avg_price": for_rent_avg_price,
            "appraisal_value_for_sale_price_per_sqm": appraisal_value_for_sale_price_per_sqm,
            "appraisal_value_for_rent_price_per_sqm": appraisal_value_for_rent_price_per_sqm,
            "appraisal_value_for_sale_price": appraisal_value_for_sale_price,
            "appraisal_value_for_rent_price": appraisal_value_for_rent_price
        }
