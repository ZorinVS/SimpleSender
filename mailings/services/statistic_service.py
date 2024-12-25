from django.core.cache import cache
from django.db.models import Prefetch, Q, Count
from django.shortcuts import get_object_or_404

from mailings.models import Mailing, Client, MailingAttempt
from mailings.services.cache_service import create_key_part
from mailings.services.utils import is_manager
from users.management.commands.create_managers import GROUP_NAME
from users.models import User


def get_mailing_statistics(context, user):
    """ Получение статистики по рассылкам для главной страницы """

    # Контекст для неавторизованных пользователй
    content = {
        "mailings": None,
        "total_mailings": 0,
        "active_mailings": 0,
        "unique_recipients": 0,
    }

    if user.is_authenticated:
        cache_key = f"{create_key_part(user)}_index_content"
        cached_content = cache.get(cache_key)

        if cached_content is None:
            is_user_manager = is_manager(user)

            mailings = Mailing.objects.filter(owner=user) if not is_user_manager else Mailing.objects.all()
            clients = Client.objects.filter(owner=user) if not is_user_manager else Client.objects.all()

            # Формирование данных для кеширования
            cached_content = {
                "mailings": mailings,
                "total_mailings": mailings.count(),
                "active_mailings": mailings.filter(status=Mailing.STATUS_LAUNCHED).count(),
                "unique_recipients": clients.count(),
            }

            # Сохранение в кеш на 15 мин
            cache.set(cache_key, cached_content, 60 * 15)

        # Обновление `content` кешированными данными
        content.update(cached_content)

    # Расширение контекста
    context.update(content)
    return context


def get_statistics(user):
    """
    Функция для сбора статистики:
    - Для менеджера: статистика по всем пользователям сервиса
    - Для пользователя: статистика только по его данным
    """
    cache_key = f"{create_key_part(user)}_user_statistics"
    cached_statistics = cache.get(cache_key)

    if cached_statistics is None:
        # Сбор статистики, если данные нет в кеше
        if is_manager(user):
            # Общая статистика для менеджера
            qs = User.objects.exclude(
                Q(is_staff=True) | Q(groups__name=GROUP_NAME)  # исключение менеджеров и администраторов
            ).prefetch_related(
                Prefetch("mailings", queryset=Mailing.objects.prefetch_related("attempts"))
            )
        else:
            # Статистика для пользователя сервиса
            qs = User.objects.filter(id=user.id).prefetch_related(
                Prefetch("mailings", queryset=Mailing.objects.prefetch_related("attempts"))
            )

        # Получение данных для кеширования
        cached_statistics = list(annotate_user_statistics(queryset=qs))
        cache.set(cache_key, cached_statistics, 60 * 15)  # 15 мин

    return cached_statistics


def annotate_user_statistics(queryset):
    """
    Функция для аннотирования статистики
    Добавляет в queryset поля:
        - message_count: количество уникальных успешных рассылок,
        - successful_mailing_attempts: количество успешных попыток рассылки,
        - unsuccessful_mailing_attempts: количество неуспешных попыток рассылки.
    """
    return queryset.annotate(
        message_count=Count(
            "mailings__attempts",
            filter=Q(mailings__attempts__status=MailingAttempt.STATUS_SUCCESS),
            distinct=True,
        ),
        successful_mailing_attempts=Count(
            "mailings__attempts",
            filter=Q(mailings__attempts__status=MailingAttempt.STATUS_SUCCESS),
        ),
        unsuccessful_mailing_attempts=Count(
            "mailings__attempts",
            filter=Q(mailings__attempts__status=MailingAttempt.STATUS_FAIL),
        ),
    ).values(
        "pk",
        "email",
        "message_count",
        "successful_mailing_attempts",
        "unsuccessful_mailing_attempts",
    )


def update_context_with_stat(context, pk):
    """ Расширение контекста статистическими данными """
    cache_key = f"mailing_attempts_{pk}"
    cached_stat = cache.get(cache_key)

    if cached_stat is None:
        mailing = get_object_or_404(Mailing, pk=pk)
        cached_stat = mailing.attempts.all()
        cache.set(cache_key, cached_stat, 60 * 15)  # 15 мин

    context["stat"] = cached_stat
    return context
