from rest_framework.serializers import ModelSerializer, SerializerMethodField
from authentication.models import User
from authentication.validators import InviteInputValidator, PhoneValidator


class UserSerializer(ModelSerializer):
    """Сериализатор для базовой информации о пользователе"""
    class Meta:
        model = User
        fields = ("id", "phone")

        validators = [PhoneValidator(phone="phone")]


class UserUpdateSerializer(ModelSerializer):
    """Сериализатор для обновления данных пользователя"""
    class Meta:
        model = User
        fields = ("id", "email", "city", "invite_input", "phone")

        validators = [InviteInputValidator(invite_input="invite_input", phone="phone")]


class UserConfirmSerializer(ModelSerializer):
    """Сериализатор для подтверждения номера телефона"""
    class Meta:
        model = User
        fields = ("id", "phone", "sms")
        extra_kwargs = {'sms': {'required': True}}


class ProfileSerializer(ModelSerializer):
    """Сериализатор профиля пользователя с отображением приглашённых пользователей"""

    invitation_list = SerializerMethodField()

    def get_invitation_list(self, obj):
        """Возвращает список пользователей, которых пригласил текущий пользователь"""
        users = User.objects.filter(invite_input=obj.invite_code)
        return [{"id": user.pk, "phone": user.phone} for user in users]

    class Meta:
        model = User
        fields = ("id", "phone", "email", "city", "invite_code", "invite_input", "invitation_list")
