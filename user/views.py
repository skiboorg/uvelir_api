import json

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from .models import *
from rest_framework import generics, viewsets, parsers
from .services import send_tg_mgs, generate_password

import logging
logger = logging.getLogger(__name__)



class GetUser(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class NewCallbackForm(generics.CreateAPIView):
    serializer_class = CallbackFormSerializer
    queryset = CallbackForm.objects.all()

class ResetPassword(APIView):
    def post(self, request):
        email = request.data.get('email', None)
        user_qs = User.objects.filter(email=email)
        if not user_qs.exists():
            return Response({'success': False}, status=status.HTTP_200_OK)
        random_password = generate_password()
        print(random_password)
        user = user_qs.first()
        user.set_password(random_password)
        user.save()
        msg_html = render_to_string('reset.html', {'password': random_password})
        send_mail('Восстановление пароля', None, 'noreply@sh44.ru', [user.email],
                  fail_silently=False, html_message=msg_html)
        return Response({'success': True}, status=status.HTTP_200_OK)


class ActivateUser(APIView):
    def post(self, request):
        print(request.data)
        token = request.data.get('token', None)
        if token is None:
            return Response({'success': False}, status=status.HTTP_200_OK)
        user_qs = User.objects.filter(activate_token=token)
        if user_qs.exists():

            user = user_qs.first()
            is_active = user.is_active
            user.is_active = True
            user.save(update_fields=['is_active'])
        else:
            return Response({'success': False}, status=status.HTTP_200_OK)
        return Response(
            {'success': True,
             'message':"Ваш аккаунт уже был успешно активирован ранее, вы можете авторизоваться на нашем сайте" if is_active else "Ваш аккаунт был успешно активирован, вы можете авторизоваться на нашем сайте"
             }, status=status.HTTP_200_OK)

class UpdateUser(APIView):
    def patch(self, request):
        print(request.data)
        serializer = UserSerializer(instance=request.user, data=request.data)
        password = request.data.get('password', None)
        if serializer.is_valid():
            user = serializer.save()
            if password:
                user.set_password(password)
                user.save()

        return Response(status=status.HTTP_200_OK)

