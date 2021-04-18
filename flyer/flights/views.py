import json

from celery.result import AsyncResult
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets

from . import tasks
from .models import Date, Flight
from .serializers import DateSerializer, FlightSerializer

# ---------- View Sets For API -----------------


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer


class DateViewSet(viewsets.ModelViewSet):
    queryset = Date.objects.all()
    serializer_class = DateSerializer


# ---------- Views -----------------


def sample_fetch(request):
    # this is done in sync, contrary to [fetch] which is done in async with celery
    # just ALA -> TSE with one day interval, for simplicity
    return JsonResponse(tasks.request_flights("ALA", "TSE", "22/05/2021", "22/05/2021"))


@csrf_exempt
def fetch(request):
    if request.method == "POST":
        task = tasks.fetch_flights.delay()
        return JsonResponse({"task_id": task.id}, status=202)

    else:
        return HttpResponse(
            "Send a post request with empty body to fetch flights \
            manually (same as calling [python manage.py fetchflights])."
        )


def home(request):
    return HttpResponse("Why, hello my friend!")


@csrf_exempt
def run_sample_task(request):
    if request.method == "POST":
        body = json.loads(request.body)
        sleep_secs = body["secs"]
        task = tasks.sample_task.delay(int(sleep_secs))
        return JsonResponse({"task_id": task.id}, status=202)

    return HttpResponse("Send a post request to see celery task in action.")


@csrf_exempt
def get_status(request, task_id):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result,
    }
    return JsonResponse(result, status=200)
