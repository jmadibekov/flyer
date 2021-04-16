from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import requests, json
from .models import Flight

API = "https://tequila-api.kiwi.com/v2/search"
API_KEY = "A5VqFeOZvXoOfy5zY19vBuWO4b4TJL23"
DATE_STR = "16/04/2021"

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


def fetch_flights():
    for route in ROUTES:
        print(route)

        response = requests.get(
            API,
            params={
                "fly_from": route["fly_from"],
                "fly_to": route["fly_to"],
                "date_from": DATE_STR,
                "date_to": DATE_STR,
            },
            headers={"apikey": API_KEY},
        )
        json_response = response.json()
        flights = json_response["data"]

        print(f"number of flights avail is {len(flights)}")

        if not flights:
            continue

        # first entry is always the cheapest flight ticket
        flight = flights[0]

        print(f"type of flight is {type(flight)}")
        print(flight)

        Flight.objects.create(
            fly_from=route["fly_from"],
            fly_to=route["fly_to"],
            price=flight["price"],
            booking_token=flight["booking_token"],
            date_time=flight["utc_departure"],
        )


def index(request):
    response = requests.get(
        API,
        params={
            "fly_from": "ALA",
            "fly_to": "TSE",
            "date_from": DATE_STR,
            "date_to": DATE_STR,
        },
        headers={"apikey": API_KEY},
    )
    json_data = response.json()
    print(f"Status code is {response.status_code}")
    return JsonResponse(json_data)