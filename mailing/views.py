from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.cache import cache
from django.core.mail import send_mail
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_control, cache_page
from django.views.decorators.http import require_POST
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  TemplateView, UpdateView)

from .forms import MailingForm, MessageForm, RecipientForm
from .models import Mailing, MailingAttempt, Message, Recipient


# HomeView
@method_decorator(cache_page(60 * 15), name="dispatch")  # Кеш страницы 15 минут
class HomeView(TemplateView):
    template_name = "mailing/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Общая статистика с низкоуровневым кешем
        total_mailings = cache.get("total_mailings")
        if total_mailings is None:
            total_mailings = Mailing.objects.count()
            cache.set("total_mailings", total_mailings, 60 * 5)

        active_mailings = cache.get("active_mailings_count")
        if active_mailings is None:
            active_mailings = Mailing.objects.filter(status="started").count()
            cache.set("active_mailings_count", active_mailings, 60 * 5)

        unique_recipients = cache.get("unique_recipients")
        if unique_recipients is None:
            unique_recipients = Recipient.objects.count()
            cache.set("unique_recipients", unique_recipients, 60 * 5)

        latest_active_mailings = cache.get("latest_active_mailings")
        if latest_active_mailings is None:
            latest_active_mailings = Mailing.objects.filter(status="started").order_by(
                "-start_time"
            )[:5]
            cache.set("latest_active_mailings", latest_active_mailings, 60 * 5)

        attempts_stats = cache.get("attempts_stats")
        if attempts_stats is None:
            attempts_stats = MailingAttempt.objects.aggregate(
                success_count=Count("id", filter=Q(status="success")),
                fail_count=Count("id", filter=Q(status="fail")),
            )
            cache.set("attempts_stats", attempts_stats, 60 * 5)

        context.update(
            {
                "total_mailings": total_mailings,
                "active_mailings": active_mailings,
                "unique_recipients": unique_recipients,
                "latest_active_mailings": latest_active_mailings,
                "success_count": attempts_stats["success_count"],
                "fail_count": attempts_stats["fail_count"],
            }
        )
        return context


# OwnerQuerysetMixin
class OwnerQuerysetMixin:
    """Фильтрует queryset по владельцу, если пользователь не менеджер."""

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_superuser or user.groups.filter(name="Менеджеры").exists():
            return qs  # Менеджеры и суперпользователи видят всё

        return qs.filter(owner=user)  # Обычные пользователи видят только своё


# Recipient CBV
class RecipientListView(LoginRequiredMixin, OwnerQuerysetMixin, ListView):
    model = Recipient
    template_name = "mailing/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Список получателей",
                "create_url": reverse_lazy("mailing:recipient-create"),
                "headers": ["ФИО", "Email", "Комментарий"],
                "fields": ["full_name", "email", "comment"],
                "update_url_name": "mailing:recipient-update",
                "delete_url_name": "mailing:recipient-delete",
            }
        )
        return context

    def test_func(self):
        return not self.request.user.groups.filter(name="Менеджеры").exists()


@method_decorator(
    cache_control(public=False, max_age=60), name="dispatch"
)  # 1 минута у клиента
class RecipientDetailView(LoginRequiredMixin, DetailView):
    model = Recipient

    def get_object(self, queryset=None):
        # Кешируем объект отдельно для текущего пользователя
        key = f"recipient_{self.kwargs['pk']}_user_{self.request.user.id}"
        recipient = cache.get(key)
        if recipient is None:
            recipient = super().get_object(queryset)
            cache.set(key, recipient, 60)  # 1 минута
        return recipient


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "mailing/form.html"
    success_url = reverse_lazy("mailing:recipient-list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = self.request.META.get(
            "HTTP_REFERER", reverse_lazy("mailing:recipient-list")
        )
        return context


class RecipientUpdateView(LoginRequiredMixin, OwnerQuerysetMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "mailing/form.html"
    success_url = reverse_lazy("mailing:recipient-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = self.request.META.get(
            "HTTP_REFERER", reverse_lazy("mailing:recipient-list")
        )
        return context

    def test_func(self):
        return not self.request.user.groups.filter(name="Менеджеры").exists()


class RecipientDeleteView(LoginRequiredMixin, OwnerQuerysetMixin, DeleteView):
    model = Recipient
    template_name = "mailing/confirm_delete.html"
    success_url = reverse_lazy("mailing:recipient-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = self.request.META.get(
            "HTTP_REFERER", reverse_lazy("mailing:recipient-list")
        )
        return context

    def test_func(self):
        return not self.request.user.groups.filter(name="Менеджеры").exists()


# Message CBV
class MessageListView(LoginRequiredMixin, OwnerQuerysetMixin, ListView):
    model = Message
    template_name = "mailing/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Список сообщений",
                "create_url": reverse_lazy("mailing:message-create"),
                "headers": ["Тема", "Текст"],
                "fields": ["subject", "body"],
                "update_url_name": "mailing:message-update",
                "delete_url_name": "mailing:message-delete",
            }
        )
        return context

    def test_func(self):
        return not self.request.user.groups.filter(name="Менеджеры").exists()


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/form.html"
    success_url = reverse_lazy("mailing:message-list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = self.request.META.get(
            "HTTP_REFERER", reverse_lazy("mailing:message-list")
        )
        return context


