from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"flights", views.FlightViewSet)
router.register(r"dates", views.DateViewSet)

urlpatterns = [
    path("", views.home, name="home"),
    # api endpoint by DRF
    path("api/", include(router.urls)),
    # sample api request done in sync
    path("sample-fetch/", views.sample_fetch, name="sample_fetch"),
    path("sample-check/", views.sample_check, name="sample_check"),
    # url endpoint to create async tasks, respectively
    path("fetch/", views.fetch, name="fetch"),
    path("check/", views.check, name="check"),
    # create a sample async task or check the status of the tasks
    path("tasks/sample-task/", views.run_sample_task, name="run_sample_task"),
    path("tasks/<task_id>/", views.get_status, name="get_status"),
]
