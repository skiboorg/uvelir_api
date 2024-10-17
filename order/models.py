from django.db import models
from decimal import Decimal
from django_resized import ResizedImageField


class Delivery(models.Model):
    name = models.CharField('Название доставки',max_length=255)
    image = ResizedImageField(size=[800, 600], quality=95, force_format='WEBP', upload_to='shop/order/delivery',
                              blank=False, null=True)
    description = models.TextField('Описание доставки', blank=True, null=True)

    def __str__(self):
        return f'{self.name}'

    class Meta:

        verbose_name = 'Доставка'
        verbose_name_plural = 'Доставка'


class Payment(models.Model):
    name = models.CharField('Название оплаты', max_length=255)
    image = ResizedImageField(size=[800, 600], quality=95, force_format='WEBP', upload_to='shop/order/payment',
                              blank=False, null=True)
    description = models.TextField('Описание оплаты', blank=True, null=True)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Оплата'
        verbose_name_plural = 'Оплата'


class Order(models.Model):
    order_id = models.CharField('Номер заказа', max_length=255, blank=True, null=True)
    user = models.ForeignKey('user.User',on_delete=models.CASCADE,blank=True, null=True,verbose_name='Юзер', related_name='orders')
    email = models.CharField('Почта', max_length=255, blank=True, null=True)
    fio = models.CharField('ФИО', max_length=255, blank=True, null=True)
    phone = models.CharField('Телефон', max_length=255, blank=True, null=True)
    payment_type = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True,verbose_name='Оплата')
    delivery_type = models.ForeignKey(Delivery, on_delete=models.SET_NULL, blank=True, null=True,verbose_name='Доставка')
    delivery_address = models.TextField('адрес доставки', blank=True, null=True)
    created_at = models.DateField('Создан',auto_now_add=True, null=True)
    is_paid = models.BooleanField('Оплачен', default=False, null=False)
    is_done = models.BooleanField('Обработан', default=False, null=False)
    is_deliveried = models.BooleanField('Доставлен', default=False, null=False)
    comment = models.TextField('Коментарий', blank=True, null=True)

    def __str__(self):
        return f'{self.order_id}'

    @property
    def total_price(self):
        result = Decimal(0)
        for item in self.items.all():
            result += item.price
        print(result)
        return result
    class Meta:

        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'




class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True, related_name='items')
    article = models.CharField('Артикул', max_length=20, blank=True, null=True)
    image = models.FileField(upload_to='order/images', blank=False, null=True)
    name = models.CharField('Название', max_length=255, blank=False, null=True)
    avg_weight = models.DecimalField('Средний вес', decimal_places=4, max_digits=8, blank=True, null=True)
    amount = models.IntegerField(default=0, blank=True, null=True)
    price = models.DecimalField('Цена', decimal_places=2, max_digits=8, blank=True, null=True)

