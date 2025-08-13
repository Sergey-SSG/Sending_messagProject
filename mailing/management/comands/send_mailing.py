from django.core.management.base import BaseCommand, CommandError
from mailing.models import Mailing, MailingAttempt
from django.core.mail import send_mail

class Command(BaseCommand):
    help = 'Отправить рассылку по ID'

    def add_arguments(self, parser):
        parser.add_argument('mailing_id', type=int, help='ID рассылки для отправки')

    def handle(self, *args, **options):
        mailing_id = options['mailing_id']
        try:
            mailing = Mailing.objects.get(pk=mailing_id)
        except Mailing.DoesNotExist:
            raise CommandError(f"Рассылка с ID {mailing_id} не найдена.")

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
                self.stdout.write(f"Отправлено {recipient.email}")
            except Exception as e:
                MailingAttempt.objects.create(
                    mailing=mailing,
                    status='fail',
                    server_response=str(e),
                )
                self.stderr.write(f"Ошибка при отправке {recipient.email}: {e}")

        self.stdout.write(self.style.SUCCESS(f"Рассылка #{mailing_id} завершена"))