from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from mailings.forms import ClientForm
from mailings.models import Client
from mailings.services.mixins import OwnerQuerySetMixin, CreateMixin, OwnerDetailMixin, OwnerActionMixin
from mailings.services.utils import cleanup_mailings_on_client_delete


class ClientCreateView(LoginRequiredMixin, CreateMixin, CreateView):
    """
    Добавление получателей
    Права доступа: пользователь; администратор
    """
    model = Client
    template_name = "mailings/client/client_form.html"
    form_class = ClientForm

    def get_success_url(self):
        is_mailing_context = self.request.GET.get("mailing_context")
        reverse = "mailings:mailing_create" if is_mailing_context == "true" else "mailings:client_list"
        return reverse_lazy(reverse)


class ClientListView(LoginRequiredMixin, OwnerQuerySetMixin, ListView):
    """
    Просмотр списка получателей
    Права доступа: автор записи клиента; менеджер; администратор
    """
    model = Client
    template_name = "mailings/client/client_list.html"


class ClientDetailView(LoginRequiredMixin, OwnerDetailMixin, DetailView):
    """
    Просмотр детальной информации получателя
    Права доступа: автор записи клиента; менеджер; администратор
    """
    model = Client
    template_name = "mailings/client/client_detail.html"


class ClientUpdateView(LoginRequiredMixin, OwnerActionMixin, UpdateView):
    """
    Обновление информации получателя
    Права доступа: автор записи клиента, администратор
    """
    model = Client
    template_name = "mailings/client/client_form.html"
    form_class = ClientForm

    def get_success_url(self):
        return reverse_lazy("mailings:client_detail", kwargs={"pk": self.object.pk})


class ClientDeleteView(LoginRequiredMixin, OwnerActionMixin, DeleteView):
    """
    Удаление получателя
    Права доступа: автор записи клиента; администратор
    """
    model = Client
    template_name = "mailings/client/client_confirm_delete.html"
    success_url = reverse_lazy("mailings:client_list")

    def delete(self, request, *args, **kwargs):
        client = self.get_object()
        cleanup_mailings_on_client_delete(client)
        return super().delete(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)
