from django.db.models import Prefetch
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from service.models import (
    Crew,
    Airport,
    Route,
    AirplaneType,
    AirCompany,
    Airplane,
    Flight,
    Ticket, Order
)
from service.serializers import (
    CrewSerializer,
    AirportSerializer,
    RouteSerializer,
    AirplaneTypeSerializer,
    AirCompanySerializer,
    AirplaneSerializer,
    FlightSerializer,
    OrderSerializer,
    OrderListSerializer,
    AirportListSerializer,
    AirportImageSerializer
)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "list":
            queryset = queryset.select_related("closest_big_city")
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return AirportListSerializer
        if self.action == "upload_image":
            return AirportImageSerializer
        return AirportSerializer

    @action(methods=["POST"], detail=True, url_path="upload-image", permission_classes=[IsAdminUser])
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to specific airport"""
        airport = self.get_object()
        serializer = self.get_serializer(airport, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


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


class OrderPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 100


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = OrderPagination
    permission_classes = (IsAuthenticated,)

    # permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        if self.action == "list":
            queryset = queryset.prefetch_related(
                Prefetch(
                    "tickets",
                    queryset=Ticket.objects.select_related(
                        "flight__route__destination",
                        "flight__route__source"
                    ).prefetch_related(
                        "flight__airplane",
                        "flight__crew"
                    )
                )
            )
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
