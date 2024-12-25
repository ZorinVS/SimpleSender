import logging
from smtplib import SMTPException

from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.utils.timezone import now

from mailings.models import Mailing, MailingAttempt
from mailings.services.utils import is_manager

logger = logging.getLogger(__name__)


def send_mailing(mailing):
    """ Отправка письма со сбором статистики """

    # Сохранение даты и времени, если рассылка делается в первый раз
    if mailing.status == Mailing.STATUS_CREATED:
        mailing.start_datetime = now()
        mailing.save()

    # Изменение статуса рассылки на 'Запущена'
    if mailing.status != Mailing.STATUS_LAUNCHED:
        update_mailing_status(mailing)

    # Получение данных рассылки
    subject = mailing.message.subject
    message = mailing.message.body
    from_email = None  # отправитель определен в `settings.py`
    recipient_list = [client.email for client in mailing.clients.all()]

    try:
        # Попытка отправки
        send_mail(subject, message, from_email, recipient_list)
    except (SMTPException, TimeoutError) as e:
        # Провальное отправление
        status = MailingAttempt.STATUS_FAIL
        response = str(e)
    else:
        # Успешное отправление
        status = MailingAttempt.STATUS_SUCCESS
        response = "Mailing successfully handed over to the SMTP server"

    # Создание записи в MailingAttempt
    MailingAttempt.objects.create(
        status=status,
        server_response=response,
        mailing=mailing,
    )

    # Если рассылка была запланирована, отменяем её задачу для решения конфликта статусов рассылки
    if mailing.job_id:
        cancel_mailing(mailing)
    else:
        update_mailing_status(mailing)

    # Сохранение даты и времени окончания отправки
    mailing.end_datetime = now()
    mailing.save()

    return response


def update_mailing_status(mailing):
    """ Обновление статуса рассылки """

    if mailing.status == Mailing.STATUS_LAUNCHED:
        mailing.status = Mailing.STATUS_COMPLETED
    else:
        mailing.status = Mailing.STATUS_LAUNCHED

    mailing.save()


def cancel_mailing(mailing):
    """ Отмена запланированной рассылки """
    if mailing.job_id:
        try:
            from mailings.tasks import scheduler
            # Удаление задачи из планировщика
            scheduler.remove_job(mailing.job_id)

        except Exception as e:
            logger.error(f"Ошибка при отмене рассылки с ID {mailing.pk}: {e}")
        else:
            # Сброс идентификатора задачи планировщика
            mailing.job_id = None

    # Обновление статуса рассылки
    if mailing.attempts.exists():
        status = Mailing.STATUS_COMPLETED
    else:
        status = Mailing.STATUS_CREATED
    mailing.status = status

    mailing.save()


def disable_mailing(mailing, user):
    """ Отключение рассылки """
    if not is_manager(user):
        raise PermissionDenied
    if mailing.is_active:
        cancel_mailing(mailing)
        mailing.is_active = False
        mailing.save()


def filter_queryset_by_status(queryset, status):
    """ Фильтр QuerySet по статусу рассылки """
    if status == "active":
        return queryset.filter(status=Mailing.STATUS_LAUNCHED)
    elif status is not None:
        return queryset.none()
    return queryset
