from django.contrib import admin

from .models import Mailing, MailingAttempt, Message, Recipient


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ("email", "full_name", "comment")
    search_fields = ("email", "full_name")
    list_filter = ("email",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("subject",)
    search_fields = ("subject", "body")


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ("id", "start_time", "end_time", "status", "message_display")
    list_filter = ("status",)
    search_fields = ("status", "message__subject")
    filter_horizontal = ("recipients",)

    def message_display(self, obj):
        return obj.message.subject

    message_display.short_description = "Сообщение"


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ("mailing", "attempt_time", "status", "short_server_response")
    list_filter = ("status",)
    search_fields = ("server_response",)

    def short_server_response(self, obj):
        return (
            (obj.server_response[:50] + "...")
            if len(obj.server_response) > 50
            else obj.server_response
        )

    short_server_response.short_description = "Ответ сервера"
