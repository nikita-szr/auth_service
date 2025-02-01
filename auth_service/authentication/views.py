import random
import time

from django.contrib.auth import login

from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.validators import UniqueValidator

from auth_service.authentication.permissions import IsSelfUser
from auth_service.authentication.serializers import UserSerializer, ProfileSerializer, UserConfirmSerializer, UserUpdateSerializer
from auth_service.authentication.models import User
from auth_service.authentication.services import InviteCodeGenerator

from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError


class UserRegisterAPIView(generics.CreateAPIView):
    """Регистрация пользователя (если нет в БД — создаётся)"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.fields['phone'].validators = [
            v for v in serializer.fields['phone'].validators
            if not isinstance(v, UniqueValidator)
        ]
        serializer.is_valid(raise_exception=True)
        user, _ = User.objects.get_or_create(
            phone=serializer.validated_data['phone'],
            defaults={
                'invite_code': InviteCodeGenerator().generate()
            }
        )

        # возможно добавление api для реальной отправки sms
        sms = random.randint(100000, 999999)
        user.sms = str(sms)
        user.save()

        time.sleep(3)
        print(sms)

        return Response(data=UserSerializer(user).data, status=status.HTTP_201_CREATED)


class UserConfirmAPIView(generics.GenericAPIView):
    """Подтверждение номера телефона через SMS"""
    queryset = User.objects.all()
    serializer_class = UserConfirmSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserConfirmSerializer(data=request.data)
        serializer.fields['phone'].validators = [
            v for v in serializer.fields['phone'].validators
            if not isinstance(v, UniqueValidator)
        ]
        serializer.is_valid(raise_exception=True)

        user = get_object_or_404(User, phone=serializer.validated_data['phone'])
        if user.sms != serializer.validated_data['sms']:
            raise ValidationError({'sms': 'Неправильный смс-код'})

        login(self.request, user)
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)


class UserUpdateAPIView(generics.UpdateAPIView):
    """Обновление данных пользователя"""
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated, IsSelfUser]


class UserProfileAPIView(generics.RetrieveAPIView):
    """Получение профиля пользователя"""

    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsSelfUser | IsAdminUser]


class UserListAPIView(generics.ListAPIView):
    """Получение списка пользователей"""

    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAdminUser]


class UserDestroyAPIView(generics.DestroyAPIView):
    """Удаление пользователя"""

    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAdminUser]
