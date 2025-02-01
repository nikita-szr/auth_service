from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.exceptions import ErrorDetail

from authentication.models import User
from authentication.services import InviteCodeGenerator

import random


class UserTest(APITestCase):
    """Тест регистрации пользователя"""

    def setUp(self):
        self.user = User.objects.create(
            phone="79000000000",
            invite_code="12Hk1p",
            email="dan@ya.ru",
            city="Kurchatov",
            is_superuser=True,
            is_staff=True,
        )
        self.user1 = User.objects.create(
            phone="79000000001", invite_code="CJ56781", invite_input="90ty7U"
        )

    def test_user_create(self):
        url = reverse("users:login")
        data = {
            "phone": "79000000002",
            "invite_code": "CJ56781",
            "city": "Samara",
            "email": "nikita@gmail.com",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.all().count(), 3)

    def test_user_update(self):
        """Тест обновления полей пользователя"""
        self.user.email = "nikita@gmail.com"
        self.user.invite_input = "90ty7U"
        self.user.city = "Samara"
        self.user.save()
        self.assertEqual(self.user.email, "nikita@gmail.com")
        self.assertEqual(self.user.invite_input, "90ty7U")
        self.assertEqual(self.user.city, "Samara")

    def test_create_invite_code(self):
        """Тест генерации кода авторизации"""
        code = InviteCodeGenerator().generate()
        self.assertTrue(len(code) == 6)
        self.assertFalse(code.isdigit())

    def test_user_delete(self):
        """Тест удаления пользователя"""
        self.client.force_authenticate(user=self.user)
        url = reverse("users:user_delete", args=(self.user1.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.all().count(), 1)

    def test_user_list(self):
        """Тест списка пользователей"""
        self.client.force_authenticate(user=self.user)
        url = reverse("users:user_list")
        response = self.client.get(url)
        data = response.json()
        result = [
            {
                "id": self.user.pk,
                "phone": self.user.phone,
                "email": self.user.email,
                "city": self.user.city,
                "invite_code": self.user.invite_code,
                "invite_input": self.user.invite_input,
                "invitation_list": [{"id": self.user1.pk, "phone": self.user1.phone}],
            },
            {
                "id": self.user1.pk,
                "phone": self.user1.phone,
                "email": self.user1.email,
                "city": self.user1.city,
                "invite_code": self.user1.invite_code,
                "invite_input": self.user1.invite_input,
                "invitation_list": [],
            },
        ]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, result)


class UserConfirmEmailCode(APITestCase):
    url = reverse('users:confirm')
    phone_number = '79277771079'
    sms_code = str(random.randint(1000, 9999))

    def setUp(self):
        self.user = User.objects.create(phone=self.phone_number, invite_code='Y2u7i9', sms=self.sms_code)

    def test_failed_if_sms_not_set(self):
        response = self.client.post(self.url, {'phone': self.phone_number})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.data, {'sms': [ErrorDetail(string='Обязательное поле.', code='required')]})

    def test_phone_not_found(self):
        response = self.client.post(self.url, {'phone': '79999999999', 'sms': self.sms_code})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_sms_code(self):
        response = self.client.post(self.url, {'phone': self.phone_number, 'sms': '000000'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.data, {'sms': ErrorDetail(string='Неправильный смс-код', code='invalid')})

    def test_login_on_site_if_sms_is_valid(self):
        response = self.client.post(self.url, {'phone': self.phone_number, 'sms': self.sms_code})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, {'id': self.user.id, 'phone': self.phone_number})
        self.assertTrue(response.wsgi_request.user.is_authenticated)
