from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status, serializers
from rest_framework.test import APIClient

from service.models import Order, Ticket
from service.tests.test_flight_api import sample_flight, detail_url

ORDER_URL = reverse("service:order-list")
FLIGHT_URL = reverse("service:flight-list")


class OrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.flight = sample_flight()
        self.user = get_user_model().objects.create_user(
            "testunique@tests.com", "unique_password"
        )
        self.client.force_authenticate(self.user)
        self.order = Order.objects.create(user=self.user)
        self.ticket = Ticket.objects.create(
            flight=self.flight, row=2, seat=5, order=self.order
        )

    def test_get_order(self):
        self.client.force_authenticate(user=self.user)
        orders_response = self.client.get(ORDER_URL)
        self.assertEqual(orders_response.status_code, status.HTTP_200_OK)
        self.assertEqual(orders_response.data["count"], 1)
        order = orders_response.data["results"][0]
        self.assertEqual(len(order["tickets"]), 1)
        ticket = order["tickets"][0]
        self.assertEqual(ticket["row"], 2)
        self.assertEqual(ticket["seat"], 5)
        flight = ticket["flight"]
        self.assertEqual(flight["route"], "test_source - test_destination")
        self.assertEqual(flight["airplane"], "Test Airplane")
        self.assertEqual(
            flight["departure_time"],
            serializers.DateTimeField().to_representation(self.flight.departure_time),
        )
        self.assertEqual(
            flight["arrival_time"],
            serializers.DateTimeField().to_representation(self.flight.arrival_time),
        )

    def test_flights_detail_tickets(self):
        response = self.client.get(detail_url(self.flight.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["taken_seats"][0]["row"], self.ticket.row)
        self.assertEqual(response.data["taken_seats"][0]["seat"], self.ticket.seat)

    def test_flight_list_tickets_available(self):
        response = self.client.get(FLIGHT_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["results"][0]["tickets_available"],
            self.flight.airplane.capacity - 1,
        )
