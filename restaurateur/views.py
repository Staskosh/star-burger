import requests
from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from foodcartapp.models import (
    Order,
    OrderItem,
    Product,
    Restaurant,
    RestaurantMenuItem,
)
from geopy import distance
from places.models import Place


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    default_availability = {restaurant.id: False for restaurant in restaurants}
    products_with_restaurants = []
    for product in products:

        availability = {
            **default_availability,
            **{item.restaurant_id: item.availability for item in product.menu_items.all()},
        }
        orderer_availability = [availability[restaurant.id] for restaurant in restaurants]

        products_with_restaurants.append(
            (product, orderer_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurants': products_with_restaurants,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


def fetch_coordinates(address):
    apikey = settings.API_KEY_YA
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
            new_place = Place.objects.get_or_create(
                address=place_address,
                lon=lon,
                lat=lat,
            )

            return lon, lat
    else:
        place_coordinates, *_ = place_coordinates
        lon, lat = place_coordinates

        return lon, lat


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = {}
    db_orders = Order.objects.with_amount().prefetch_related('responsible_restaurant')\
        .filter(status__in=['Unprocessed', 'In_procces']).order_by('responsible_restaurant_id')
    db_orders_addresses = [db_orders_address.address for db_orders_address in db_orders]
    places = [place for place in Place.objects.filter(address__in=db_orders_addresses)]
    for order in db_orders:
        available_restaurants = []
        filtered_order_items = order.items.all()
        for order_item in filtered_order_items:
            restaurants = []
            filtered_restaurant_items = order_item.product.menu_items.all()
            for restaurant_item in filtered_restaurant_items:
                restaurants.append(restaurant_item.restaurant)
            available_restaurants.append(restaurants)
        are_able_to_cook_restaurants = list(set.intersection(*map(set, available_restaurants)))
        restaurants_details = {}

        for is_able_to_cook_restaurant in are_able_to_cook_restaurants:
            if not handle_place(places, order.address) or not handle_place(places, is_able_to_cook_restaurant.address):
                restaurants_and_order_distance = None
            else:
                restaurants_and_order_distance = round(
                    distance.distance(
                        handle_place(places, order.address),
                        handle_place(places, is_able_to_cook_restaurant.address)
                    ).km, 3)
            restaurants_details[is_able_to_cook_restaurant] = restaurants_and_order_distance
        sorted_restaurants_details = {
            restaurant: restaurants_details[restaurant]
            for restaurant in sorted(restaurants_details, key=restaurants_details.get)
        }
        orders[order] = {
            'restaurants_details': sorted_restaurants_details,
            'order_amount': order.amount
        }

    return render(request, template_name='order_items.html', context={
        'orders': orders
    })
