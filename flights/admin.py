from django.contrib import admin

from .models import Flight

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('fly_from', 'fly_to', 'price', 'date_time')
