from logging import getLogger
from typing import List
from ..models.property_listing_model import PropertyListingModel

logger = getLogger(__name__)


class PublicPropertyService:
    """
    Service class for accessing public property listings.

    This class provides static methods to interact with property listing data,
    allowing for retrieval of property listings from the database.
    """

    @staticmethod
    def get_all_property_listing() -> List[PropertyListingModel]:
        """
        Retrieves all property listings from the database.

        This method queries the PropertyListingModel to fetch all existing property listings
        without any filters applied.

        Returns:
            List[PropertyListingModel]: A list of all property listings.
        """
        return PropertyListingModel.objects.filter(is_active=True, is_delisted=False)
