from rest_framework.exceptions import ValidationError


class PhoneValidator:

    def __init__(self, phone):

        self.phone = phone

    def __call__(self, value):

        number = dict(value).get(self.phone)
        if number[0:2] != "79" or not number.isdigit() or len(number) != 11:
            raise ValidationError("Введите номер в формате 79XXXXXXXX")


def phone_validator(phone_number):
    if phone_number[0:2] != "79" or not phone_number.isdigit() or len(phone_number) != 11:
        raise ValidationError("Введите номер в формате 79XXXXXXXX")