class MessageUpdateView(LoginRequiredMixin, OwnerQuerysetMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/form.html"
    success_url = reverse_lazy("mailing:message-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = self.request.META.get(
            "HTTP_REFERER", reverse_lazy("mailing:message-list")
        )
        return context

    def test_func(self):
        return not self.request.user.groups.filter(name="Менеджеры").exists()


class MessageDeleteView(LoginRequiredMixin, OwnerQuerysetMixin, DeleteView):
    model = Message
    template_name = "mailing/confirm_delete.html"
    success_url = reverse_lazy("mailing:message-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = self.request.META.get(
            "HTTP_REFERER", reverse_lazy("mailing:message-list")
        )
        return context

    def test_func(self):
        return not self.request.user.groups.filter(name="Менеджеры").exists()


# Mailing CBV
class MailingListView(LoginRequiredMixin, OwnerQuerysetMixin, ListView):
    model = Mailing
    template_name = "mailing/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Список рассылок",
                "create_url": reverse_lazy("mailing:mailing-create"),
                "headers": ["Дата начала", "Дата окончания", "Статус", "Активна"],
                "fields": ["start_time", "end_time", "status", "is_active"],
                "update_url_name": "mailing:mailing-update",
                "delete_url_name": "mailing:mailing-delete",
                "extra_action": {
                    "url_name": "mailing:send_mailing",
                    "label": "Отправить",
                },
            }
        )
        return context

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .select_related("message")
            .prefetch_related("recipients")
        )
        # Менеджеры видят ВСЕ рассылки
        if self.request.user.groups.filter(name="Менеджеры").exists():
            return qs
        return qs.filter(owner=self.request.user)


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/form.html"
    success_url = reverse_lazy("mailing:mailing-list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = self.request.META.get(
            "HTTP_REFERER", reverse_lazy("mailing:mailing-list")
        )
        return context


class MailingUpdateView(LoginRequiredMixin, OwnerQuerysetMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/form.html"
    success_url = reverse_lazy("mailing:mailing-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = self.request.META.get(
            "HTTP_REFERER", reverse_lazy("mailing:mailing-list")
        )
        return context

    def test_func(self):
        # Только владелец может редактировать
        mailing = self.get_object()
        return self.request.user == mailing.owner


class MailingDeleteView(LoginRequiredMixin, OwnerQuerysetMixin, DeleteView):
    model = Mailing
    template_name = "mailing/confirm_delete.html"
    success_url = reverse_lazy("mailing:mailing-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = self.request.META.get(
            "HTTP_REFERER", reverse_lazy("mailing:mailing-list")
        )
        return context

    def test_func(self):
        # Только владелец может удалять
        mailing = self.get_object()
        return self.request.user == mailing.owner


class MailingDisableView(LoginRequiredMixin, UserPassesTestMixin, View):
    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        mailing.is_active = False
        mailing.save()
        messages.success(request, f"Рассылка #{mailing.pk} отключена")
        return redirect("mailing:mailing-list")

    def test_func(self):
        return self.request.user.groups.filter(name="Менеджеры").exists()


# Send Mailing
@require_POST
def send_mailing(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)

    if mailing.status != "created":
        messages.warning(
            request, f"Рассылка #{mailing.pk} уже была отправлена или запущена."
        )
        return redirect("mailing:mailing-list")

    mailing.status = "started"
    mailing.save()

    success_count = 0
    fail_count = 0

    for recipient in mailing.recipients.all():
        try:
            result = send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                fail_silently=False,
            )

            if result:
                MailingAttempt.objects.create(
                    mailing=mailing,
                    status="success",
                    server_response="Отправлено успешно",
                )
                success_count += 1
            else:
                MailingAttempt.objects.create(
                    mailing=mailing,
                    status="fail",
                    server_response="Не удалось отправить",
                )
                fail_count += 1

        except Exception as e:
            MailingAttempt.objects.create(
                mailing=mailing,
                status="fail",
                server_response=str(e),
            )
            fail_count += 1

    mailing.status = "finished"
    mailing.save()

    messages.success(
        request,
        f"Рассылка #{mailing.pk} завершена: {success_count} успешно, {fail_count} с ошибками.",
    )
    return redirect("mailing:mailing-list")
