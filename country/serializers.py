from rest_framework import serializers

from country.models import City, Country


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ("id", "name", "country", "airports")


class CityListRetrieveSerializer(CitySerializer):
    country = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="name"
    )
    airports = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )


class CityDetailSerializer(CitySerializer):
    country = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="name"
    )

    class Meta:
        model = City
        fields = ("id", "name", "country")


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ("id", "name")


class CountryListRetrieveSerializer(CountrySerializer):
    cities = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")

    class Meta:
        model = Country
        fields = ("id", "name", "cities")
