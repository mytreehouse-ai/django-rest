import re
import json
from time import sleep
from logging import getLogger
from bs4 import BeautifulSoup
from celery import shared_task
from django.utils import timezone

from .services.scraperapi_service import ScrapyJobService
from .serializers.create_scrapy_job_serializer import CreateScrapyJobSerializer
from properties.models.property_type_model import PropertyTypeModel
from properties.models.property_status_model import PropertyStatusModel
from properties.models.listing_type_model import ListingTypeModel
from properties.models.property_listing_model import PropertyListingModel
from properties.models.property_model import PropertyModel
from domain.models.city_model import CityModel
from properties.models.price_history_model import PriceHistoryModel
from django_celery_beat.models import IntervalSchedule, PeriodicTask


logger = getLogger(__name__)


@shared_task()
def scraperapi_process_scrapy_web():
    """
    Initiates scraping jobs for each page of every Scrapy web entity.

    This function iterates through all Scrapy web entities retrieved from the database
    and sends a POST request to the ScraperAPI for each page of each Scrapy web entity.
    It constructs a payload containing the API key, the URL to scrape (with page number),
    and a callback webhook URL. After sending the request, it processes the response,
    creating a new Scrapy job in the database with the response data or logs an error
    if the response cannot be parsed as JSON or if the ScraperAPI returns an error status code.
    """
    scrapy_webs = ScrapyJobService.get_all_scrapy_web()

    for scrapy_web in scrapy_webs:
        for i in range(1, scrapy_web.page_number + 1):
            response = ScrapyJobService.scraper_api(
                scrapy_web=f"{scrapy_web.web_url}/?page={i}"
            )

            try:
                response_json: CreateScrapyJobSerializer = response.json()
                job = {
                    "job_id": response_json.get("id", None),
                    "domain": response_json.get("url", None),
                    "status": response_json.get("status", None),
                    "attempts": response_json.get("attempts", None),
                    "status_url": response_json.get("status_url", None),
                    "supposed_to_run_at": response_json.get("supposedToRunAt", None)
                }
                ScrapyJobService.create_job(**job)
            except ValueError:
                logger.error("Failed to parse response as JSON.")
                response_json = "Invalid JSON response"
            if response.status_code == 200:
                logger.info(
                    f"Scraping job started successfully. Response: {response_json}"
                )
            else:
                logger.error(
                    f"Failed to start scraping job. Status code: {response.status_code}, Response: {response_json}"
                )

            # Sleep for 1 second after each page iteration to avoid overwhelming the server
            sleep(1)


@shared_task()
def scraperapi_job_checker():
    pass


