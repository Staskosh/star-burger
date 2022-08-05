import requests
from django.conf import settings

from places.models import Place


def fetch_coordinates(address):
    apikey = settings.YA_API_KEY
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']
    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def get_serialized_places_and_coordinates(order_places):
    serialized_places_and_coordinates = {}
    places_and_coordinates = {}
    for place in Place.objects.filter(address__in=order_places):
        places_and_coordinates[place.address] = [place.lon, place.lat]

    for place in order_places:
        if place not in places_and_coordinates:
            place_coordinates = fetch_coordinates(place)
            serialized_places_and_coordinates[place] = None
            if place_coordinates:
                lon, lat = place_coordinates
                Place.objects.get_or_create(
                    address=place,
                    lon=lon,
                    lat=lat,
                )
                serialized_places_and_coordinates[place] = [place_coordinates]
        else:
            serialized_places_and_coordinates[place] = places_and_coordinates[place]

    return serialized_places_and_coordinates
