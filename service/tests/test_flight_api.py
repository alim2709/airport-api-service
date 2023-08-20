import datetime
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from country.models import Country, City
from service.models import (
    Airport,
    Route,
    AirplaneType,
    AirCompany,
    Airplane,
    Crew,
    Flight,
)
from service.serializers import FlightListSerializer, FlightDetailSerializer

FLIGHT_URL = reverse("service:flight-list")


def sample_country(**params):
    defaults = {"name": "testCountry"}
    defaults.update(params)
    country, _ = Country.objects.get_or_create(**defaults)
    return country


def sample_city(**params):
    country = sample_country()

    defaults = {"name": "Sample city", "country": country}
    defaults.update(params)
    city, _ = City.objects.get_or_create(**defaults)
    return city


def sample_airport(**params):
    city = sample_city()
    defaults = {"name": "TestAirport", "closest_big_city": city}
    defaults.update(params)
    airport, _ = Airport.objects.get_or_create(**defaults)
    return airport


def sample_route(**params):
    source_city = sample_city(name="test_source")
    source = sample_airport(name="test_source", closest_big_city=source_city)
    destination_city = sample_city(name="test_destination")
    destination = sample_airport(
        name="test_destination", closest_big_city=destination_city
    )
    defaults = {"source": source, "destination": destination, "distance": 300}
    defaults.update(params)
    route, _ = Route.objects.get_or_create(**defaults)
    return route


def sample_airplane_type(**params):
    defaults = {"name": "TestAirplaneType"}

    defaults.update(params)
    airplane_type, _ = AirplaneType.objects.get_or_create(**defaults)
    return airplane_type


def sample_air_company(**params):
    defaults = {"name": "TestAirCompany"}

    defaults.update(params)
    air_company, _ = AirCompany.objects.get_or_create(**defaults)
    return air_company


def sample_airplane(**params):
    airplane_type = sample_airplane_type()
    air_company = sample_air_company()

    defaults = {
        "name": "Test Airplane",
        "rows": 6,
        "seats_in_row": 10,
        "airplane_type": airplane_type,
        "air_company": air_company,
    }

    defaults.update(params)
    airplane, _ = Airplane.objects.get_or_create(**defaults)
    return airplane


def sample_crew(**params):
    defaults = {"first_name": "test_first_name", "last_name": "test_last_name"}
    defaults.update(params)
    crew, _ = Crew.objects.get_or_create(**defaults)
    return crew


def sample_flight(**params):
    route = sample_route()
    airplane = sample_airplane()
    departure_time = datetime.datetime.now() + datetime.timedelta(days=1)
    arrival_time = departure_time + datetime.timedelta(hours=10)

    defaults = {
        "route": route,
        "airplane": airplane,
        "departure_time": departure_time,
        "arrival_time": arrival_time,
    }
    defaults.update(params)
    flight, _ = Flight.objects.get_or_create(**defaults)
    return flight


def detail_url(flight_id):
    return reverse("service:flight-detail", args=[flight_id])


class UnauthenticatedFlightApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(FLIGHT_URL)
        self.assertEquals(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedFlightApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "testunique@tests.com", "unique_password"
        )
        self.client.force_authenticate(self.user)

    def test_list_flight(self):
        sample_flight()
        city = sample_city(name="test23")
        route1 = sample_route(
            source=sample_airport(name="test_test1", closest_big_city=city),
            destination=sample_airport(name="test_test2"),
        )
        flight_with_crews = sample_flight(route=route1)

        crew1 = sample_crew(first_name="test_name")
        crew2 = sample_crew(first_name="test2_name")

        flight_with_crews.crew.add(crew1, crew2)

        res = self.client.get(FLIGHT_URL)

        flights = Flight.objects.all()
        for flight_data in res.data["results"]:
            flight_data.pop("tickets_available", None)
        serializer = FlightListSerializer(flights, many=True)

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertEquals(res.data["results"], serializer.data)

    def test_filter_flight_by_route(self):
        flight1 = sample_flight(route=sample_route(distance=300))
        flight2 = sample_flight(route=sample_route(distance=400))
        flight3 = sample_flight(route=sample_route(distance=500))

        res = self.client.get(FLIGHT_URL, {"routes": f"{flight1.route_id}"})

        serializer1 = FlightListSerializer(flight1)
        serializer2 = FlightListSerializer(flight2)
        serializer3 = FlightListSerializer(flight3)
        for flight_data in res.data["results"]:
            flight_data.pop("tickets_available", None)

        self.assertIn(serializer1.data, res.data["results"])
        self.assertNotIn(serializer2.data, res.data["results"])
        self.assertNotIn(serializer3.data, res.data["results"])

    def test_filter_flight_by_departure_date(self):
        with patch("service.models.datetime") as now_time_mock:
            now_time_mock.now.return_value = datetime.datetime(2023, 7, 10)

            flight1 = sample_flight(
                route=sample_route(distance=300), departure_time="2023-07-11"
            )
            flight2 = sample_flight(
                route=sample_route(distance=400), departure_time="2023-07-12"
            )
            flight3 = sample_flight(
                route=sample_route(distance=500), departure_time="2023-07-13"
            )

            res = self.client.get(FLIGHT_URL, {"departure": "2023-07-11"})

            serializer1 = FlightListSerializer(flight1)
            serializer2 = FlightListSerializer(flight2)
            serializer3 = FlightListSerializer(flight3)
            for flight_data in res.data["results"]:
                flight_data.pop("tickets_available", None)

            self.assertIn(serializer1.data, res.data["results"])
            self.assertNotIn(serializer2.data, res.data["results"])
            self.assertNotIn(serializer3.data, res.data["results"])

    def test_filter_flight_by_arrival_date(self):
        with patch("service.models.datetime") as now_time_mock:
            now_time_mock.now.return_value = datetime.datetime(2023, 7, 10)
            flight1 = sample_flight(
                route=sample_route(distance=300), arrival_time="2023-09-11"
            )
            flight2 = sample_flight(
                route=sample_route(distance=400), arrival_time="2023-09-12"
            )
            flight3 = sample_flight(
                route=sample_route(distance=500), arrival_time="2023-09-13"
            )

            res = self.client.get(FLIGHT_URL, {"arrival": "2023-09-11"})

            serializer1 = FlightListSerializer(flight1)
            serializer2 = FlightListSerializer(flight2)
            serializer3 = FlightListSerializer(flight3)
            for flight_data in res.data["results"]:
                flight_data.pop("tickets_available", None)

            self.assertIn(serializer1.data, res.data["results"])
            self.assertNotIn(serializer2.data, res.data["results"])
            self.assertNotIn(serializer3.data, res.data["results"])

    def test_retrieve_flight_detail(self):
        flight = sample_flight()

        url = detail_url(flight.id)
        res = self.client.get(url)

        serializer = FlightDetailSerializer(flight)

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertEquals(res.data, serializer.data)

    def test_create_flight_forbidden(self):
        route = sample_route()
        airplane = sample_airplane()
        departure_time = datetime.datetime.now() + datetime.timedelta(days=2)
        arrival_time = departure_time + datetime.timedelta(hours=10)
        payload = {
            "route": route,
            "airplane": airplane,
            "departure_time": departure_time,
            "arrival_time": arrival_time,
        }
        res = self.client.post(FLIGHT_URL, payload)

        self.assertEquals(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_flight_not_allowed(self):
        flight = sample_flight()
        url = detail_url(flight.id)
        res = self.client.delete(url)

        self.assertEquals(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_flight_not_allowed(self):
        flight = sample_flight()
        url = detail_url(flight.id)
        route = sample_route(distance=400)
        airplane = sample_airplane(name="test_update")
        departure_time = datetime.datetime.now() + datetime.timedelta(days=3)
        arrival_time = departure_time + datetime.timedelta(hours=10)
        payload = {
            "route": route,
            "airplane": airplane,
            "departure_time": departure_time,
            "arrival_time": arrival_time,
        }
        res = self.client.put(url, payload)

        self.assertEquals(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminFlightApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_flight(self):
        route = sample_route()
        airplane = sample_airplane()
        crew1 = sample_crew()
        crew2 = sample_crew(first_name="test_create")
        departure_time = datetime.datetime.now() + datetime.timedelta(days=4)
        arrival_time = departure_time + datetime.timedelta(hours=10)
        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": departure_time,
            "arrival_time": arrival_time,
            "crew": [crew1.id, crew2.id],
        }
        check_in = {
            "route": route,
            "airplane": airplane,
            "departure_time": departure_time,
            "arrival_time": arrival_time,
            "crew": [crew1, crew2],
        }

        res = self.client.post(FLIGHT_URL, payload)
        flight = Flight.objects.get(id=res.data["id"])

        self.assertEquals(res.status_code, status.HTTP_201_CREATED)
        self.assertEquals(check_in["route"], flight.route)
        self.assertEquals(check_in["airplane"], flight.airplane)
        self.assertEqual(check_in["crew"], list(flight.crew.all().order_by("id")))

    def test_update_flight(self):
        flight = sample_flight()
        url = detail_url(flight.id)
        route = sample_route(source=sample_airport(name="test_1_source"), distance=500)
        airplane = sample_airplane(name="test_update_1")
        crew1 = sample_crew(first_name="test_crew1")
        crew2 = sample_crew(first_name="test_crew2")
        departure_time = datetime.datetime.now() + datetime.timedelta(days=6)
        arrival_time = departure_time + datetime.timedelta(hours=10)
        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": departure_time,
            "arrival_time": arrival_time,
            "crew": [crew1.id, crew2.id],
        }
        res = self.client.put(url, payload)
        self.assertEquals(res.status_code, status.HTTP_200_OK)

    def test_delete_flight_allowed(self):
        flight = sample_flight()
        url = detail_url(flight.id)
        res = self.client.delete(url)

        self.assertEquals(res.status_code, status.HTTP_204_NO_CONTENT)
