from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from foodcartapp.models import (
    Order,
    Product,
    Restaurant,
)
from geopy import distance

from places.views import get_serialized_places_and_coordinates


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
        orders_availability = [availability[restaurant.id] for restaurant in restaurants]

        products_with_restaurants.append(
            (product, orders_availability)
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


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    serialized_orders = {}
    db_orders = Order.objects.with_amount().with_are_able_to_cook_restaurants()
    db_orders_addresses = [db_orders_address.address for db_orders_address in db_orders]
    restaurant_addresses = [restaurant.address for restaurant in Restaurant.objects.all()]
    serialized_places_and_coordinates = get_serialized_places_and_coordinates(
        db_orders_addresses + restaurant_addresses)
    for order in db_orders:
        restaurants_details = {}
        for is_able_to_cook_restaurant in order.are_able_to_cook_restaurants:
            if not serialized_places_and_coordinates[
                order.address
            ] or not serialized_places_and_coordinates[
                is_able_to_cook_restaurant.address
            ]:
                restaurants_and_order_distance = 0
            else:
                restaurants_and_order_distance = round(
                    distance.distance(
                        serialized_places_and_coordinates[order.address],
                        serialized_places_and_coordinates[is_able_to_cook_restaurant.address]
                    ).km, 3)
            restaurants_details[is_able_to_cook_restaurant] = restaurants_and_order_distance
        sorted_restaurants_details = {
            restaurant: restaurants_details[restaurant]
            for restaurant in sorted(restaurants_details, key=restaurants_details.get)
        }
        serialized_orders[order] = {
            'restaurants_details': sorted_restaurants_details,
            'order_amount': order.amount
        }

    return render(request, template_name='order_items.html', context={
        'orders': serialized_orders
    })
