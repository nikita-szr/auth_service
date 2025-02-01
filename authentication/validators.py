from rest_framework.exceptions import ValidationError
from authentication.models import User


class PhoneValidator:
    """Проверят корректность ввода номера"""

    def __init__(self, phone):

        self.phone = phone

    def __call__(self, value):

        number = dict(value).get(self.phone)
        if number[0:2] != "79" or not number.isdigit() or len(number) != 11:
            raise ValidationError("Введите номер в формате 79XXXXXXXX")


def phone_validator(phone_number):
    if phone_number[0:2] != "79" or not phone_number.isdigit() or len(phone_number) != 11:
        raise ValidationError("Введите номер в формате 79XXXXXXXX")


class InviteInputValidator:
    """Проверят корректность ввода инвайт кода"""

    def __init__(self, invite_input, phone):
        self.invite_input = invite_input
        self.users = User.objects.all()
        self.phone = phone

    def __call__(self, value):
        invite_code_input = dict(value).get(self.invite_input)
        user_phone = dict(value).get(self.phone)
        user = self.users.filter(phone=user_phone).first()
        if user.invite_input:
            if invite_code_input:
                raise ValidationError("Пригласительный код уже использован")
        else:
            if invite_code_input:
                if user.invite_code == invite_code_input:
                    raise ValidationError("Нельзя использовать Ваш собственный пригласительный код")
                elif not self.users.filter(invite_code=invite_code_input).exists():
                    raise ValidationError("Пригласительный код не найден")
