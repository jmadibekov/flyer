from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"flights", views.FlightViewSet)
router.register(r"dates", views.DateViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
    path("sample-fetch/", views.sample_fetch, name="sample_fetch"),
]
