from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from .models import Recipient, Message, Mailing, MailingAttempt
from .forms import RecipientForm, MessageForm, MailingForm



class HomeView(TemplateView):
    template_name = 'mailing/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_mailings'] = Mailing.objects.count()
        context['active_mailings'] = Mailing.objects.filter(status='started').count()
        context['unique_recipients'] = Recipient.objects.count()
        context['latest_active_mailings'] = (
            Mailing.objects.filter(status='started')
            .order_by('-start_time')[:5]
        )
        return context


class RecipientListView(ListView):
    model = Recipient
    template_name = 'mailing/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Список получателей'
        context['create_url'] = reverse_lazy('mailing:recipient-create')
        context['headers'] = ['Email', 'ФИО']
        context['fields'] = ['email', 'full_name']
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
        context['title'] = 'Список сообщений'
        context['create_url'] = reverse_lazy('mailing:message-create')
        context['headers'] = ['Тема письма', 'Текст письма']
        context['fields'] = ['subject', 'body']
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
        context['title'] = 'Список рассылок'
        context['create_url'] = reverse_lazy('mailing:mailing-create')
        context['headers'] = ['Дата начала', 'Дата окончания', 'Статус']
        context['fields'] = ['start_time', 'end_time', 'status']
        context['extra_action'] = {
            'url_suffix': 'send',
            'label': 'Отправить',
        }
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

    if mailing.status == 'created':
        mailing.status = 'started'
        mailing.save()

    for recipient in mailing.recipients.all():
        try:
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=None,
                recipient_list=[recipient.email],
                fail_silently=False,
            )
            MailingAttempt.objects.create(
                mailing=mailing,
                status='success',
                server_response='Отправлено успешно',
            )
        except Exception as e:
            MailingAttempt.objects.create(
                mailing=mailing,
                status='fail',
                server_response=str(e),
            )
    messages.success(request, f"Рассылка #{mailing.pk} отправлена.")
    return redirect('mailing:mailing-list')
