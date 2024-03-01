import csv
from django.core.management.base import BaseCommand
from domain.models.city_model import CityModel


class Command(BaseCommand):
    help = 'Seed cities from CSV file'

    def handle(self, *args, **options):
        with open('../../csv/refcitymun.csv', mode='r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                _, created = CityModel.objects.get_or_create(
                    name=row[2]
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(
                        f'Successfully added city {row[2]}'))
                else:
                    self.stdout.write(self.style.WARNING(
                        f'City {row[2]} already exists'))
