from django.contrib import admin

from .models import Flight


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ("fly_from", "fly_to", "price", "utc_departure", "last_updated")
    readonly_fields = ("last_updated", "last_fetched")
