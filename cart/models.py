from decimal import Decimal

from django.db import models

class Cart(models.Model):
    session_uuid = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, blank=True, null=True)

    @property
    def total_price(self):
        price = 0
        for item in self.items.all():
            price += Decimal(item.size.price) * item.amount
        return price

    @property
    def total_opt_price(self):
        price = 0
        for item in self.items.all():
            price += Decimal(item.size.price_opt) * item.amount
        return price


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, blank=True, null=True, related_name='items')
    product = models.ForeignKey('shop.Product', on_delete=models.CASCADE, blank=True, null=True)
    size = models.ForeignKey('shop.Size', on_delete=models.CASCADE, blank=True, null=True)
    amount = models.DecimalField(default=0,decimal_places=2,max_digits=8, blank=True, null=True)

    @property
    def total_price(self):
        price = Decimal(self.size.price) * self.amount
        return price