from django.db import transaction
from rest_framework import serializers

from country.models import City
from country.serializers import CityDetailSerializer
from service.models import (
    Crew,
    Airport,
    Route,
    AirplaneType,
    AirCompany,
    Airplane,
    Flight,
    Ticket,
    Order,
)


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ["id", "first_name", "last_name"]


class AirportSerializer(serializers.ModelSerializer):
    closest_big_city = serializers.SlugRelatedField(
        slug_field="id", queryset=City.objects.select_related("country")
    )

    class Meta:
        model = Airport
        fields = (
            "id",
            "name",
            "closest_big_city",
        )


class AirportImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = (
            "id",
            "image",
        )


class AirportListSerializer(AirportSerializer):
    closest_big_city = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="name"
    )

    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city", "image")
        read_only_fields = ("id", "image")


class AirportDetailSerializer(AirportSerializer):
    closest_big_city = CityDetailSerializer(many=False, read_only=True)

    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city", "image")
        read_only_fields = ("id", "image")


class RouteSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(
        slug_field="id", queryset=Airport.objects.select_related("closest_big_city")
    )
    destination = serializers.SlugRelatedField(
        slug_field="id", queryset=Airport.objects.select_related("closest_big_city")
    )

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(RouteSerializer):
    source = serializers.SlugRelatedField(many=False, read_only=True, slug_field="name")
    destination = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="name"
    )


class RouteDetailSerializer(RouteSerializer):
    source = AirportDetailSerializer(many=False, read_only=True)
    destination = AirportDetailSerializer(many=False, read_only=True)


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = AirCompany
        fields = ("id", "name")


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "capacity",
            "airplane_type",
            "air_company",
        )


class AirplaneListSerializer(AirplaneSerializer):
    airplane_type = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="name"
    )
    air_company = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="name"
    )


class AirplaneDetailSerializer(AirplaneSerializer):
    airplane_type = AirplaneTypeSerializer(many=False, read_only=True)
    air_company = AirCompanySerializer(many=False, read_only=True)


class FlightSerializer(serializers.ModelSerializer):
    route = serializers.SlugRelatedField(
        slug_field="id", queryset=Route.objects.select_related("source", "destination")
    )
    airplane = serializers.SlugRelatedField(
        slug_field="id",
        queryset=Airplane.objects.select_related("airplane_type", "air_company"),
    )

    def validate(self, attrs):
        data = super(FlightSerializer, self).validate(attrs)
        Flight.validate_departure_arrival_time(
            attrs["departure_time"], attrs["arrival_time"], serializers.ValidationError
        )
        return data

    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time", "crew")


class FlightListSerializer(FlightSerializer):
    route = serializers.StringRelatedField(many=False, read_only=True)
    crew = serializers.StringRelatedField(many=True, read_only=True)
    airplane = serializers.CharField(source="airplane.name")
    airplane_num_seats = serializers.IntegerField(source="airplane.capacity")
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "airplane_num_seats",
            "tickets_available",
            "departure_time",
            "arrival_time",
            "crew",
        )


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs)
        Ticket.validate_seat_row(
            attrs["row"], attrs["seat"], attrs["flight"], serializers.ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight")


class TicketSeatsSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat")


class FlightDetailSerializer(FlightSerializer):
    route = RouteDetailSerializer(many=False, read_only=True)
    crew = CrewSerializer(many=True, read_only=True)
    airplane = AirplaneDetailSerializer(many=False, read_only=True)
    taken_seats = TicketSeatsSerializer(source="tickets", many=True, read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "taken_seats",
            "departure_time",
            "arrival_time",
            "crew",
        )


class TicketListSerializer(TicketSerializer):
    flight = FlightListSerializer(many=False, read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at")

    @transaction.atomic
    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")
        order = Order.objects.create(**validated_data)
        for ticket_data in tickets_data:
            Ticket.objects.create(order=order, **ticket_data)
        return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