@shared_task()
def lamudi_single_page_scraper_task():
    property_details = []
    scrapy_jobs = ScrapyJobService.get_all_scrapy_job(single_page=True)

    def extract_address(soup):
        address_tag = soup.find(
            'h3',
            {
                'class': 'Title-pdp-address'
            }
        )

        if address_tag:
            address_text = address_tag.get_text(strip=True)
            return address_text
        else:
            return 'n/a'

    def extract_description(soup):
        description_div = soup.find(
            'div',
            {
                'class': 'listing-section listing-description'
            }
        )
        description_text = description_div.find(
            'div',
            {
                'class': 'ViewMore-text-description'
            }
        ) if description_div else None

        return description_text.get_text(separator=" ", strip=True) if description_text else 'n/a'

    def extract_images(soup):
        images = []
        if soup:  # Check if soup object is not None
            divs = soup.find_all(
                'div',
                {
                    'class': 'Banner-Images'
                }
            )

            for div_tag in divs:
                img_tag = div_tag.find('img')
                if img_tag:
                    data_src = img_tag.get('data-src')
                    if data_src and data_src.endswith('.webp'):
                        images.append(data_src)
        else:
            return ['n/a']  # Return a list with 'n/a' if soup is None

        return images

    def extract_amenities(soup):
        amenities_list = []
        amenities_div = soup.find(
            'div',
            {
                'class': 'listing-amenities-list'
            }
        )
        if amenities_div:
            amenities_span = amenities_div.find_all(
                'span',
                {
                    'class': 'listing-amenities-name'
                }
            )
            amenities_list = [span.text.strip() for span in amenities_span]
        return amenities_list

    def extract_property_details_div(soup):
        details_div = soup.find(
            'div', {'class': 'listing-section listing-details'})
        details = {}
        if details_div:
            rows = details_div.find_all('div', {'class': 'row'})
            for row in rows:
                columns = row.find_all(
                    'div', {'class': 'columns medium-6 small-6 striped'})
                for column in columns:
                    items = column.find_all('div', {'class': 'columns-2'})
                    for item in items:
                        key = item.find('div', {'class': 'ellipsis'}).get(
                            'data-attr-name', 'n/a').strip()
                        value = item.find(
                            'div', {'class': 'last'}).text.strip()
                        details[key] = value
        return details

    def extract_property_details(html_code: str):
        soup = BeautifulSoup(html_code, 'html.parser')

        address = re.sub(
            r'[\ufffd\u00f1\u00d1]',
            'ñ',
            extract_address(soup),
            flags=re.IGNORECASE
        )

        if address != "n/a":
            city = CityModel.objects.filter(
                name__icontains=address
            )

        property_details = {
            "address": address,
            "city": city.first().name if city.exists() else "Unknown",
            "description": extract_description(soup),
            "images": extract_images(soup),
            "details": extract_property_details_div(soup),
            "amenities": extract_amenities(soup)
        }

        return property_details

    for scrapy_job in scrapy_jobs:
        property_details = extract_property_details(scrapy_job.html_code)
        print(json.dumps(property_details, indent=4))


