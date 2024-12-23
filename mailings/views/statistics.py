from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from mailings.services.mixins import StatAccessControlMixin
from mailings.services.statistic_service import get_mailing_statistics, update_context_with_stat, get_statistics


class IndexView(TemplateView):
    """ Контроллер главной страницы """
    template_name = "mailings/index.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        user = self.request.user

        return get_mailing_statistics(context_data, user)


class MailingAttemptsView(LoginRequiredMixin, StatAccessControlMixin, TemplateView):
    """
    Отображение информации о попытках одной рассылки
    Права доступа: создатель рассылки; менеджер; администратор
    """
    template_name = "mailings/mailing_attempts.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        pk = kwargs.get("pk")
        return update_context_with_stat(context_data, pk)


class UserAttemptsView(LoginRequiredMixin, TemplateView):
    """
    Отображение информации о попытках рассылок пользователей
    Права доступа: создатель рассылки; менеджер; администратор
    """
    template_name = "mailings/user_attempts.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        user = self.request.user

        # Расширение контекста
        context_data["statistics"] = get_statistics(user)
        return context_data
