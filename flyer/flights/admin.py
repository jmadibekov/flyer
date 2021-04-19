from django.contrib import admin

from .models import Date, Flight


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ("fly_from", "fly_to", "price", "utc_departure", "last_updated")
    readonly_fields = ("id", "last_updated", "last_fetched")


class FlightInline(admin.TabularInline):
    model = Flight
    fields = ("fly_from", "fly_to", "price")
    max_num = 10
    extra = 0


@admin.register(Date)
class DateAdmin(admin.ModelAdmin):
    inlines = [
        FlightInline,
    ]
