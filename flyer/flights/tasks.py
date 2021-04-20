import time
from datetime import timedelta
from enum import Enum

import maya
import requests
from celery import shared_task
from django.utils import timezone

from .models import Date, Flight


@shared_task
def sample_task(sleep_secs):
    time.sleep(int(sleep_secs))
    print(f"Why, I've slept for {sleep_secs} seconds!")
    return True


# ------------------------------------

ROOT_API = "https://tequila-api.kiwi.com/v2/"
SEARCH_API = ROOT_API + "search"
CHECK_FLIGHTS_API = ROOT_API + "booking/check_flights/"

API_KEY = "A5VqFeOZvXoOfy5zY19vBuWO4b4TJL23"

DATE_FROM = timezone.now()
DATE_FROM_STR = DATE_FROM.strftime("%d/%m/%Y")

INTERVAL = timedelta(days=30)

DATE_TO = DATE_FROM + INTERVAL
DATE_TO_STR = DATE_TO.strftime("%d/%m/%Y")

LIMIT = 5000

# for each date and route, I store only up to 5 flights (starting from cheapest);
# for one, I think that's more than enough; secondly, it'll be faster performance-wise
MAX_NUM_OF_FLIGHTS_FOR_DAY_PER_ROUTE = 5


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


ROUTES = common_routes()

MAX_RETRIES_ON_CHECK_FLIGHTS = 5

# ------------- Updating Flights -------------


def update_flight(flight):
    print(f"{flight} --- updating")

    retries = 0
    data = None

    while True:
        retries += 1
        if retries > MAX_RETRIES_ON_CHECK_FLIGHTS:
            break

        response = requests.get(
            CHECK_FLIGHTS_API,
            params={
                "booking_token": flight.booking_token,
                "bnum": 0,
                "pnum": 1,
            },
            headers={"apikey": API_KEY},
        )
        data = response.json()
        if data["flights_checked"] is False:
            time.sleep(2)
            print("[flights_checked] is false, thus retrying again!")
        else:
            break

    if data["flights_checked"] is False:
        print(f"{flight} --- error: [flight_checked] is false instead of true!")

    elif data["flights_invalid"] is True:
        print(f"{flight} --- it isnt valid anymore, thus deleting the instance!")
        flight.delete()

    elif data["price_change"] is True:
        print(f'{flight} --- new price is {data["total"]}!')
        flight.price = data["total"]
        flight.save()

    else:
        print(f"{flight} --- no changes :)")
        flight.save()

    return data


@shared_task
def check_flights():
    print("Celery worker started the task [check_flights].")
    print(f"There are {Flight.objects.all().count()} flights to update.")
    for flight in Flight.objects.order_by("utc_departure"):
        update_flight(flight)


# ------------- Fetching Flights -------------


def request_flights(fly_from, fly_to, date_from, date_to):
    response = requests.get(
        SEARCH_API,
        params={
            "fly_from": fly_from,
            "fly_to": fly_to,
            "date_from": date_from,
            "date_to": date_to,
            "sort": "price",  # sorted from cheapest
            "asc": 1,  # to the most expensive
            "limit": LIMIT,
        },
        headers={"apikey": API_KEY},
    )
    return response.json()


@shared_task
def fetch_flights():
    # fetch from scratch, so clearing the db first
    print("Celery worker started the task [fetch_flights].")
    print("Flushing the DB.")
    Flight.objects.all().delete()
    Date.objects.all().delete()

    print(
        f"Requesting flight info from external API from {DATE_FROM_STR} to {DATE_TO_STR}."
    )

    for route in ROUTES:
        fly_from, fly_to = route["fly_from"], route["fly_to"]
        flights = request_flights(fly_from, fly_to, DATE_FROM_STR, DATE_TO_STR)["data"]

        print(f"Route [{fly_from} -> {fly_to}] has {len(flights)} flights.")

        for flight in flights:
            cur_datetime = maya.parse(flight["utc_departure"]).datetime()
            local_datetime = cur_datetime.astimezone(timezone.get_current_timezone())

            date, _ = Date.objects.get_or_create(date=local_datetime.date())

            num_of_flights = date.flight_set.filter(
                fly_from=fly_from, fly_to=fly_to
            ).count()

            # print(
            #     f'Date {date} [{flight["local_departure"]}] has already {num_of_flights} flights.'
            # )

            if num_of_flights >= MAX_NUM_OF_FLIGHTS_FOR_DAY_PER_ROUTE:
                continue

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
