from rest_framework.serializers import ModelSerializer

from foodcartapp.models import OrderItem, Order


class ProductsSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = ProductsSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = ['products', 'firstname', 'lastname', 'phonenumber', 'address']
