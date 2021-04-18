from django.core.management.base import BaseCommand
from flights.views import fetch_flights


class Command(BaseCommand):
    help = "Fetch the price list for flights from external API and populate the DB from scratch"

    def handle(self, *args, **options):
        self.stdout.write("Starting fetching flight")
        fetch_flights()
