from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import requests, json
from .models import Flight
from django.utils import timezone
from datetime import timedelta

API = "https://tequila-api.kiwi.com/v2/search"
API_KEY = "A5VqFeOZvXoOfy5zY19vBuWO4b4TJL23"
DATE_FROM = timezone.now()
DATE_FROM_STR = DATE_FROM.strftime("%d/%m/%Y")

INTERVAL = timedelta(days=10)

DATE_TO = DATE_FROM + INTERVAL
DATE_TO_STR = DATE_TO.strftime("%d/%m/%Y")


ROUTES = [
    {
        "fly_from": "ALA",
        "fly_to": "TSE",
    },
    {
        "fly_from": "TSE",
        "fly_to": "ALA",
    },
    {
        "fly_from": "TSE",
        "fly_to": "LED",
    },
]


def flights_for_route(fly_from, fly_to):
    response = requests.get(
        API,
        params={
            "fly_from": fly_from,
            "fly_to": fly_to,
            "date_from": DATE_FROM_STR,
            "date_to": DATE_TO_STR,
        },
        headers={"apikey": API_KEY},
    )
    json_response = response.json()
    return json_response["data"]


def fetch_flights():
    # fetch from scratch, so clear the db
    Flight.objects.all().delete()

    for route in ROUTES:
        fly_from, fly_to = route["fly_from"], route["fly_to"]
        flights = flights_for_route(fly_from, fly_to)

        print(f"{route=} has {len(flights)} flights")

        for flight in flights:
            Flight.objects.create(
                fly_from=fly_from,
                fly_to=fly_to,
                price=flight["price"],
                booking_token=flight["booking_token"],
                utc_departure=flight["utc_departure"],
                utc_arrival=flight["utc_arrival"],
                deep_link=flight["deep_link"],
            )


def index(request):
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