@shared_task()
def lamudi_multi_page_scraper_task():
    property_details = []

    def get_attribute(element, attribute):
        value = element.attrs.get(attribute, '')
        return 'n/a' if not value else value

    def extract_html(html_data: str):
        soup = BeautifulSoup(html_data, 'html.parser')
        info_elements = soup.find_all(class_='ListingCell-AllInfo ListingUnit')
        return info_elements

    scrapy_jobs = ScrapyJobService.get_all_scrapy_job()

    current_scrapy_job_id = None
    for_sale = ListingTypeModel.objects.get(id=1)
    for_rent = ListingTypeModel.objects.get(id=2)
    condominium = PropertyTypeModel.objects.get(id=1)
    house = PropertyTypeModel.objects.get(id=2)
    apartment = PropertyTypeModel.objects.get(id=3)
    warehouse = PropertyTypeModel.objects.get(id=4)
    land = PropertyTypeModel.objects.get(id=5)

    every_one_minute, created = IntervalSchedule.objects.get_or_create(
        every=1,
        period=IntervalSchedule.MINUTES
    )

    for scrapy_job in scrapy_jobs:
        current_scrapy_job_id = scrapy_job.job_id
        if scrapy_job.html_code:
            info_elements = extract_html(html_data=scrapy_job.html_code)
            listing_type = "for-sale" if "buy" in scrapy_job.domain else "for-rent"
            for element in info_elements:
                details_dict = {
                    'listing_title': element.find('a', class_='js-listing-link')['title'] if element.find('a', class_='js-listing-link') else 'n/a',
                    'listing_type': listing_type,
                    'price': float(get_attribute(element, 'data-price')) if get_attribute(element, 'data-price') != 'n/a' else 0.0,
                    # Seen in warehouse
                    'price_condition': get_attribute(element, 'data-price_conditions'),
                    'category': get_attribute(element, 'data-category'),
                    'subcategories': json.loads(get_attribute(element, 'data-subcategories')),
                    'year_built': int(get_attribute(element, 'data-year_built')) if get_attribute(element, 'data-year_built') != 'n/a' else None,
                    'building_name': get_attribute(element, 'data-condominiumname') if get_attribute(element, 'data-condominiumname') != 'n/a' else None,
                    'car_spaces': int(get_attribute(element, 'data-car_spaces')) if get_attribute(element, 'data-car_spaces').isdigit() else 0,
                    'bedrooms': int(get_attribute(element, 'data-bedrooms')) if get_attribute(element, 'data-bedrooms').isdigit() else 0,
                    'bathrooms': int(get_attribute(element, 'data-bathrooms')) if get_attribute(element, 'data-bathrooms').isdigit() else 0,
                    # floor area
                    'building_size': float(get_attribute(element, 'data-building_size')) if get_attribute(element, 'data-building_size') != 'n/a' else 0.0,
                    # sqm
                    'land_size': float(get_attribute(element, 'data-land_size')) if get_attribute(element, 'data-land_size') != 'n/a' else 0.0,
                    'furnished': get_attribute(element, 'data-furnished'),
                    'classification': get_attribute(element, 'data-classification'),
                    'block': get_attribute(element, 'data-block'),
                    # For warehouse
                    'subdivision_name': get_attribute(element, 'data-subdivisionname') if get_attribute(element, 'data-subdivisionname') != 'n/a' else None,
                    'sku': get_attribute(element, 'data-sku'),
                    'geo_point': [
                        float(coord.strip('[]')) for coord in get_attribute(element, 'data-geo-point').split(',') if coord.strip('[]') != 'null'
                    ] if get_attribute(element, 'data-geo-point') not in ['n/a', 'null', ''] else [0.0, 0.0],
                    'listing_url': element.find('a', class_='js-listing-link')['href'] if element.find('a', class_='js-listing-link') else None
                }
                property_details.append(details_dict)

    if current_scrapy_job_id:
        scrapy_job = ScrapyJobService.get_scrapy_job(
            job_id=current_scrapy_job_id
        )

        scrapy_job.html_code = None
        scrapy_job.is_processed = True
        scrapy_job.finished_processed_at = timezone.now()
        scrapy_job.save(
            update_fields=[
                "html_code",
                "is_processed",
                "finished_processed_at"
            ]
        )

        current_scrapy_job_id = None

    for property in property_details:
        if property.get("category") == "commercial":
            # Ensure price does not cause numeric field overflow
            price = min(property.get("price", 0), 999999999999.99)
            new_listing, created = PropertyListingModel.objects.get_or_create(
                listing_title=property.get("listing_title"),
                defaults={
                    'listing_url': property.get("listing_url"),
                    'listing_type': for_sale if property.get("listing_type") == "for-sale" else for_rent,
                    'property_type': warehouse,
                    'price': price,
                    'is_active': True
                }
            )

            if new_listing or created:
                response = ScrapyJobService.scraper_api(
                    scrapy_web=property.get("listing_url")
                )

                try:
                    response_json: CreateScrapyJobSerializer = response.json()
                    job = {
                        "job_id": response_json.get("id", None),
                        "domain": response_json.get("url", None),
                        "status": response_json.get("status", None),
                        "attempts": response_json.get("attempts", None),
                        "status_url": response_json.get("status_url", None),
                        "supposed_to_run_at": response_json.get("supposedToRunAt", None)
                    }
                    ScrapyJobService.create_job(**job)
                except ValueError:
                    logger.error("Failed to parse response as JSON.")
                    response_json = "Invalid JSON response"
                if response.status_code == 200:
                    logger.info(
                        f"Scraping job started successfully. Response: {response_json}"
                    )
                else:
                    logger.error(
                        f"Failed to start scraping job. Status code: {response.status_code}, Response: {response_json}"
                    )

            # Extract geo_point safely
            geo_point = property.get("geo_point", [None, None])
            longitude = geo_point[0] if len(geo_point) > 0 else 0.0
            latitude = geo_point[1] if len(geo_point) > 1 else 0.0

            if not created and new_listing.price != price:
                # If the listing already exists and the price has changed, save the historical price
                PriceHistoryModel.objects.create(
                    property_listing=new_listing,
                    price=new_listing.price,
                    date_recorded=timezone.now()
                )
                # Update the listing with the new price
                new_listing.price = price
                new_listing.save(update_fields=["price"])

            if created:
                new_warehouse = PropertyModel.objects.create(
                    subdivision_name=property.get("subdivision_name"),
                    lot_size=property.get("land_size"),
                    building_size=property.get("building_size"),
                    longitude=longitude,
                    latitude=latitude
                )

                new_listing.estate = new_warehouse
                new_listing.save(update_fields=["estate"])

                print(f"New listing added: {new_listing.listing_url}")
            else:
                if new_listing.estate:
                    new_listing.estate.subdivision_name = property.get(
                        "subdivision_name"
                    )
                    new_listing.estate.lot_size = property.get("land_size")
                    new_listing.estate.building_size = property.get(
                        "building_size"
                    )
                    new_listing.estate.longitude = longitude
                    new_listing.estate.latitude = latitude
                    new_listing.estate.save(
                        update_fields=[
                            "subdivision_name",
                            "lot_size",
                            "building_size",
                            "longitude",
                            "latitude"
                        ]
                    )
                    print(f"Listing already exists: {new_listing.listing_url}")
                else:
                    print(
                        f"Failed to update listing as estate does not exist: {new_listing.listing_url}"
                    )

        if property.get("category") == "condominium":
            # Ensure price does not cause numeric field overflow
            price = min(property.get("price", 0), 999999999999.99)
            new_listing, created = PropertyListingModel.objects.get_or_create(
                listing_title=property.get("listing_title"),
                defaults={
                    'listing_url': property.get("listing_url"),
                    'listing_type': for_sale if property.get("listing_type") == "for-sale" else for_rent,
                    'property_type': condominium,
                    'price': price,
                    'is_active': True
                }
            )

            if new_listing or created:
                response = ScrapyJobService.scraper_api(
                    scrapy_web=property.get("listing_url")
                )

                try:
                    response_json: CreateScrapyJobSerializer = response.json()
                    job = {
                        "job_id": response_json.get("id", None),
                        "domain": response_json.get("url", None),
                        "status": response_json.get("status", None),
                        "attempts": response_json.get("attempts", None),
                        "status_url": response_json.get("status_url", None),
                        "supposed_to_run_at": response_json.get("supposedToRunAt", None)
                    }
                    ScrapyJobService.create_job(**job)
                except ValueError:
                    logger.error("Failed to parse response as JSON.")
                    response_json = "Invalid JSON response"
                if response.status_code == 200:
                    logger.info(
                        f"Scraping job started successfully. Response: {response_json}"
                    )
                else:
                    logger.error(
                        f"Failed to start scraping job. Status code: {response.status_code}, Response: {response_json}"
                    )

            # Extract geo_point safely
            geo_point = property.get("geo_point", [None, None])
            longitude = geo_point[0] if len(geo_point) > 0 else 0.0
            latitude = geo_point[1] if len(geo_point) > 1 else 0.0

            if not created and new_listing.price != price:
                # If the listing already exists and the price has changed, save the historical price
                PriceHistoryModel.objects.create(
                    property_listing=new_listing,
                    price=new_listing.price,
                    date_recorded=timezone.now()
                )
                # Update the listing with the new price
                new_listing.price = price
                new_listing.save(update_fields=["price"])

            if created:
                new_condominium = PropertyModel.objects.create(
                    building_name=property.get("building_name"),
                    lot_size=property.get("land_size"),
                    floor_size=property.get("building_size"),
                    num_bedrooms=property.get("bedrooms"),
                    num_bathrooms=property.get("bathrooms"),
                    num_carspaces=property.get("car_spaces"),
                    year_built=property.get("year_built"),
                    central_business_district=False,
                    longitude=longitude,
                    latitude=latitude
                )

                new_listing.estate = new_condominium
                new_listing.save(update_fields=["estate"])

                print(f"New listing added: {new_listing.listing_url}")
            else:
                if new_listing.estate:
                    new_listing.estate.building_name = property.get(
                        "building_name"
                    )
                    new_listing.estate.lot_size = property.get("land_size")
                    new_listing.estate.floor_size = property.get(
                        "building_size"
                    )
                    new_listing.estate.num_bedrooms = property.get("bedrooms")
                    new_listing.estate.num_bathrooms = property.get(
                        "bathrooms"
                    )
                    new_listing.estate.num_carspaces = property.get(
                        "car_spaces"
                    )
                    new_listing.estate.year_built = property.get("year_built")
                    new_listing.estate.longitude = longitude
                    new_listing.estate.latitude = latitude
                    new_listing.estate.save(
                        update_fields=[
                            "building_name",
                            "lot_size",
                            "floor_size",
                            "num_bedrooms",
                            "num_bathrooms",
                            "num_carspaces",
                            "year_built",
                            "longitude",
                            "latitude"
                        ]
                    )
                else:
                    print(
                        f"Error: Estate for listing {new_listing.listing_url} is None."
                    )
                print(f"Listing already exists: {new_listing.listing_url}")

        if property.get("category") == "house":
            # Ensure price does not cause numeric field overflow
            price = min(property.get("price", 0), 999999999999.99)
            new_listing, created = PropertyListingModel.objects.get_or_create(
                listing_title=property.get("listing_title"),
                defaults={
                    'listing_url': property.get("listing_url"),
                    'listing_type': for_sale if property.get("listing_type") == "for-sale" else for_rent,
                    'property_type': house,
                    'price': price,
                    'is_active': True
                }
            )

            if new_listing or created:
                response = ScrapyJobService.scraper_api(
                    scrapy_web=property.get("listing_url")
                )

                try:
                    response_json: CreateScrapyJobSerializer = response.json()
                    job = {
                        "job_id": response_json.get("id", None),
                        "domain": response_json.get("url", None),
                        "status": response_json.get("status", None),
                        "attempts": response_json.get("attempts", None),
                        "status_url": response_json.get("status_url", None),
                        "supposed_to_run_at": response_json.get("supposedToRunAt", None)
                    }
                    ScrapyJobService.create_job(**job)
                except ValueError:
                    logger.error("Failed to parse response as JSON.")
                    response_json = "Invalid JSON response"
                if response.status_code == 200:
                    logger.info(
                        f"Scraping job started successfully. Response: {response_json}"
                    )
                else:
                    logger.error(
                        f"Failed to start scraping job. Status code: {response.status_code}, Response: {response_json}"
                    )

            # Extract geo_point safely
            geo_point = property.get("geo_point", [None, None])
            longitude = geo_point[0] if len(geo_point) > 0 else 0.0
            latitude = geo_point[1] if len(geo_point) > 1 else 0.0

            if not created and new_listing.price != price:
                # If the listing already exists and the price has changed, save the historical price
                PriceHistoryModel.objects.create(
                    property_listing=new_listing,
                    price=new_listing.price,
                    date_recorded=timezone.now()
                )
                # Update the listing with the new price
                new_listing.price = price
                new_listing.save(update_fields=["price"])

            if created:
                new_house = PropertyModel.objects.create(
                    lot_size=property.get("land_size"),
                    floor_size=property.get("building_size"),
                    num_bedrooms=property.get("bedrooms"),
                    num_bathrooms=property.get("bathrooms"),
                    num_carspaces=property.get("car_spaces"),
                    year_built=property.get("year_built"),
                    central_business_district=False,
                    longitude=longitude,
                    latitude=latitude
                )

                new_listing.estate = new_house
                new_listing.save(update_fields=["estate"])

                print(f"New listing added: {new_listing.listing_url}")
            else:
                if new_listing.estate:
                    new_listing.estate.lot_size = property.get("land_size")
                    new_listing.estate.floor_size = property.get(
                        "building_size"
                    )
                    new_listing.estate.num_bedrooms = property.get("bedrooms")
                    new_listing.estate.num_bathrooms = property.get(
                        "bathrooms"
                    )
                    new_listing.estate.num_carspaces = property.get(
                        "car_spaces"
                    )
                    new_listing.estate.year_built = property.get("year_built")
                    new_listing.estate.longitude = longitude
                    new_listing.estate.latitude = latitude
                    new_listing.estate.save(
                        update_fields=[
                            "lot_size",
                            "floor_size",
                            "num_bedrooms",
                            "num_bathrooms",
                            "num_carspaces",
                            "year_built",
                            "longitude",
                            "latitude"
                        ]
                    )
                else:
                    print(
                        f"Error: Estate for listing {new_listing.listing_url} is None."
                    )
                print(f"Listing already exists: {new_listing.listing_url}")

        if property.get("category") == "apartment":
            # Ensure price does not cause numeric field overflow
            price = min(property.get("price", 0), 999999999999.99)
            new_listing, created = PropertyListingModel.objects.get_or_create(
                listing_title=property.get("listing_title"),
                defaults={
                    'listing_url': property.get("listing_url"),
                    'listing_type': for_sale if property.get("listing_type") == "for-sale" else for_rent,
                    'property_type': apartment,
                    'price': price,
                    'is_active': True
                }
            )

            if new_listing or created:
                response = ScrapyJobService.scraper_api(
                    scrapy_web=property.get("listing_url")
                )

                try:
                    response_json: CreateScrapyJobSerializer = response.json()
                    job = {
                        "job_id": response_json.get("id", None),
                        "domain": response_json.get("url", None),
                        "status": response_json.get("status", None),
                        "attempts": response_json.get("attempts", None),
                        "status_url": response_json.get("status_url", None),
                        "supposed_to_run_at": response_json.get("supposedToRunAt", None)
                    }
                    ScrapyJobService.create_job(**job)
                except ValueError:
                    logger.error("Failed to parse response as JSON.")
                    response_json = "Invalid JSON response"
                if response.status_code == 200:
                    logger.info(
                        f"Scraping job started successfully. Response: {response_json}"
                    )
                else:
                    logger.error(
                        f"Failed to start scraping job. Status code: {response.status_code}, Response: {response_json}"
                    )

            # Extract geo_point safely
            geo_point = property.get("geo_point", [None, None])
            longitude = geo_point[0] if len(geo_point) > 0 else 0.0
            latitude = geo_point[1] if len(geo_point) > 1 else 0.0

            if not created and new_listing.price != price:
                # If the listing already exists and the price has changed, save the historical price
                PriceHistoryModel.objects.create(
                    property_listing=new_listing,
                    price=new_listing.price,
                    date_recorded=timezone.now()
                )
                # Update the listing with the new price
                new_listing.price = price
                new_listing.save(update_fields=["price"])

            if created:
                new_apartment = PropertyModel.objects.create(
                    lot_size=property.get("land_size"),
                    floor_size=property.get("building_size"),
                    num_bedrooms=property.get("bedrooms"),
                    num_bathrooms=property.get("bathrooms"),
                    num_carspaces=property.get("car_spaces"),
                    year_built=property.get("year_built"),
                    central_business_district=False,
                    longitude=longitude,
                    latitude=latitude
                )

                new_listing.estate = new_apartment
                new_listing.save(update_fields=["estate"])

                print(f"New listing added: {new_listing.listing_url}")
            else:
                if new_listing.estate:
                    new_listing.estate.lot_size = property.get("land_size")
                    new_listing.estate.floor_size = property.get(
                        "building_size"
                    )
                    new_listing.estate.num_bedrooms = property.get("bedrooms")
                    new_listing.estate.num_bathrooms = property.get(
                        "bathrooms"
                    )
                    new_listing.estate.num_carspaces = property.get(
                        "car_spaces"
                    )
                    new_listing.estate.year_built = property.get("year_built")
                    new_listing.estate.longitude = longitude
                    new_listing.estate.latitude = latitude
                    new_listing.estate.save(
                        update_fields=[
                            "lot_size",
                            "floor_size",
                            "num_bedrooms",
                            "num_bathrooms",
                            "num_carspaces",
                            "year_built",
                            "longitude",
                            "latitude"
                        ]
                    )
                else:
                    print(
                        f"Error: Estate for listing {new_listing.listing_url} is None."
                    )
                print(f"Listing already exists: {new_listing.listing_url}")

        if property.get("category") == "land":
            # Ensure price does not cause numeric field overflow
            price = min(property.get("price", 0), 999999999999.99)
            new_listing, created = PropertyListingModel.objects.get_or_create(
                listing_title=property.get("listing_title"),
                defaults={
                    'listing_url': property.get("listing_url"),
                    'listing_type': for_sale if property.get("listing_type") == "for-sale" else for_rent,
                    'property_type': land,
                    'price': price,
                    'is_active': True
                }
            )

            if new_listing or created:
                response = ScrapyJobService.scraper_api(
                    scrapy_web=property.get("listing_url")
                )

                try:
                    response_json: CreateScrapyJobSerializer = response.json()
                    job = {
                        "job_id": response_json.get("id", None),
                        "domain": response_json.get("url", None),
                        "status": response_json.get("status", None),
                        "attempts": response_json.get("attempts", None),
                        "status_url": response_json.get("status_url", None),
                        "supposed_to_run_at": response_json.get("supposedToRunAt", None)
                    }
                    ScrapyJobService.create_job(**job)
                except ValueError:
                    logger.error("Failed to parse response as JSON.")
                    response_json = "Invalid JSON response"
                if response.status_code == 200:
                    logger.info(
                        f"Scraping job started successfully. Response: {response_json}"
                    )
                else:
                    logger.error(
                        f"Failed to start scraping job. Status code: {response.status_code}, Response: {response_json}"
                    )

            # Extract geo_point safely
            geo_point = property.get("geo_point", [None, None])
            longitude = geo_point[0] if len(geo_point) > 0 else 0.0
            latitude = geo_point[1] if len(geo_point) > 1 else 0.0

            if not created and new_listing.price != price:
                # If the listing already exists and the price has changed, save the historical price
                PriceHistoryModel.objects.create(
                    property_listing=new_listing,
                    price=new_listing.price,
                    date_recorded=timezone.now()
                )
                # Update the listing with the new price
                new_listing.price = price
                new_listing.save(update_fields=["price"])

            if created:
                new_land = PropertyModel.objects.create(
                    subdivision_name=property.get("subdivision_name"),
                    lot_size=property.get("land_size"),
                    building_size=property.get("building_size"),
                    longitude=longitude,
                    latitude=latitude
                )

                new_listing.estate = new_land
                new_listing.save(update_fields=["estate"])

                print(f"New listing added: {new_listing.listing_url}")
            else:
                if new_listing.estate:
                    new_listing.estate.subdivision_name = property.get(
                        "subdivision_name"
                    )
                    new_listing.estate.lot_size = property.get("land_size")
                    new_listing.estate.building_size = property.get(
                        "building_size"
                    )
                    new_listing.estate.longitude = longitude
                    new_listing.estate.latitude = latitude
                    new_listing.estate.save(
                        update_fields=[
                            "subdivision_name",
                            "lot_size",
                            "building_size",
                            "longitude",
                            "latitude"
                        ]
                    )
                    print(f"Listing already exists: {new_listing.listing_url}")
                else:
                    print(
                        f"Failed to update listing as estate does not exist: {new_listing.listing_url}"
                    )

        sleep(0.5)

    property_details = []
