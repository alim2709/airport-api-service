import tempfile
import os

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from service.models import Airport
from service.tests.test_flight_api import sample_city, sample_airport


AIRPORT_URL = reverse("service:airport-list")


def image_upload_url(airport_id):
    """Return URL for recipe image upload"""
    return reverse("service:airport-upload-image", args=[airport_id])


def detail_url(airport_id):
    return reverse("service:airport-detail", args=[airport_id])


class AirportImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@myproject.com", "password"
        )
        self.client.force_authenticate(self.user)
        self.city = sample_city()
        self.airport = sample_airport()

    def tearDown(self):
        self.airport.image.delete()

    def test_upload_image_to_airport(self):
        """Test uploading an image to airport"""
        url = image_upload_url(self.airport.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.airport.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.airport.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.airport.id)
        res = self.client.post(url, {"image": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_airport_list(self):
        url = AIRPORT_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url,
                {
                    "name": "Name_airport",
                    "closest_big_city": self.city.id,
                    "image": ntf,
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        airport = Airport.objects.get(name="Name_airport")
        self.assertFalse(airport.image)

    def test_image_url_is_shown_on_airport_detail(self):
        url = image_upload_url(self.airport.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(detail_url(self.airport.id))

        self.assertIn("image", res.data)

    def test_image_url_is_shown_on_airport_list(self):
        url = image_upload_url(self.airport.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(AIRPORT_URL)

        self.assertIn("image", res.data["results"][0].keys())
