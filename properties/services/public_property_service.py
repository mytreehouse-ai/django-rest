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
        return PropertyListingModel.objects.filter(slug__isnull=False)

    @staticmethod
    def get_one_property_listing(listing_title: str) -> PropertyListingModel:
        """
        Retrieves a single property listing from the database based on the listing URL.

        This method queries the PropertyListingModel to fetch a property listing that matches
        the provided listing URL. If no matching property is found, it returns None.

        Args:
            listing_url (str): The URL of the listing to retrieve.

        Returns:
            PropertyListingModel: The property listing if found, otherwise None.
        """
        try:
            return PropertyListingModel.objects.get(slug=listing_title)
        except PropertyListingModel.DoesNotExist:
            return None
