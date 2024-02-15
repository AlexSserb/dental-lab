from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model

import uuid 
from decimal import Decimal, getcontext
import pghistory


User = get_user_model()

DECIMAL_PRECISION = 9
getcontext().prec = DECIMAL_PRECISION


# Справочник видов операций
class OperationType(models.Model):
    class OperationGroup(models.TextChoices):
        MODELS = 'MO', 'Модели'
        CAD_CAM = 'CA', 'CAD\CAM'
        CERAMICS = 'CE', 'Керамика'
        DENTURES = 'DE', 'Протезы'

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    name = models.CharField(max_length=128)
    exec_time = models.TimeField(auto_now=False, auto_now_add=False)
    group = models.CharField(
        max_length=2,
        choices=OperationGroup.choices,
        default=OperationGroup.MODELS,
    )

    class Meta:
        verbose_name = "Тип операции"
        verbose_name_plural = "Типы операций"

    def get_group(self):
        return self.OperationGroup(self.group).label

    def __str__(self):
        return f'{self.name}, группа: {self.get_group()}'


# Справочник видов изделий
class ProductType(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    name = models.CharField(max_length=128)
    operation_types = models.ManyToManyField(OperationType, related_name='product_types')
    cost = models.DecimalField(max_digits=DECIMAL_PRECISION, decimal_places=2, default=0.0)

    class Meta:
        verbose_name = "Тип изделия"
        verbose_name_plural = "Типы изделий"

    def __str__(self):
        return f'{self.name}'


# Статусы операций
class OperationStatus(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    number = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=128)

    class Meta:
        verbose_name = "Статус операции"
        verbose_name_plural = "Статусы операций"

    def __str__(self):
        return f'{self.name}'

    @staticmethod
    def get_default_status():
        status = OperationStatus.objects.filter(number=1).first()
        if not status:
            status = OperationStatus.objects.create(name='Default status', number=1)
        return status


# Статусы операций
class ProductStatus(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    number = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=128)

    class Meta:
        verbose_name = "Статус изделия"
        verbose_name_plural = "Статусы изделий"

    def __str__(self):
        return f'{self.name}'

    @staticmethod
    def get_default_status():
        status = ProductStatus.objects.filter(number=1).first()
        if not status:
            status = ProductStatus.objects.create(name='Default status', number=1)
        return status


class OrderStatus(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    number = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=128)

    class Meta:
        verbose_name = "Статус заказа"
        verbose_name_plural = "Статусы заказов"

    def __str__(self):
        return f'{self.name}'

    @staticmethod
    def get_default_status():
        status = OrderStatus.objects.filter(number=1).first()
        if not status:
            status = OrderStatus.objects.create(name='Default status', number=1)
        return status


# Заказы
class Order(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    user = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    status = models.ForeignKey(OrderStatus, related_name='orders', on_delete=models.CASCADE)
    order_date = models.DateField(auto_now=True)
    discount = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f'Заказ для {self.user.last_name} {self.user.first_name}, дата создания: {self.order_date}'

    def get_cost(self) -> float:
        products = Product.objects.filter(order=self).all()
        cost = sum((product.get_cost() for product in products))
        return round(cost, 2)

    def get_cost_with_discount(self) -> float:
        cost = self.get_cost()
        return round(cost * Decimal((1 - self.discount)), 2)

    
# История изменения статусов заказов
BaseOrderEvent = pghistory.create_event_model(Order, fields=['status'])
class OrderEvent(BaseOrderEvent):
    def get_order_status(self) -> OrderStatus:
        return OrderStatus.objects.get(id=self.status_id)


# Изделия
class Product(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    product_type = models.ForeignKey(ProductType, related_name='products', on_delete=models.CASCADE)
    product_status = models.ForeignKey(ProductStatus, related_name='products', on_delete=models.CASCADE)
    order = models.ForeignKey(Order, related_name='products', on_delete=models.CASCADE)
    amount = models.IntegerField(default=1)
    discount = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)

    class Meta:
        verbose_name = "Изделие"
        verbose_name_plural = "Изделия"

    def __str__(self):
        return f'Изделие "{self.product_type.name}" для заказа от даты {self.order.order_date}'

    @staticmethod
    def products_from_product_types(product_types: list[dict], order: Order):
        for product_type in product_types:
            product_type_id = product_type.get("product_type_id", None)
            teeth = product_type.get('teeth', None)
            amount = product_type.get('amount', None)

            if  product_type_id and amount and teeth and type(teeth) is list:
                product_type_inst = ProductType.objects.filter(id=product_type_id).first()
                
                if not product_type_inst:
                    print('Указан несуществующий тип изделия.')
                    continue
            
                product = Product.objects.create(product_type=product_type_inst, amount=amount,
                    order=order, product_status=ProductStatus.get_default_status())

                for tooth in teeth:
                    Tooth.objects.create(product=product, tooth_number=tooth)
            else:
                print('Переданы некорректные данные об изделиях.')

    def get_cost(self):
        return round(self.product_type.cost * self.amount * (1 - self.discount), 2)


# История изменения статусов изделий
BaseProductEvent = pghistory.create_event_model(Product, fields=['product_status'])
class ProductEvent(BaseProductEvent):
    def get_product_status(self) -> ProductStatus:
        return ProductStatus.objects.get(id=self.product_status_id)


# Отметка для зуба
class Tooth(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    product = models.ForeignKey(Product, related_name='teeth', on_delete=models.CASCADE)
    tooth_number = models.PositiveIntegerField(validators=[MinValueValidator(11), MaxValueValidator(48)])
    
    class Meta:
        verbose_name = "Отмеченный зуб"
        verbose_name_plural = "Отмеченные зубы"

    def __str__(self):
        return f'Зуб под номером {self.tooth_number} для изделия "{self.product.product_type.name}"'


# Операции
class Operation(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    operation_type = models.ForeignKey(OperationType, related_name='operations', on_delete=models.CASCADE)
    operation_status = models.ForeignKey(OperationStatus, related_name='operations', on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, related_name='operations', on_delete=models.CASCADE)
    tech = models.ForeignKey(User, related_name='operations', null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Операция"
        verbose_name_plural = "Операции"

    def __str__(self):
        return f'Операция "{self.operation_type.name}" для изделия "{self.product.product_type}" от даты {self.product.order.order_date}'


# История изменения статусов операций
BaseOperationEvent = pghistory.create_event_model(Operation, fields=['operation_status'])
class OperationEvent(BaseOperationEvent):
    def get_operation_status(self) -> OperationStatus:
        return OperationStatus.objects.get(id=self.operation_status_id)
