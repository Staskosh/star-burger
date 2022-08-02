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


def handle_place(places, place_address):
    place_coordinates = [[place.lon, place.lat] for place in places
                         if place.address == place_address]
    if not place_coordinates:
        place_coordinates = fetch_coordinates(place_address)
        if place_coordinates:
            lon, lat = place_coordinates
            Place.objects.get_or_create(
                address=place_address,
                lon=lon,
                lat=lat,
            )

            return lon, lat
    else:
        place_coordinates, *_ = place_coordinates
        lon, lat = place_coordinates

        return lon, lat
