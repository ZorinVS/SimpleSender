from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class MailingsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "mailings"

    def ready(self):
        from mailings.tasks import scheduler
        try:
            scheduler.start()
        except Exception as e:
            logger.error(f"Ошибка запуска scheduler: {e}")
