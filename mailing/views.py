from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from .models import Recipient, Message, Mailing, MailingAttempt
from .forms import RecipientForm, MessageForm, MailingForm
from django.conf import settings


class HomeView(TemplateView):
    template_name = 'mailing/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Базовая статистика
        context['total_mailings'] = Mailing.objects.count()
        context['active_mailings'] = Mailing.objects.filter(status='started').count()
        context['unique_recipients'] = Recipient.objects.count()

        # Последние активные рассылки
        context['latest_active_mailings'] = (
            Mailing.objects.filter(status='started')
            .order_by('-start_time')[:5]
        )

        # Статистика по попыткам отправки
        attempts_stats = MailingAttempt.objects.aggregate(
            success_count=Count('id', filter=Q(status='success')),
            fail_count=Count('id', filter=Q(status='fail'))
        )
        context['success_count'] = attempts_stats['success_count']
        context['fail_count'] = attempts_stats['fail_count']

        return context


class RecipientListView(ListView):
    model = Recipient
    template_name = 'mailing/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Список получателей',
            'create_url': reverse_lazy('mailing:recipient-create'),
            'headers': ['ФИО', 'Email', 'Комментарий'],
            'fields': ['full_name', 'email', 'comment'],
            'update_url_name': 'mailing:recipient-update',
            'delete_url_name': 'mailing:recipient-delete',
        })
        return context


class RecipientDetailView(DetailView):
    model = Recipient


class RecipientCreateView(CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing/form.html'
    success_url = reverse_lazy('mailing:recipient-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = self.request.META.get('HTTP_REFERER', reverse_lazy('mailing:recipient-list'))
        return context


class RecipientUpdateView(UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing/form.html'
    success_url = reverse_lazy('mailing:recipient-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = self.request.META.get('HTTP_REFERER', reverse_lazy('mailing:recipient-list'))
        return context


class RecipientDeleteView(DeleteView):
    model = Recipient
    template_name = 'mailing/confirm_delete.html'
    success_url = reverse_lazy('mailing:recipient-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = self.request.META.get('HTTP_REFERER', reverse_lazy('mailing:recipient-list'))
        return context


class MessageListView(ListView):
    model = Message
    template_name = 'mailing/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Список сообщений',
            'create_url': reverse_lazy('mailing:message-create'),
            'headers': ['Тема', 'Текст'],
            'fields': ['subject', 'body'],
            'update_url_name': 'mailing:message-update',
            'delete_url_name': 'mailing:message-delete',
        })
        return context


class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/form.html'
    success_url = reverse_lazy('mailing:message-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = self.request.META.get('HTTP_REFERER', reverse_lazy('mailing:message-list'))
        return context


class MessageUpdateView(UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/form.html'
    success_url = reverse_lazy('mailing:message-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = self.request.META.get('HTTP_REFERER', reverse_lazy('mailing:message-list'))
        return context


class MessageDeleteView(DeleteView):
    model = Message
    template_name = 'mailing/confirm_delete.html'
    success_url = reverse_lazy('mailing:message-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = self.request.META.get('HTTP_REFERER', reverse_lazy('mailing:recipient-list'))
        return context


class MailingListView(ListView):
    model = Mailing
    template_name = 'mailing/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Список рассылок',
            'create_url': reverse_lazy('mailing:mailing-create'),
            'headers': ['Дата начала', 'Дата окончания', 'Статус'],
            'fields': ['start_time', 'end_time', 'status'],
            'update_url_name': 'mailing:mailing-update',
            'delete_url_name': 'mailing:mailing-delete',
            'extra_action': {
                'url_name': 'mailing:send_mailing',
                'label': 'Отправить',
            }
        })
        return context


class MailingCreateView(CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/form.html'
    success_url = reverse_lazy('mailing:mailing-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = self.request.META.get('HTTP_REFERER', reverse_lazy('mailing:mailing-list'))
        return context


class MailingUpdateView(UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/form.html'
    success_url = reverse_lazy('mailing:mailing-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = self.request.META.get('HTTP_REFERER', reverse_lazy('mailing:mailing-list'))
        return context


class MailingDeleteView(DeleteView):
    model = Mailing
    template_name = 'mailing/confirm_delete.html'
    success_url = reverse_lazy('mailing:mailing-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = self.request.META.get('HTTP_REFERER', reverse_lazy('mailing:recipient-list'))
        return context


@require_POST
def send_mailing(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)

    if mailing.status != 'created':
        messages.warning(request, f"Рассылка #{mailing.pk} уже была отправлена или запущена.")
        return redirect('mailing:mailing-list')

    mailing.status = 'started'
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

            if result:  # send_mail возвращает количество успешно доставленных писем
                MailingAttempt.objects.create(
                    mailing=mailing,
                    status='success',
                    server_response='Отправлено успешно',
                )
                success_count += 1
            else:
                MailingAttempt.objects.create(
                    mailing=mailing,
                    status='fail',
                    server_response='Не удалось отправить',
                )
                fail_count += 1

        except Exception as e:
            MailingAttempt.objects.create(
                mailing=mailing,
                status='fail',
                server_response=str(e),
            )
            fail_count += 1

    mailing.status = 'finished'
    mailing.save()

    messages.success(
        request,
        f"Рассылка #{mailing.pk} завершена: {success_count} успешно, {fail_count} с ошибками."
    )
    return redirect('mailing:mailing-list')
