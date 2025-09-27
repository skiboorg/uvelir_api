from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics

from cart.views import get_cart
from .serializers import *
from .models import *

from django.core.mail import send_mail
from django.template.loader import render_to_string

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
        have_bad_items = False
        cart = get_cart(request)
        status,_ = Status.objects.get_or_create(is_default=True, name='Новый')
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
            price = 0
            if request.user.is_authenticated and request.user.is_opt_user:
                price = item.size.price_opt
            else:
                price = item.size.price

            if item.product.images.exists():
                image = item.product.images.first().file
            else:
                image = None
            OrderItem.objects.create(
                order=new_order,
                article=item.product.article,
                image=image,
                name=item.product.name,
                avg_weight=item.size.avg_weight,
                amount=item.amount,
                price=price,
                size=item.size.size,
            )
            item.delete()


        result = {'success': True, 'message': new_order.id}

        msg_html = render_to_string('order.html', {'order': new_order})
        email_list = [new_order.email,'stepenina@mail.ru']
        # email_list = ['greshnik.im@gmail.com']
        send_mail('Новый заказ', None, 'noreply@sh44.ru',
                  email_list,
                  fail_silently=False, html_message=msg_html)

        return Response(result, status=200)


class GetDeliveries(generics.ListAPIView):
    serializer_class = DeliverySerializer
    queryset = Delivery.objects.all()

class GetPayments(generics.ListAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()