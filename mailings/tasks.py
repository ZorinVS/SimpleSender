from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from django_apscheduler.jobstores import DjangoJobStore

from config import settings
from mailings.models import Mailing
import logging

from mailings.services.mailing_service import send_mailing

logger = logging.getLogger(__name__)

# Создание планировщика
scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
scheduler.add_jobstore(DjangoJobStore(), "default")


def schedule_mailing_once(mailing_id, run_time):
    """ Планирование разовой отправки рассылки на указанное время """
    job_id = f"mailing_once_{mailing_id}"

    # Добавление задачи
    scheduler.add_job(
        send_mailing_task,
        trigger=DateTrigger(run_date=run_time),
        args=[mailing_id],
        id=job_id,
        replace_existing=True,
        name=f"One-time mailing for ID {mailing_id}"
    )

    # Обновление данных модели
    mailing = Mailing.objects.get(pk=mailing_id)
    mailing.status = Mailing.STATUS_LAUNCHED
    mailing.job_id = job_id
    mailing.save()


def send_mailing_task(mailing_id):
    """ Задача отправки рассылки по ее ID """
    try:
        mailing = Mailing.objects.get(pk=mailing_id)
    except Mailing.DoesNotExist:
        logger.error(f"Рассылка с ID {mailing_id} не найдена")
    else:
        send_mailing(mailing)
        mailing.job_id = None
        mailing.save()
