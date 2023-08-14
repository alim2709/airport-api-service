from django.urls import path, include
from rest_framework import routers

from service.views import (
    CrewViewSet,
    AirportViewSet,
    RouteViewSet,
    AirplaneTypeViewSet,
    AirCompanyViewSet,
    AirplaneViewSet,
    FlightViewSet,
    OrderViewSet,
)

router = routers.DefaultRouter()
router.register("crew", CrewViewSet)
router.register("airport", AirportViewSet)
router.register("route", RouteViewSet)
router.register("airplane-type", AirplaneTypeViewSet)
router.register("air-company", AirCompanyViewSet)
router.register("airplane", AirplaneViewSet)
router.register("flight", FlightViewSet)
router.register("orders", OrderViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "service"
