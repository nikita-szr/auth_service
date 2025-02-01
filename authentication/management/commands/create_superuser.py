from django.core.management import BaseCommand
from auth_service.authentication.models import User


class Command(BaseCommand):
    help = "Создание суперпользователя с указанным номером телефона"

    def add_arguments(self, parser):
        parser.add_argument('phone', type=str, help="Номер телефона суперпользователя")
        parser.add_argument('password', type=str, help="Пароль суперпользователя")

    def handle(self, *args, **kwargs):
        phone = kwargs['phone']
        password = kwargs['password']

        if User.objects.filter(phone=phone).exists():
            self.stdout.write(self.style.ERROR(f"Пользователь с номером {phone} уже существует"))
            return

        user = User.objects.create(phone=phone, is_active=True, is_staff=True, is_superuser=True)
        user.set_password(password)
        user.save()

        self.stdout.write(self.style.SUCCESS(f"Суперпользователь {phone} успешно создан"))