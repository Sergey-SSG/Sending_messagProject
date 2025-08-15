from django.conf import settings
from django.db import models


class Recipient(models.Model):
    email = models.EmailField("Электронная почта", unique=True)
    full_name = models.CharField("Полное имя", max_length=255)
    comment = models.TextField("Комментарий", blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recipients",
        verbose_name="Владелец",
    )

    class Meta:
        verbose_name = "Получатель"
        verbose_name_plural = "Получатели"

    def __str__(self):
        return f"{self.full_name} <{self.email}>"


class Message(models.Model):
    subject = models.CharField("Тема письма", max_length=255)
    body = models.TextField("Текст письма")

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="message",
        verbose_name="Владелец",
    )

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"

    def __str__(self):
        return self.subject


class Mailing(models.Model):
    STATUS_CHOICES = [
        ("created", "Создана"),
        ("started", "Запущена"),
        ("finished", "Завершена"),
    ]

    start_time = models.DateTimeField("Время начала")
    end_time = models.DateTimeField("Время окончания")
    status = models.CharField(
        "Статус", max_length=10, choices=STATUS_CHOICES, default="created"
    )
    message = models.ForeignKey(
        Message,
        verbose_name="Сообщение",
        on_delete=models.CASCADE,
        related_name="mailings",
    )
    recipients = models.ManyToManyField(
        Recipient, verbose_name="Получатели", related_name="mailings"
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mailings",
        verbose_name="Владелец",
    )

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"

    def __str__(self):
        return f"Рассылка #{self.pk} - {self.status}"


class MailingAttempt(models.Model):
    STATUS_CHOICES = [
        ("success", "Успешно"),
        ("fail", "Не успешно"),
    ]

    mailing = models.ForeignKey(
        Mailing,
        verbose_name="Рассылка",
        on_delete=models.CASCADE,
        related_name="attempts",
    )
    attempt_time = models.DateTimeField("Время попытки", auto_now_add=True)
    status = models.CharField("Статус", max_length=10, choices=STATUS_CHOICES)
    server_response = models.TextField("Ответ сервера", blank=True)

    class Meta:
        verbose_name = "Попытка отправки"
        verbose_name_plural = "Попытки отправки"

    def __str__(self):
        return f"Попытка {self.pk} для Рассылки #{self.mailing.pk} - {self.status}"
