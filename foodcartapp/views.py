import phonenumbers
from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Order, OrderItem, Product


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    fields = ('products', 'firstname', 'lastname', 'phonenumber', 'address')
    incorrect_fields = []
    for field in fields:
        if field not in request.data or request.data[field] is None or request.data[field] == []:
            incorrect_fields.append(field)

    if incorrect_fields:
        content = {'error': f'{", ".join(incorrect_fields)} is/are not specified or not str'}

        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    else:
        products = request.data['products']
        firstname = request.data['firstname']
        lastname = request.data['lastname']
        phonenumber = request.data['phonenumber']
        address = request.data['address']

        if isinstance(products, list) and products != []:
            for product in products:
                if not product['product'] <= Product.objects.last().id:
                    content = {'error': f'products: not allowed the key {product["product"]}'}

                    return Response(content, status=status.HTTP_400_BAD_REQUEST)

            parsed_phonenumber = phonenumbers.parse(phonenumber, 'RU')
            valid_phonenumber = phonenumbers.is_valid_number(parsed_phonenumber)
            if phonenumber == '' or not valid_phonenumber:
                content = {'error': f'phonenumber {phonenumber} is not valid'}

                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            else:
                order = Order.objects.create(
                    firstname=firstname,
                    lastname=lastname,
                    phonenumber=phonenumber,
                    address=address
                )
                for product in products:
                    OrderItem.objects.create(
                        order=order,
                        product=Product.objects.get(id=product['product']),
                        quantity=product['quantity']
                    )

                return Response({}, status=status.HTTP_200_OK)
        else:
            content = {'error': 'products are not presented or not a list'}

            return Response(content, status=status.HTTP_400_BAD_REQUEST)
