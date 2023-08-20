from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from service.models import Route
from service.serializers import RouteListSerializer, RouteDetailSerializer
from service.tests.test_flight_api import sample_route, sample_airport


ROUTE_URL = reverse("service:route-list")


def detail_url(route_id):
    return reverse("service:route-detail", args=[route_id])


class UnauthenticatedRouteApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ROUTE_URL)
        self.assertEquals(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedRouteApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "testunique@tests.com", "unique_password"
        )
        self.client.force_authenticate(self.user)
        self.route = sample_route()
        self.airport = sample_airport()

    def test_list_routes(self):
        res = self.client.get(ROUTE_URL)

        routes = Route.objects.all()
        serializer = RouteListSerializer(routes, many=True)
        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertEquals(res.data["results"], serializer.data)

    def test_filter_route_by_source(self):
        route1 = sample_route(
            source=sample_airport(name="test_source_filtered"), distance=300
        )
        route2 = sample_route(source=sample_airport(name="test_source2"), distance=400)
        route3 = sample_route(source=sample_airport(name="test_source3"), distance=500)

        res = self.client.get(ROUTE_URL, {"source": "f"})

        serializer1 = RouteListSerializer(route1)
        serializer2 = RouteListSerializer(route2)
        serializer3 = RouteListSerializer(route3)

        self.assertIn(serializer1.data, res.data["results"])
        self.assertNotIn(serializer2.data, res.data["results"])
        self.assertNotIn(serializer3.data, res.data["results"])

    def test_filter_route_by_destination(self):
        route1 = sample_route(
            destination=sample_airport(name="test_source_filtered"), distance=300
        )
        route2 = sample_route(
            destination=sample_airport(name="test_source2"), distance=400
        )
        route3 = sample_route(
            destination=sample_airport(name="test_source3"), distance=500
        )

        res = self.client.get(ROUTE_URL, {"destination": "f"})

        serializer1 = RouteListSerializer(route1)
        serializer2 = RouteListSerializer(route2)
        serializer3 = RouteListSerializer(route3)

        self.assertIn(serializer1.data, res.data["results"])
        self.assertNotIn(serializer2.data, res.data["results"])
        self.assertNotIn(serializer3.data, res.data["results"])

    def test_retrieve_airplane_detail(self):
        route = self.route

        url = detail_url(route.id)
        res = self.client.get(url)

        serializer = RouteDetailSerializer(route)

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertEquals(res.data, serializer.data)

    def test_create_route_forbidden(self):
        source_airport = sample_airport(name="test_create_forbidden")
        destination_airport = sample_airport(name="test_destination_forbidden")
        payload = {
            "source": source_airport,
            "destination": destination_airport,
            "distance": 500,
        }
        res = self.client.post(ROUTE_URL, payload)

        self.assertEquals(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_route_not_allowed(self):
        route = self.route
        url = detail_url(route.id)
        res = self.client.delete(url)

        self.assertEquals(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_route_not_allowed(self):
        route = self.route
        url = detail_url(route.id)
        source_airport = sample_airport(name="test_update_forbidden")
        destination_airport = sample_airport(name="test_update_destination_forbidden")
        payload = {
            "source": source_airport,
            "destination": destination_airport,
            "distance": 500,
        }
        res = self.client.put(url, payload)

        self.assertEquals(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminRouteApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)
        self.route = sample_route()

    def test_create_route(self):
        source_airport = sample_airport(name="test_create_forbidden")
        destination_airport = sample_airport(name="test_destination_forbidden")
        payload = {
            "source": source_airport.id,
            "destination": destination_airport.id,
            "distance": 500,
        }
        res = self.client.post(ROUTE_URL, payload)

        self.assertEquals(res.status_code, status.HTTP_201_CREATED)

    def test_update_route_allowed(self):
        route = self.route
        url = detail_url(route.id)
        source_airport = sample_airport(name="test_update_forbidden")
        destination_airport = sample_airport(name="test_update_destination_forbidden")
        payload = {
            "source": source_airport.id,
            "destination": destination_airport.id,
            "distance": 500,
        }
        res = self.client.put(url, payload)

        self.assertEquals(res.status_code, status.HTTP_200_OK)

    def test_delete_airplane_not_allowed(self):
        route = self.route
        url = detail_url(route.id)
        res = self.client.delete(url)

        self.assertEquals(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
