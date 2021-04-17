from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r"flights", views.FlightViewSet)
router.register(r"dates", views.DateViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
    path("sample-fetch/", views.sample_fetch, name="sample_fetch"),
]