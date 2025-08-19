from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import CustomUser


class RegisterView(CreateView):
    template_name = "users/register.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("mailing:home")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        self.send_welcome_email(user.email)
        return super().form_valid(form)

    def send_welcome_email(self, user_email):
        subject = "Добро пожаловать в наш сервис"
        message = "Спасибо, что зарегистрировались в нашем сервисе!"
        from_email = "awesome.gauf@yandex.ru"
        send_mail(subject, message, from_email, [user_email])


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = "users/profile_edit.html"
    success_url = reverse_lazy("mailing:home")

    def get_object(self, queryset=None):
        return self.request.user


class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = CustomUser
    template_name = "users/user_list.html"
    context_object_name = "users"

    def test_func(self):
        return self.request.user.groups.filter(name="Менеджеры").exists()


class UserBlockView(LoginRequiredMixin, UserPassesTestMixin, View):
    def post(self, request, pk):
        user = CustomUser.objects.get(pk=pk)
        user.is_blocked = not user.is_blocked
        user.save()
        messages.success(
            request,
            f"Пользователь {user.email} {'заблокирован' if user.is_blocked else 'разблокирован'}",
        )
        return redirect("users:user_list")

    def test_func(self):
        return self.request.user.groups.filter(name="Менеджеры").exists()
