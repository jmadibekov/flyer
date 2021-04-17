from rest_framework import serializers
from .models import Flight, Date


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = "__all__"


class DateSerializer(serializers.ModelSerializer):
    cheapest_flight = serializers.SerializerMethodField()

    class Meta:
        model = Date
        fields = "__all__"

    def get_cheapest_flight(self, obj):
        try:
            flight = obj.flight_set.order_by("price")[0]
            return FlightSerializer(flight).data
        except IndexError:
            return None
