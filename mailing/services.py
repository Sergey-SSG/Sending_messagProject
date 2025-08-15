from django.core.cache import cache

from .models import Mailing


def get_active_mailings():
    """Возвращает последние активные рассылки с кешированием."""
    mailings = cache.get("active_mailings")
    if not mailings:
        mailings = Mailing.objects.filter(status="started").order_by("-start_time")[:5]
        cache.set("active_mailings", mailings, timeout=60 * 5)  # кеш на 5 минут
    return mailings
