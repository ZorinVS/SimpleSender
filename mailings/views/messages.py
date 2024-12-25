from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from mailings.forms import MessageForm
from mailings.models import Message
from mailings.services.mixins import OwnerQuerySetMixin, CreateMixin, OwnerDetailMixin, OwnerActionMixin


class MessageCreateView(LoginRequiredMixin, CreateMixin, CreateView):
    """
    Создание сообщения
    Права доступа: пользователь; администратор
    """
    model = Message
    template_name = "mailings/message/message_form.html"
    form_class = MessageForm

    def get_success_url(self):
        is_mailing_context = self.request.GET.get("mailing_context")
        reverse = "mailings:mailing_create" if is_mailing_context == "true" else "mailings:message_list"
        return reverse_lazy(reverse)


class MessageListView(LoginRequiredMixin, OwnerQuerySetMixin, ListView):
    """
    Просмотр списка сообщений
    Права доступа: автор сообщения; менеджер; администратор
    """
    model = Message
    template_name = "mailings/message/message_list.html"


class MessageDetailView(LoginRequiredMixin, OwnerDetailMixin, DetailView):
    """
    Детальный просмотр
    Права доступа: автор сообщения; менеджер; администратор
    """
    model = Message
    template_name = "mailings/message/message_detail.html"


class MessageUpdateView(LoginRequiredMixin, OwnerActionMixin, UpdateView):
    """
    Редактирование сообщения
    Права доступа: автор сообщения; администратор
    """
    model = Message
    template_name = "mailings/message/message_form.html"
    form_class = MessageForm

    def get_success_url(self):
        return reverse_lazy("mailings:message_detail", kwargs={"pk": self.object.pk})


class MessageDeleteView(LoginRequiredMixin, OwnerActionMixin, DeleteView):
    """
    Удаление сообщения
    Права доступа: автор сообщения; администратор
    """
    model = Message
    template_name = "mailings/message/message_confirm_delete.html"
    success_url = reverse_lazy("mailings:message_list")
