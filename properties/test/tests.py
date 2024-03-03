import json
from django.test import TestCase

# Create your tests here.
from properties.services.property_valuation_service import PropertyValuationService
from properties.models.property_type_model import PropertyTypeModel
from properties.models.listing_type_model import ListingTypeModel
from properties.models.property_listing_model import PropertyListingModel
from domain.models.city_model import CityModel
from django.utils import timezone
from unittest.mock import patch, MagicMock


class TestPropertyValuationService(TestCase):

    @patch('properties.services.property_valuation_service.PropertyTypeModel.objects.get')
    @patch('properties.services.property_valuation_service.CityModel.objects.get')
    @patch('properties.services.property_valuation_service.ListingTypeModel.objects.get')
    @patch('properties.services.property_valuation_service.PropertyListingModel.objects.filter')
    def test_condominium_valuation(self, mock_filter, mock_get_listing_type, mock_get_city, mock_get_property_type):
        # Setup
        city_id = 1990  # Taguig
        floor_area = 100  # sqm
        year_built = timezone.now().year - 10  # Assuming the building is 10 years old

        # Mocking the dependencies
        mock_get_property_type.return_value = PropertyTypeModel(
            id=1,
            description='Condominium'
        )
        mock_get_city.return_value = CityModel(id=city_id, name='Taguig')
        mock_get_listing_type.side_effect = [
            ListingTypeModel(id=1, description='For Sale'),  # For sale
            ListingTypeModel(id=2, description='For Rent')  # For rent
        ]
        mock_filter.return_value = MagicMock()
        mock_filter.return_value.aggregate.return_value = {
            'average': 500000
        }  # Mock average price
        # Ensure there is at least one condominium listing
        mock_filter.return_value.exists.return_value = True

        # Test
        service = PropertyValuationService()
        result = service.condominium(
            floor_area=floor_area,
            city_id=city_id,
            year_built=year_built
        )

        # Verify
        # Printing the result to the console
        print(f"Test Result: {json.dumps(result, indent=4)}")
        self.assertIsNotNone(result)
        self.assertIn('for_sale_avg_price', result)
        self.assertIn('for_rent_avg_price', result)
        self.assertIn('appraisal_value_for_sale_price', result)
        self.assertIn('appraisal_value_for_rent_price', result)
        self.assertGreater(result['for_sale_avg_price'], 0)
        self.assertGreater(result['for_rent_avg_price'], 0)
        self.assertGreater(result['appraisal_value_for_sale_price'], 0)
        self.assertGreater(result['appraisal_value_for_rent_price'], 0)
        mock_filter.assert_called()  # Ensure the property listing model check was performed
