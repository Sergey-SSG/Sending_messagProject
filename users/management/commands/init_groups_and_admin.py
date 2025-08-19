from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from mailing.models import Mailing, Message, Recipient


class Command(BaseCommand):
    help = "Создаёт группы 'Менеджеры' и 'Пользователи' и суперпользователя"

    def handle(self, *args, **kwargs):
        User = get_user_model()

        # --- Создаём группы ---
        manager_group, _ = Group.objects.get_or_create(name="Менеджеры")
        user_group, _ = Group.objects.get_or_create(name="Пользователи")

        # Менеджеры — только просмотр всех моделей
        for model in [Mailing, Recipient, User]:
            ct = ContentType.objects.get_for_model(model)
            view_perm = Permission.objects.get(
                codename=f"view_{model._meta.model_name}", content_type=ct
            )
            manager_group.permissions.add(view_perm)

        # Пользователи — полный CRUD для своих объектов (логика в CBV)
        for model in [Mailing, Message, Recipient]:
            ct = ContentType.objects.get_for_model(model)
            for action in ["add", "change", "delete", "view"]:
                perm = Permission.objects.get(
                    codename=f"{action}_{model._meta.model_name}", content_type=ct
                )
                user_group.permissions.add(perm)

        # --- Создаём суперпользователя ---
        if not User.objects.filter(email="admin@example.com").exists():
            user = User.objects.create_superuser(
                email="admin@example.com",
                password="12345678",
                first_name="Admin",
                last_name="Adminex",
            )
            self.stdout.write(self.style.SUCCESS(f"Superuser created: {user.email}"))
        else:
            self.stdout.write(self.style.WARNING("Superuser already exists"))

        self.stdout.write(self.style.SUCCESS("Группы и права успешно созданы"))
