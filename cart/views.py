from decimal import Decimal

from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import *
from .models import *

def get_cart(request) -> Cart:
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        session_id = request.query_params.get('session_uuid', None)
        print('session_uuid',session_id)
        cart, _ = Cart.objects.get_or_create(session_uuid=session_id)
    return cart

class CartDel(APIView):
    def get(self, request):
        Cart.objects.filter(user__isnull=True).delete()
        return Response(status=200)
class CartView(APIView):
    def get(self, request):
        cart = get_cart(request)
        serializer = CartSerializer(cart, many=False)
        return Response(serializer.data, status=200)


    def delete(self, request):
        cart = get_cart(request)
        cart.delete()
        get_cart(request)
        result = {'result': True,'message':'Корзина очищена'}
        return Response(result, status=200)

    def patch(self, request):
        print(request.data)
        item = CartItem.objects.get(id=request.data['cart_item_id'])
        amount = Decimal(request.data['new_amount'])
        if amount > 0:
            item.amount = amount
            item.save()
        else:
            item.delete()
        result = {}
        return Response(result,status=200)

    def post(self, request):
        print(request.data)
        cart = get_cart(request)
        result = {'result': False, 'message': 'Ошибка добавления в корзину'}
        for item in request.data:
            print(item)
            cart_item,created = CartItem.objects.get_or_create(
                cart=cart,
                product_id=item['product'],
                size_id=item['id']
            )

            if created:
                print('created')
                cart_item.amount = item['selected_amount']
                cart_item.save()
                result = {'result': True, 'message': 'Товары добавлены'}
            else:
                print('updated')
                cart_item.amount += Decimal(item['selected_amount'])
                cart_item.save()
                result = {'result': True, 'message': 'Корзина изменена'}

        return Response(result, status=200)


