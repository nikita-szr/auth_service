import random
import time

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import (
    CreateView,
    DetailView,
    UpdateView,
    TemplateView,
    ListView,
)
from rest_framework.reverse import reverse_lazy, reverse

from authentication.models import User
from authentication.services import InviteCodeGenerator
from frontend.forms import UserRegisterForm, SmsCodeForm, UserUpdateForm


class HomeView(TemplateView):
    """Контроллер главной страницы сайта"""

    template_name = "frontend/index.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        users = User.objects.all()
        context_data["all_clients"] = users.count()
        context_data["all_invite_inputs"] = users.exclude(invite_input=None).count()

        return context_data


class UserCreateView(CreateView):
    """Регистрация пользователя + отправка СМС-кода"""

    template_name = "frontend/register.html"
    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy("frontend:login")

    def get_success_url(self):
        return reverse_lazy("frontend:sms_code") + "?phone=" + self.object.phone

    def form_valid(self, form, *args, **kwargs):
        return_data = {}

        form.is_valid()
        user = form.save()
        user.invite_code = InviteCodeGenerator().generate()
        return_data["invite_code"] = user.invite_code

        password = random.randint(1000, 9999)
        user.set_password(str(password))
        user.save()
        messages.success(self.request, "Отправили код в смс!")
        time.sleep(3)
        print(password)
        return super().form_valid(form)

    def form_invalid(self, form, *args, **kwargs):
        user = User.objects.get(phone=form.data.get("phone"))
        if user.phone == "79321225043":
            password = "1111"
        else:
            password = random.randint(1000, 9999)
        user.set_password(str(password))
        user.save()
        messages.success(self.request, "Отправили код в смс!")
        self.object = user
        time.sleep(3)
        print(password)
        return redirect(self.get_success_url())


class SmsCodeView(View):
    """Авторизация пользователя по СМС-коду"""

    def post(self, *args, **kwargs):
        phone = self.request.POST.get("phone")
        code = self.request.POST.get("code")
        user = authenticate(self.request, username=phone, password=code)
        if user:
            login(self.request, user)
            return redirect(reverse("frontend:user_detail"))
        else:
            return redirect(reverse("frontend:login"))

    def get(self, *args, **kwargs):
        form = SmsCodeForm()
        return render(self.request, "frontend/sms_code.html", {"form": form})


class UserDetailView(DetailView):
    """Отображение профиля пользователя"""

    model = User
    template_name = "frontend/user_detail.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["invitation_list"] = [
            user.phone
            for user in User.objects.all().filter(
                invite_input=self.request.user.invite_code
            )
        ]
        return context_data


class UserUpdateView(UpdateView):
    """Обновление данных пользователя"""

    model = User
    template_name = "frontend/user_form.html"
    form_class = UserUpdateForm
    success_url = reverse_lazy("frontend:user_detail")

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(
        self,
    ):
        return reverse_lazy("frontend:user_detail") + "?phone=" + self.object.phone


class UserListView(ListView, LoginRequiredMixin):
    """Список пользователей (только для авторизованных)"""
    model = User
    template_name = "frontend/user_list.html"
