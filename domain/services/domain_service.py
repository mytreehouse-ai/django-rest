from logging import getLogger
from typing import List

from ..models.city_model import CityModel

logger = getLogger(__name__)


class DomainService:
    """
    A service class for domain-related operations.

    This class provides services related to domain operations, such as retrieving city information.
    """

    @staticmethod
    def get_all_city() -> List[CityModel]:
        """
        Retrieves all cities from the database.

        Returns:
            List[CityModel]: A list of all CityModel instances from the database.
        """
        return CityModel.objects.filter()
