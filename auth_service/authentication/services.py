import random
import string

from auth_service.authentication.models import User


class InviteCodeGenerator:
    """Генератор инвайт-кодов с валидацией"""

    def __init__(self, length=10, min_digits=3):
        self.length = length
        self.min_digits = min_digits
        self.characters = string.ascii_letters + string.digits

    def generate(self):
        """Генерирует новый инвайт-код"""
        while True:
            invite_code = ''.join(random.choices(self.characters, k=self.length))

            if self.is_valid(invite_code):
                return invite_code

    def is_valid(self, invite_code):
        """Проверяет, соответствует ли код требованиям"""
        return (
            any(c.isupper() for c in invite_code) and
            any(c.islower() for c in invite_code) and
            sum(c.isdigit() for c in invite_code) >= self.min_digits and
            not User.objects.filter(invite_code=invite_code).exists()
        )
