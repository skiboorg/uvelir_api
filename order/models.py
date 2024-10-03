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
    customer = models.ForeignKey('user.User',on_delete=models.CASCADE,blank=False, null=True,verbose_name='Юзер', related_name='orders')
    payment_type = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True,verbose_name='Оплата')
    delivery_type = models.ForeignKey(Delivery, on_delete=models.SET_NULL, blank=True, null=True,verbose_name='Доставка')
    delivery_address = models.TextField('адрес доставки', blank=True, null=True)
    created_at = models.DateField('Создан',blank=True, null=True)
    is_paid = models.BooleanField('Оплачен', default=False, null=False)
    is_done = models.BooleanField('Обработан', default=False, null=False)
    is_deliveried = models.BooleanField('Доставлен', default=False, null=False)

    def __str__(self):
        return f'{self.order_id}'

    class Meta:

        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'




class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True, related_name='items')
    product = models.ForeignKey('shop.Product', on_delete=models.CASCADE, blank=True, null=True)
    amount = models.IntegerField(default=0, blank=True, null=True)

