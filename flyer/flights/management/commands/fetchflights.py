from django.core.management.base import BaseCommand
from flights import tasks


class Command(BaseCommand):
    help = "Fetch the price list for flights from external API and populate the DB from scratch."

    def handle(self, *args, **options):
        task = tasks.fetch_flights.delay()
        self.stdout.write(f"Success. Created task with task_id: {task.id}")
