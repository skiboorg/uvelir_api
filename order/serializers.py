from rest_framework import serializers
from .models import *

from shop.serializers import ProductShortSerializer, SizeSerializer
class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = '__all__'




class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True, required=False)
    delivery_type = DeliverySerializer(many=False, read_only=True, required=False)
    status = StatusSerializer(many=False, read_only=True, required=False)
    total_price = serializers.ReadOnlyField()
    class Meta:
        model = Order
        fields = '__all__'
