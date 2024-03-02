import json
import uuid
from time import sleep
from logging import getLogger
from bs4 import BeautifulSoup
from celery import shared_task
from django.utils import timezone

from .services.scraperapi_service import ScrapyJobService
from .serializers.create_scrapy_job_serializer import CreateScrapyJobSerializer
from .models.scrapy_job_model import ScrapyJobModel
from properties.models.property_listing_model import PropertyListingModel
from properties.models.property_model import PropertyModel
from properties.models.price_history_model import PriceHistoryModel


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
                ScrapyJobModel.objects.update_or_create(
                    domain=response_json.get("url", None),
                    defaults={
                        "job_id": response_json.get("id", None),
                        "status": response_json.get("status", None),
                        "attempts": response_json.get("attempts", None),
                        "status_url": response_json.get("status_url", None),
                        "supposed_to_run_at": response_json.get("supposedToRunAt", None),
                        "is_multi_page_processed": False,
                        "is_single_page_processed": False
                    }
                )
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

            sleep(0.5)


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

    scrapy_jobs = ScrapyJobService.get_all_scrapy_job_for_task()

    logger.info(f"Scrapy jobs length: {len(scrapy_jobs)}")

    if not scrapy_jobs:
        ScrapyJobModel.objects.all().update(
            is_multi_page_processed=False,
            finished_processed_at=None
        )
        logger.info(
            "No scrapy jobs found for task reseting processed properties."
        )

    current_scrapy_domains = []

    for scrapy_job in scrapy_jobs:
        if scrapy_job.html_code:
            current_scrapy_domains.append(scrapy_job.domain)
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

    ScrapyJobModel.objects.filter(domain__in=current_scrapy_domains).update(
        html_code=None,
        is_multi_page_processed=True,
        finished_processed_at=timezone.now()
    )

    current_scrapy_domains = []

    for property in property_details:
        if property.get("category") == "commercial":
            listing_url = PropertyListingModel.objects.filter(
                listing_url=property.get("listing_url")
            )
            if not listing_url.exists():
                # Ensure price does not cause numeric field overflow
                price = min(property.get("price", 0), 999999999999.99)
                new_listing, created = PropertyListingModel.objects.update_or_create(
                    listing_title=property.get("listing_title"),
                    defaults={
                        'listing_url': property.get("listing_url"),
                        'price': price
                    }
                )

                if new_listing or created:
                    generated_uuid = str(uuid.uuid4())
                    ScrapyJobModel.objects.get_or_create(
                        domain=property.get("listing_url"),
                        defaults={
                            "job_id": generated_uuid,
                            "status": "finished",
                            "attempts": 0,
                            "single_page": True,
                            "status_url": f"https://api.mytree.house/status/{generated_uuid}",
                            "supposed_to_run_at": timezone.now()
                        }
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
                    new_listing.price_formatted = f"₱{price:,.2f}"
                    new_listing.save(
                        update_fields=[
                            "price",
                            "price_formatted"
                        ]
                    )

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

        if property.get("category") == "condominium":
            listing_url = PropertyListingModel.objects.filter(
                listing_url=property.get("listing_url")
            )
            if not listing_url.exists():
                # Ensure price does not cause numeric field overflow
                price = min(property.get("price", 0), 999999999999.99)
                new_listing, created = PropertyListingModel.objects.update_or_create(
                    listing_title=property.get("listing_title"),
                    defaults={
                        'listing_url': property.get("listing_url"),
                        'price': price
                    }
                )

                if new_listing or created:
                    generated_uuid = str(uuid.uuid4())
                    ScrapyJobModel.objects.get_or_create(
                        domain=property.get("listing_url"),
                        defaults={
                            "job_id": generated_uuid,
                            "status": "finished",
                            "attempts": 0,
                            "single_page": True,
                            "status_url": f"https://api.mytree.house/status/{generated_uuid}",
                            "supposed_to_run_at": timezone.now()
                        }
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
                    new_listing.price_formatted = f"₱{price:,.2f}"
                    new_listing.save(
                        update_fields=[
                            "price",
                            "price_formatted"
                        ]
                    )

                if created:
                    new_condominium = PropertyModel.objects.create(
                        building_name=property.get("building_name"),
                        lot_size=property.get("land_size"),
                        floor_size=property.get("building_size"),
                        num_bedrooms=property.get("bedrooms"),
                        num_bathrooms=property.get("bathrooms"),
                        num_carspaces=property.get("car_spaces"),
                        longitude=longitude,
                        latitude=latitude
                    )

                    new_listing.estate = new_condominium
                    new_listing.save(update_fields=["estate"])

                    print(f"New listing added: {new_listing.listing_url}")

        if property.get("category") == "house":
            listing_url = PropertyListingModel.objects.filter(
                listing_url=property.get("listing_url")
            )
            if not listing_url.exists():
                # Ensure price does not cause numeric field overflow
                price = min(property.get("price", 0), 999999999999.99)
                new_listing, created = PropertyListingModel.objects.update_or_create(
                    listing_title=property.get("listing_title"),
                    defaults={
                        'listing_url': property.get("listing_url"),
                        'price': price
                    }
                )

                if new_listing or created:
                    generated_uuid = str(uuid.uuid4())
                    ScrapyJobModel.objects.get_or_create(
                        domain=property.get("listing_url"),
                        defaults={
                            "job_id": generated_uuid,
                            "status": "finished",
                            "attempts": 0,
                            "single_page": True,
                            "status_url": f"https://api.mytree.house/status/{generated_uuid}",
                            "supposed_to_run_at": timezone.now()
                        }
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
                    new_listing.price_formatted = f"₱{price:,.2f}"
                    new_listing.save(
                        update_fields=[
                            "price",
                            "price_formatted"
                        ]
                    )

                if created:
                    new_house = PropertyModel.objects.create(
                        lot_size=property.get("land_size"),
                        floor_size=property.get("building_size"),
                        num_bedrooms=property.get("bedrooms"),
                        num_bathrooms=property.get("bathrooms"),
                        num_carspaces=property.get("car_spaces"),
                        longitude=longitude,
                        latitude=latitude
                    )

                    new_listing.estate = new_house
                    new_listing.save(update_fields=["estate"])

                    print(f"New listing added: {new_listing.listing_url}")

        if property.get("category") == "apartment":
            listing_url = PropertyListingModel.objects.filter(
                listing_url=property.get("listing_url")
            )
            if not listing_url.exists():
                # Ensure price does not cause numeric field overflow
                price = min(property.get("price", 0), 999999999999.99)
                new_listing, created = PropertyListingModel.objects.update_or_create(
                    listing_title=property.get("listing_title"),
                    defaults={
                        'listing_url': property.get("listing_url"),
                        'price': price
                    }
                )

                if new_listing or created:
                    generated_uuid = str(uuid.uuid4())
                    ScrapyJobModel.objects.get_or_create(
                        domain=property.get("listing_url"),
                        defaults={
                            "job_id": generated_uuid,
                            "status": "finished",
                            "attempts": 0,
                            "single_page": True,
                            "status_url": f"https://api.mytree.house/status/{generated_uuid}",
                            "supposed_to_run_at": timezone.now()
                        }
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
                    new_listing.price_formatted = f"₱{price:,.2f}"
                    new_listing.save(
                        update_fields=[
                            "price",
                            "price_formatted"
                        ]
                    )

                if created:
                    new_apartment = PropertyModel.objects.create(
                        lot_size=property.get("land_size"),
                        floor_size=property.get("building_size"),
                        num_bedrooms=property.get("bedrooms"),
                        num_bathrooms=property.get("bathrooms"),
                        num_carspaces=property.get("car_spaces"),
                        longitude=longitude,
                        latitude=latitude
                    )

                    new_listing.estate = new_apartment
                    new_listing.save(update_fields=["estate"])

                    print(f"New listing added: {new_listing.listing_url}")

        if property.get("category") == "land":
            listing_url = PropertyListingModel.objects.filter(
                listing_url=property.get("listing_url")
            )
            if not listing_url.exists():
                # Ensure price does not cause numeric field overflow
                price = min(property.get("price", 0), 999999999999.99)
                new_listing, created = PropertyListingModel.objects.update_or_create(
                    listing_title=property.get("listing_title"),
                    defaults={
                        'listing_url': property.get("listing_url"),
                        'price': price
                    }
                )

                if new_listing or created:
                    generated_uuid = str(uuid.uuid4())
                    ScrapyJobModel.objects.get_or_create(
                        domain=property.get("listing_url"),
                        defaults={
                            "job_id": generated_uuid,
                            "status": "finished",
                            "attempts": 0,
                            "single_page": True,
                            "status_url": f"https://api.mytree.house/status/{generated_uuid}",
                            "supposed_to_run_at": timezone.now()
                        }
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
                    new_listing.price_formatted = f"₱{price:,.2f}"
                    new_listing.save(
                        update_fields=[
                            "price",
                            "price_formatted"
                        ]
                    )

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

        sleep(0.5)

    property_details = []
