from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import requests, json
from .models import Flight, Date
from django.utils import timezone
from datetime import timedelta, datetime
import maya
from rest_framework import viewsets
from .serializers import FlightSerializer, DateSerializer
from enum import Enum

API = "https://tequila-api.kiwi.com/v2/search"
API_KEY = "A5VqFeOZvXoOfy5zY19vBuWO4b4TJL23"
DATE_FROM = timezone.now()
DATE_FROM_STR = DATE_FROM.strftime("%d/%m/%Y")

INTERVAL = timedelta(days=30)

DATE_TO = DATE_FROM + INTERVAL
DATE_TO_STR = DATE_TO.strftime("%d/%m/%Y")

LIMIT = 5000


class CityCode(Enum):
    ALA = "Almaty"
    TSE = "Nur-Sultan"
    MOW = "Moscow"
    CIT = "Shymkent"
    LED = "Saint Petersburg"


# most common routes
def common_routes():
    routes = [
        (CityCode.ALA, CityCode.TSE),
        (CityCode.ALA, CityCode.MOW),
        (CityCode.ALA, CityCode.CIT),
        (CityCode.TSE, CityCode.MOW),
        (CityCode.TSE, CityCode.LED),
    ]
    list_routes = []
    for route in routes:
        list_routes.extend(
            [
                {
                    "fly_from": route[0].name,
                    "fly_to": route[1].name,
                },
                {
                    "fly_from": route[1].name,
                    "fly_to": route[0].name,
                },
            ]
        )
    return list_routes


def flights_for_route(fly_from, fly_to):
    response = requests.get(
        API,
        params={
            "fly_from": fly_from,
            "fly_to": fly_to,
            "date_from": DATE_FROM_STR,
            "date_to": DATE_TO_STR,
            "limit": LIMIT,
        },
        headers={"apikey": API_KEY},
    )
    json_response = response.json()
    return json_response["data"]


def fetch_flights():
    # fetch from scratch, so clear the db
    Flight.objects.all().delete()
    Date.objects.all().delete()

    for route in common_routes():
        fly_from, fly_to = route["fly_from"], route["fly_to"]
        flights = flights_for_route(fly_from, fly_to)

        print(f"{route=} has {len(flights)} flights")

        for flight in flights:
            cur_datetime = maya.parse(flight["utc_departure"]).datetime()
            local_datetime = cur_datetime.astimezone(timezone.get_current_timezone())

            date, _ = Date.objects.get_or_create(date=local_datetime.date())

            Flight.objects.create(
                fly_from=fly_from,
                fly_to=fly_to,
                price=flight["price"],
                booking_token=flight["booking_token"],
                utc_departure=flight["utc_departure"],
                utc_arrival=flight["utc_arrival"],
                deep_link=flight["deep_link"],
                date=date,
            )


def sample_fetch(request):
    response = requests.get(
        API,
        params={
            "fly_from": "ALA",
            "fly_to": "TSE",
            # just a one day interval, for simplicity
            "date_from": DATE_FROM_STR,
            "date_to": DATE_FROM_STR,
        },
        headers={"apikey": API_KEY},
    )
    json_data = response.json()
    print(f"Status code is {response.status_code}")
    return JsonResponse(json_data)


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer


class DateViewSet(viewsets.ModelViewSet):
    queryset = Date.objects.all()
    serializer_class = DateSerializer
