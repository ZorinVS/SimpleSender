from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView, View

from mailings.forms import MailingForm, ScheduleMailingForm
from mailings.models import Mailing
from mailings.services.mailing_service import filter_queryset_by_status, cancel_mailing, send_mailing, disable_mailing
from mailings.services.mixins import (
    CreateMixin, OwnerQuerySetMixin, OwnerDetailMixin,
    ActiveMailingRequiredMixin, OwnerActionMixin, MailingOwnerRequiredMixin,
)
from mailings.services.utils import can_cancel
from mailings.tasks import schedule_mailing_once


class MailingCreateView(LoginRequiredMixin, CreateMixin, CreateView):
    """
    Создание рассылки
    Права доступа: создатель рассылки; администратор
    """
    model = Mailing
    template_name = "mailings/mailing/mailing_form.html"
    form_class = MailingForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Передача текущего пользователя в форму
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy("mailings:mailing_detail", kwargs={"pk": self.object.pk})


class MailingListView(LoginRequiredMixin, OwnerQuerySetMixin, ListView):
    """
    Просмотр списка рассылок с фильтрацией по статусу
    Права доступа: создатель рассылки; менеджер; администратор
    """
    model = Mailing
    template_name = "mailings/mailing/mailing_list.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get("status")
        return filter_queryset_by_status(queryset, status)


class MailingDetailView(LoginRequiredMixin, OwnerDetailMixin, DetailView):
    """
    Просмотр детальной информации рассылки
    Права доступа: создатель рассылки; менеджер; администратор
    """
    model = Mailing
    template_name = "mailings/mailing/mailing_detail.html"


class MailingUpdateView(LoginRequiredMixin, ActiveMailingRequiredMixin, OwnerActionMixin, UpdateView):
    """
    Обновление рассылки
    Права доступа: создатель рассылки; администратор
    """
    model = Mailing
    template_name = "mailings/mailing/mailing_form.html"
    form_class = MailingForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Передача текущего пользователя в форму
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy("mailings:mailing_detail", kwargs={"pk": self.object.pk})


class MailingDeleteView(LoginRequiredMixin, OwnerActionMixin, DeleteView):
    """
    Удаление рассылки
    Права доступа: создатель рассылки; администратор
    """
    model = Mailing
    template_name = "mailings/mailing/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailings:mailing_list")

    def form_valid(self, form):
        mailing = self.get_object()
        cancel_mailing(mailing)
        return super().form_valid(form)


class MailingSendView(LoginRequiredMixin, ActiveMailingRequiredMixin, MailingOwnerRequiredMixin, View):
    """
    Отправка рассылки со сбором статистики
    Права доступа: создатель рассылки; администратор
    """
    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        send_mailing(mailing)
        return redirect("mailings:mailing_list")


class MailingScheduleView(LoginRequiredMixin, ActiveMailingRequiredMixin, MailingOwnerRequiredMixin, View):
    """
    Планирование разовой отправки рассылки на определенное время
    Права доступа: создатель рассылки; администратор
    """
    template_name = "mailings/mailing/mailing_schedule.html"

    def get(self, request, pk):
        form = ScheduleMailingForm()
        return render(request, self.template_name, {"form": form, "pk": pk})

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        form = ScheduleMailingForm(request.POST)
        if form.is_valid():
            scheduled_time = form.cleaned_data["scheduled_time"]
            if scheduled_time <= timezone.now():
                form.add_error("scheduled_time", "Рассылка сообщения в прошлом пока невозможна")
            else:
                schedule_mailing_once(mailing.pk, scheduled_time)
                return redirect("mailings:mailing_list")
        return render(request, self.template_name, {"form": form, "pk": pk})


class MailingCancelView(LoginRequiredMixin, View):
    """
    Отмена запланированной отправки рассылки
    Права доступа: создатель рассылки; менеджер; администратор
    """
    def post(self, request, pk):
        user = self.request.user
        mailing = get_object_or_404(Mailing, pk=pk)
        can_cancel(mailing, user)
        cancel_mailing(mailing)
        return redirect("mailings:mailing_detail", pk=pk)


class MailingDisableView(LoginRequiredMixin, View):
    """
    Отключение рассылки
    Права доступа: менеджер; администратор
    """
    def post(self, request, pk):
        user = self.request.user
        mailing = get_object_or_404(Mailing, pk=pk)
        disable_mailing(mailing, user)
        return redirect("mailings:mailing_list")
