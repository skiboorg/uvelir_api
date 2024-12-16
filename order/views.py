from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics

from cart.views import get_cart
from .serializers import *
from .models import *


class OrderView(APIView):
    def get(self, request):
        print(request.data)
        result = {}
        return Response(status=200)

    def delete(self, request):
        print(request.data)
        result = {}
        return Response(status=200)

    def patch(self, request):
        print(request.data)
        result = {}
        return Response(result,status=200)

    def post(self, request):
        data = request.data
        print(data)
        cart = get_cart(request)
        status,_ = Status.objects.get_or_create(is_default=True)
        if request.user.is_authenticated:
            user = request.user
        else:
            user = None
        new_order = Order.objects.create(
            user=user,
            fio=data['fio'],
            phone=data['phone'],
            email=data['email'],
            comment=data['comment'],
            status=status,
            payment_type_id=data['payment_type'],
            delivery_type_id=data['delivery_type'],
        )
        for item in cart.items.all():
            OrderItem.objects.create(
                order=new_order,
                article=item.product.article,
                image=item.product.image,
                name=item.product.name,
                avg_weight=item.size.avg_weight,
                amount=item.amount,
                price=item.size.price
            )
            item.delete()
        result = {'success': True, 'message': new_order.id}
        return Response(result, status=200)


class GetDeliveries(generics.ListAPIView):
    serializer_class = DeliverySerializer
    queryset = Delivery.objects.all()

class GetPayments(generics.ListAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()