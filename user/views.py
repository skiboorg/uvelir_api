import json

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from .models import *
from rest_framework import generics, viewsets, parsers
from .services import send_tg_mgs


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

