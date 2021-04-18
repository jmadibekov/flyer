from django.core.management.base import BaseCommand
from flights.views import fetch_flights


class Command(BaseCommand):
    help = "Fetch/update the price list for flights."

    def handle(self, *args, **options):
        print("calling fetch flights")
        fetch_flights()
