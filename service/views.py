from django.db.models import Prefetch, F, Count
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
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
    Ticket,
    Order
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
    AirportImageSerializer,
    RouteListSerializer,
    AirportDetailSerializer,
    RouteDetailSerializer,
    AirplaneListSerializer,
    AirplaneDetailSerializer,
    FlightListSerializer,
    FlightDetailSerializer
)


def _params_to_ints(qs):
    """Converts a list of string IDs to a list of integers"""
    return [int(str_id) for str_id in qs.split(",")]


class CrewViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminUser,)


class AirportViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
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
        if self.action == "retrieve":
            return AirportDetailSerializer
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


class RouteViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "list":
            queryset = queryset.select_related("source__closest_big_city", "destination__closest_big_city")

        """Filtering by source and destination"""

        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")

        if source:
            queryset = queryset.filter(source__name__icontains=source)
        if destination:
            queryset = queryset.filter(destination__name__icontains=destination)
        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        if self.action == "retrieve":
            return RouteDetailSerializer
        return RouteSerializer

    # Only for documentation purposes
    @extend_schema(
        parameters=[
            OpenApiParameter(
                "source",
                type={"type": "list", "items": {"type": "string"}},
                description="Filter by source  (ex. ?source=ka)"
            ),
            OpenApiParameter(
                "destination",
                type={"type": "list", "items": {"type": "string"}},
                description="Filter by destination  (ex. ?destination=pa)"
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class AirplaneTypeViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminUser,)


class AirCompanyViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = AirCompany.objects.all()
    serializer_class = AirCompanySerializer


class AirplaneViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related("airplane_type", "air_company")
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        if self.action == "retrieve":
            return AirplaneDetailSerializer
        return AirplaneSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer

    def get_queryset(self):

        queryset = self.queryset

        if self.action == "list":
            queryset = (
                queryset.select_related("airplane")
                .annotate(tickets_available=F("airplane__rows") * F("airplane__seats_in_row") - Count("tickets"))
                .order_by("id").prefetch_related("crew")
            )

        """Filtering by route, departure date, arrival date"""

        routes = self.request.query_params.get("routes")
        departure_date = self.request.query_params.get("departure")
        arrival_date = self.request.query_params.get("arrival")
        if routes:
            route_ids = _params_to_ints(routes)
            queryset = queryset.filter(route__id__in=route_ids)
        if departure_date:
            queryset = queryset.filter(departure_time__date=departure_date)
        if arrival_date:
            queryset = queryset.filter(arrival_time__date=arrival_date)

        return queryset.select_related(
            "airplane__air_company",
            "airplane__airplane_type",
            "route__source__closest_big_city__country",
            "route__destination__closest_big_city__country"
        ).prefetch_related("crew", "tickets").distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightDetailSerializer
        return FlightSerializer

    # Only for documentation purposes
    @extend_schema(
        parameters=[
            OpenApiParameter(
                "routes",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by routes  (ex. ?route=1,2)"
            ),
            OpenApiParameter(
                "departure date",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description="Filter by departure date (ex. ?departure=2023-10-08)",
            ),
            OpenApiParameter(
                "arrival date",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description="Filter by arrival date (ex. ?arrival=2023-11-08)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

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
