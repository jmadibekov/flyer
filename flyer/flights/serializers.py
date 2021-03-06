from rest_framework import serializers

from .models import Date, Flight
from .tasks import ROUTES


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = "__all__"


class DateSerializer(serializers.ModelSerializer):
    cheapest_flights = serializers.SerializerMethodField()

    class Meta:
        model = Date
        fields = "__all__"

    def get_cheapest_flights(self, obj):
        cheapest_flights = []

        for route in ROUTES:
            fly_from, fly_to = route["fly_from"], route["fly_to"]
            try:
                flight = obj.flight_set.filter(
                    fly_from=fly_from, fly_to=fly_to
                ).order_by("price")[0]
                cheapest_flights.append(flight)
            except IndexError:
                continue

        return FlightSerializer(cheapest_flights, many=True).data
