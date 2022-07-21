from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Sum
from django.utils.timezone import now
from phonenumber_field.modelfields import PhoneNumberField
from rest_framework.serializers import ModelSerializer


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def with_amount(self):
        amount = self.annotate(
            amount=Sum(F('items__price') * F('items__quantity')))

        return amount

    def with_are_able_to_cook_restaurants(self):
        orders_ids = self.filter(items__product__menu_items__availability=True).values_list('id', flat=True)
        orders = self.select_related('responsible_restaurant')\
            .prefetch_related('items__product__menu_items__restaurant')\
            .filter(id__in=orders_ids, status__in=['Unprocessed', 'In_procces'])\
            .order_by('responsible_restaurant_id')
        for order in orders:
            available_restaurants = []
            filtered_order_items = order.items.all()
            for order_item in filtered_order_items:
                restaurants = []
                filtered_restaurant_items = order_item.product.menu_items.all()
                for restaurant_item in filtered_restaurant_items:
                    restaurants.append(restaurant_item.restaurant)
                available_restaurants.append(restaurants)
            are_able_to_cook_restaurants = list(set.intersection(*map(set, available_restaurants)))
            order.are_able_to_cook_restaurants = are_able_to_cook_restaurants
        return orders


class Order(models.Model):
    STATUSES = (
        ('Unprocessed', 'Необработанный'),
        ('In_procces', 'В работе'),
        ('Сompleted', 'Завершен'),
    )
    PAYMENT_OPTIONS = (
        ('Online', 'Электронно'),
        ('Cash', 'Наличность'),
        ('Unknown', 'Неизвестно'),
    )
    firstname = models.CharField(
        'Имя',
        max_length=50
    )
    lastname = models.CharField(
        'Фамилия',
        max_length=50,
    )
    phonenumber = PhoneNumberField(
        'Телефон',
        db_index=True
    )
    address = models.CharField(
        'Адрес',
        max_length=250,
        db_index=True
    )
    status = models.CharField(
        'Статус заказа',
        max_length=15,
        choices=STATUSES,
        default='Unprocessed',
        db_index=True
    )
    comment = models.TextField(
        'Комментарий',
        blank=True
    )
    registered_at = models.DateTimeField(
        'Время регистрации заказа',
        default=now,
        db_index=True
    )
    called_at = models.DateTimeField(
        'Время звонка',
        blank=True,
        null=True,
        db_index=True
    )
    delivered_at = models.DateTimeField(
        'Время доставки',
        blank=True,
        null=True,
        db_index=True
    )
    payment_option = models.CharField(
        'Способ оплаты',
        max_length=15,
        choices=PAYMENT_OPTIONS,
        default='Unknown',
        db_index=True
    )
    responsible_restaurant = models.ForeignKey(
        Restaurant,
        related_name='orders',
        verbose_name="Ответственный за готовку ресторан",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'{self.id} {self.firstname} {self.lastname}, {self.address}'


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='items',
        verbose_name="заказ",
        on_delete=models.CASCADE,
        db_index=True
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name='продукт',
    )
    quantity = models.IntegerField(
        'Количество',
        validators=[MinValueValidator(1)]
    )
    price = models.DecimalField(
        'Стоимость позиции заказа',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'Элемент  заказа'
        verbose_name_plural = 'Элементы заказа'

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"


class ProductsSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = ProductsSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = ['products', 'firstname', 'lastname', 'phonenumber', 'address']
