
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from django.db import IntegrityError, transaction
from django.contrib.auth.tokens import default_token_generator

from rest_framework import exceptions, serializers, status, generics
from .models import *
from djoser.conf import settings

from order.serializers import OrderSerializer
import logging
logger = logging.getLogger(__name__)






class CallbackFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallbackForm
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    orders = OrderSerializer(many=True, read_only=True)
    favorites = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = [
            "id",
            "fio",
            "phone",
            'email',
            'orders',
            'is_opt_user',
            'is_staff',
            'favorites'

        ]

        extra_kwargs = {
            'password': {'required': False},

        }
    def get_favorites(self, obj):
        result = []
        for favorite in obj.favorites.all():
            result.append(favorite.product.id)
        return result


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)

    default_error_messages = {
        "cannot_create_user": settings.CONSTANTS.messages.CANNOT_CREATE_USER_ERROR
    }

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            "fio",
            "phone",
            'email',
            'password',
        )

    def validate(self, attrs):
        user = User(**attrs)
        password = attrs.get("password")


        try:
            validate_password(password, user)
        except django_exceptions.ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            print(e)
            raise serializers.ValidationError(
                {"password": serializer_error["non_field_errors"]}
            )

        return attrs

    def create(self, validated_data):
        try:
            user = self.perform_create(validated_data)
        except IntegrityError:
            self.fail("cannot_create_user")

        return user

    def perform_create(self, validated_data):

        with transaction.atomic():
            user = User.objects.create_user(**validated_data)
            token = default_token_generator.make_token(user)
            user.is_active = False
            user.activate_token = token
            user.save(update_fields=["is_active","activate_token"])
            msg_html = render_to_string('activate.html', {'token': token})
            send_mail('Подтверждение регистрации аккаунта', None, 'noreply@sh44.ru', [user.email],
                      fail_silently=False, html_message=msg_html)
            msg_html = render_to_string('new_user.html', {'user': user})
            send_mail('Новый юзер', None, 'noreply@sh44.ru', ['stepenina@mail.ru'],
                      fail_silently=False, html_message=msg_html)

        return user


