import os
import uuid
from datetime import datetime

from django.utils import timezone

from app import settings
from country.models import City
from django.db import models
from django.utils.text import slugify

from django.core.exceptions import ValidationError


class Crew(models.Model):
    first_name = models.CharField(max_length=63)
    last_name = models.CharField(max_length=63)

    class Meta:
        ordering = (
            "first_name",
            "last_name",
        )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


def airport_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.name)}-{uuid.uuid4()}.{extension}"
    return os.path.join("uploads/airports/", filename)


class Airport(models.Model):
    name = models.CharField(max_length=255, unique=True)
    closest_big_city = models.ForeignKey(
        City, on_delete=models.SET_NULL, null=True, related_name="airports"
    )
    image = models.ImageField(null=True, upload_to=airport_image_file_path, blank=True)

    class Meta:
        ordering = ("name", "closest_big_city")

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(
        Airport, on_delete=models.SET_NULL, null=True, related_name="sources"
    )
    destination = models.ForeignKey(
        Airport, on_delete=models.SET_NULL, null=True, related_name="destinations"
    )
    distance = models.IntegerField()

    class Meta:
        ordering = ("source",)

    def __str__(self):
        return f"{self.source} - {self.destination}"


class AirplaneType(models.Model):
    name = models.CharField(max_length=63, unique=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class AirCompany(models.Model):
    name = models.CharField(max_length=63, unique=True)

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "AirCompanies"

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=63)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(
        AirplaneType, on_delete=models.SET_NULL, null=True, related_name="airplanes"
    )
    air_company = models.ForeignKey(
        AirCompany, on_delete=models.SET_NULL, null=True, related_name="airplanes"
    )

    class Meta:
        ordering = ["name", "air_company", "airplane_type"]

    @property
    def capacity(self):
        return self.rows * self.seats_in_row

    def __str__(self):
        return f"{self.name}, company: {self.air_company} (type: {self.airplane_type})"


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="flights")
    airplane = models.ForeignKey(
        Airplane, on_delete=models.CASCADE, related_name="flights"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew, related_name="flights")

    class Meta:
        ordering = ["route", "-departure_time"]
        indexes = [
            models.Index(fields=["route"]),
            models.Index(fields=["departure_time"]),
        ]

    @staticmethod
    def validate_departure_arrival_time(departure_time, arrival_time, error_to_raise):
        now = datetime.now()
        if departure_time < now:
            raise error_to_raise(
                {"departure_time": f"Departure time shouldn't be earlier than {now}"}
            )

        if arrival_time < departure_time:
            raise error_to_raise(
                {"arrival_time": f"Arrival time can't be earlier than departure time"}
            )

    def clean(self):
        Flight.validate_departure_arrival_time(
            self.departure_time, self.arrival_time, ValidationError
        )

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.full_clean()
        return super(Flight, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self):
        return f"{str(self.route)} (departure: {self.departure_time}, arrival: {self.arrival_time})"


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey("Order", on_delete=models.CASCADE, related_name="tickets")

    class Meta:
        unique_together = ("flight", "row", "seat")
        ordering = ("seat", "row")

    @staticmethod
    def validate_seat_row(row: int, seat: int, flight, error_to_raise):
        for ticket_attr_value, ticket_attr_name, airplane_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row"),
        ]:
            count_attrs = getattr(flight.airplane, airplane_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                        f"number must be in available range: "
                        f"(1, {airplane_attr_name}): "
                        f"(1, {count_attrs})"
                    }
                )

    def clean(self):
        Ticket.validate_seat_row(self.row, self.seat, self.flight, ValidationError)

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        super(Ticket, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f"{str(self.flight)} (row: {self.row}, seat: {self.seat})"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return str(self.created_at)
