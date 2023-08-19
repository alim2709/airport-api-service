from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from service.models import AirplaneType, AirCompany, Airplane
from service.serializers import AirplaneListSerializer, AirplaneDetailSerializer

AIRPLANE_URL = reverse("service:airplane-list")


def sample_airplane_type(**params):
    defaults = {
        "name": "test_type"
    }
    defaults.update(params)

    return AirplaneType.objects.create(**defaults)


def sample_air_company(**params):
    defaults = {
        "name": "test_company"
    }
    defaults.update(params)

    return AirCompany.objects.create(**defaults)


def sample_airplane(**params):
    airplane_type = sample_airplane_type()
    air_company = sample_air_company()
    defaults = {
        "name": "test_airplane",
        "rows": 6,
        "seats_in_row": 5,
        "airplane_type": airplane_type,
        "air_company": air_company
    }
    defaults.update(params)

    return Airplane.objects.create(**defaults)


def detail_url(airplane_id):
    return reverse("service:airplane-detail", args=[airplane_id])


class UnauthenticatedFlightApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPLANE_URL)
        self.assertEquals(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedFlightApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "testunique@tests.com",
            "unique_password"
        )
        self.client.force_authenticate(self.user)
        self.airplane = sample_airplane()

    def test_list_airplanes(self):
        res = self.client.get(AIRPLANE_URL)

        airplanes = Airplane.objects.all()
        serializer = AirplaneListSerializer(airplanes, many=True)
        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertEquals(res.data["results"], serializer.data)

    def test_retrieve_airplane_detail(self):
        airplane = self.airplane

        url = detail_url(airplane.id)
        res = self.client.get(url)

        serializer = AirplaneDetailSerializer(airplane)

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertEquals(res.data, serializer.data)

    def test_create_flight_forbidden(self):
        airplane_type = sample_airplane_type(name="test_create_forbidden")
        air_company = sample_air_company(name="test_air_company_forbidden")
        payload = {
            "name": "test_create_airplane",
            "rows": 6,
            "seats_in_row": 6,
            "airplane_type": airplane_type,
            "air_company": air_company
        }
        res = self.client.post(AIRPLANE_URL, payload)

        self.assertEquals(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_airplane_not_allowed(self):
        airplane = self.airplane
        url = detail_url(airplane.id)
        res = self.client.delete(url)

        self.assertEquals(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_airplane_not_allowed(self):
        airplane = self.airplane
        url = detail_url(airplane.id)
        airplane_type = sample_airplane_type(name="test_update_not_allowed")
        air_company = sample_air_company(name="test_air_company_not_allowed")
        payload = {
            "name": "test_update_airplane",
            "rows": 6,
            "seats_in_row": 6,
            "airplane_type": airplane_type,
            "air_company": air_company
        }
        res = self.client.put(url, payload)

        self.assertEquals(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com",
            "testpass",
            is_staff=True
        )
        self.client.force_authenticate(self.user)
        self.airplane = sample_airplane()

    def test_create_airplane(self):
        airplane_type = sample_airplane_type(name="test_create_allowed")
        air_company = sample_air_company(name="test_air_company_allowed")
        payload = {
            "name": "test_create_airplane_allowed",
            "rows": 6,
            "seats_in_row": 6,
            "airplane_type": airplane_type.id,
            "air_company": air_company.id
        }
        res = self.client.post(AIRPLANE_URL, payload)
        self.assertEquals(res.status_code, status.HTTP_201_CREATED)

    def test_update_airplane_allowed(self):
        airplane = self.airplane
        url = detail_url(airplane.id)
        airplane_type = sample_airplane_type(name="test_update_allowed")
        air_company = sample_air_company(name="test_air_company_allowed")
        payload = {
            "name": "test_update_airplane_allowed",
            "rows": 6,
            "seats_in_row": 6,
            "airplane_type": airplane_type.id,
            "air_company": air_company.id
        }
        res = self.client.put(url, payload)

        self.assertEquals(res.status_code, status.HTTP_200_OK)

    def test_delete_airplane_not_allowed(self):
        airplane = self.airplane
        url = detail_url(airplane.id)
        res = self.client.delete(url)

        self.assertEquals(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
