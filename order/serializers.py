from rest_framework import serializers
from .models import *

from shop.serializers import ProductShortSerializer
class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductShortSerializer(many=False, read_only=True)
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True, required=False)
    class Meta:
        model = Order
        fields = '__all__'
