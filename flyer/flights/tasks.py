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


# --------------

API = "https://tequila-api.kiwi.com/v2/search"
API_KEY = "A5VqFeOZvXoOfy5zY19vBuWO4b4TJL23"
DATE_FROM = timezone.now()
DATE_FROM_STR = DATE_FROM.strftime("%d/%m/%Y")

INTERVAL = timedelta(days=3)

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
        # (CityCode.ALA, CityCode.MOW),
        # (CityCode.ALA, CityCode.CIT),
        # (CityCode.TSE, CityCode.MOW),
        # (CityCode.TSE, CityCode.LED),
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


def request_flights(fly_from, fly_to, date_from, date_to):
    response = requests.get(
        API,
        params={
            "fly_from": fly_from,
            "fly_to": fly_to,
            "date_from": date_from,
            "date_to": date_to,
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
        f"Requesting flight info from external API \
            from {DATE_FROM_STR} to {DATE_TO_STR}."
    )

    for route in ROUTES:
        fly_from, fly_to = route["fly_from"], route["fly_to"]
        flights = request_flights(fly_from, fly_to, DATE_FROM_STR, DATE_TO_STR)["data"]

        print(f"Route [{fly_from} -> {fly_to}] has {len(flights)} flights.")

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
