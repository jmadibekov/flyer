from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"flights", views.FlightViewSet)
router.register(r"dates", views.DateViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
    path("", views.home, name="home"),
    path("sample-fetch/", views.sample_fetch, name="sample_fetch"),
    path("fetch/", views.fetch, name="fetch"),
    path("tasks/sample-task/", views.run_sample_task, name="run_sample_task"),
    path("tasks/<task_id>/", views.get_status, name="get_status"),
]
