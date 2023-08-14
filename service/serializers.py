from django.db import transaction
from rest_framework import serializers

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


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ["id", "first_name", "last_name"]


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city",)


class AirportListSerializer(AirportSerializer):
    closest_big_city = serializers.SlugRelatedField(many=False, read_only=True, slug_field="name")


class AirportImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "image",)


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


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
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type", "air_company")


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time", "crew")


class FlightListSerializer(FlightSerializer):
    route = serializers.StringRelatedField(many=False, read_only=True)
    crew = serializers.StringRelatedField(many=True, read_only=True)
    airplane = serializers.CharField(source="airplane.name")
    airplane_num_seats = serializers.IntegerField(source="airplane.capacity")

    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "airplane_num_seats", "departure_time", "arrival_time", "crew")


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
