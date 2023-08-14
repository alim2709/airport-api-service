from django.shortcuts import render
from rest_framework import viewsets

from service.models import (
    Crew,
    Airport,
    Route,
    AirplaneType,
    AirCompany,
    Airplane,
    Flight,
    Ticket
)
from service.serializers import (
    CrewSerializer,
    AirportSerializer,
    RouteSerializer,
    AirplaneTypeSerializer,
    AirCompanySerializer,
    AirplaneSerializer,
    FlightSerializer,
    TicketSerializer
)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirCompanyViewSet(viewsets.ModelViewSet):
    queryset = AirCompany.objects.all()
    serializer_class = AirCompanySerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer



