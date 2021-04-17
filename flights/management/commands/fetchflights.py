from django.core.management.base import BaseCommand, CommandError
from flights.models import Flight
from flights.views import fetch_flights


class Command(BaseCommand):
    help = "Fetch/update the price list for flights."

    def handle(self, *args, **options):
        print("calling fetch flights")
        fetch_flights()
