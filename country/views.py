from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAdminUser

from country.models import Country, City
from country.serializers import (
    CountrySerializer,
    CitySerializer,
    CityListSerializer,
    CountryDetailSerializer,
)


class CountryViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = (IsAdminUser,)

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ("list", "retrieve"):
            queryset = queryset.prefetch_related("cities")
        return queryset

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return CountryDetailSerializer
        return CountrySerializer


class CityViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = City.objects.all().select_related("country").prefetch_related("airports")
    serializer_class = CitySerializer

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return CityListSerializer
        return CitySerializer
