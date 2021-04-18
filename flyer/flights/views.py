from datetime import timedelta
from enum import Enum

import maya
import requests
from celery.result import AsyncResult
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets

from .models import Date, Flight
from .serializers import DateSerializer, FlightSerializer
from .tasks import sample_task

# ---------- View Sets For API -----------------


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer


class DateViewSet(viewsets.ModelViewSet):
    queryset = Date.objects.all()
    serializer_class = DateSerializer


# ---------------------------------------------


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


def fetch_flights():
    # fetch from scratch, so clear the db
    Flight.objects.all().delete()
    Date.objects.all().delete()

    for route in ROUTES:
        fly_from, fly_to = route["fly_from"], route["fly_to"]
        flights = request_flights(fly_from, fly_to, DATE_FROM_STR, DATE_TO_STR)["data"]

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


# ---------- Views -----------------


def sample_fetch(request):
    # just ALA -> TSE with one day interval, for simplicity
    return JsonResponse(
        request_flights(
            CityCode.ALA.name, CityCode.TSE.name, DATE_FROM_STR, DATE_TO_STR
        )
    )


def home(request):
    return HttpResponse("Why, hello my friend!")


@csrf_exempt
def run_sample_task(request):
    if request.POST:
        sleep_secs = request.POST.get("secs")
        task = sample_task.delay(int(sleep_secs))
        return JsonResponse({"task_id": task.id}, status=202)


@csrf_exempt
def get_status(request, task_id):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result,
    }
    return JsonResponse(result, status=200)
