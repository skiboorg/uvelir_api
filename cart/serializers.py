from rest_framework import serializers
from .models import *
from shop.serializers import SizeSerializer, ProductShortSerializer


class CartItemSerializer(serializers.ModelSerializer):
    size = SizeSerializer(read_only=True)
    product = ProductShortSerializer(read_only=True)
    total_price = serializers.ReadOnlyField()
    class Meta:
        model = CartItem
        fields = '__all__'
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True, required=False)
    class Meta:
        model = Cart
        fields = [
            'items',
            'total_price',
            'total_opt_price'
        ]
