from rest_framework import serializers

from country.models import City, Country


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ("id", "name", "country")


class CityDetailSerializer(CitySerializer):
    country = serializers.SlugRelatedField(many=False, read_only=True, slug_field="name")


class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = ("id", "name")

