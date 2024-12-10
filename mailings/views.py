import pandas as pd
from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView, View

from mailings.forms import ExcelUploadForm
from mailings.models import Client, Mailing, Message


class ClientListView(ListView):
    model = Client
    template_name = "mailings/client/client_list.html"

    def get_queryset(self):
        return Client.objects.order_by("-id")


class ClientCreateView(CreateView):
    model = Client
    template_name = "mailings/client/client_form.html"
    fields = "__all__"
    success_url = reverse_lazy("mailings:client_list")


class ClientUploadView(View):
    def get(self, request):
        form = ExcelUploadForm()
        return render(request, "mailings/client/client_upload.html", {"form": form})

    def post(self, request):
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]

            try:
                df = pd.read_excel(file)
                for _, row in df.iterrows():
                    email = row['email']
                    surname = row['surname']
                    first_name = row['first_name']
                    patronymic = row['patronymic']
                    comment = row['comment'] if pd.notna(row['comment']) else ""

                    if not Client.objects.filter(email=email).exists():
                        Client.objects.create(
                           email=email,
                           surname=surname,
                           first_name=first_name,
                           patronymic=patronymic,
                           comment=comment,
                        )

                return redirect("mailings:client_list")

            except Exception as e:
                messages.error(request, f"Ошибка обработки файла: {e}")
        else:
            messages.error(request, "Форма некорректна")
        return render(request, "mailings/client_upload.html", {"form": form})


class ClientDetailView(DetailView):
    model = Client
    template_name = "mailings/client/client_detail.html"


class ClientUpdateView(UpdateView):
    model = Client
    template_name = "mailings/client/client_form.html"
    fields = "__all__"

    def get_success_url(self):
        return reverse_lazy("mailings:client_detail", kwargs={"pk": self.object.pk})


class ClientDeleteView(DeleteView):
    model = Client
    template_name = "mailings/client/client_confirm_delete.html"
    success_url = reverse_lazy("mailings:client_list")

    # def delete(self, request, *args, **kwargs):
    #     client = self.get_object()
    #     related_mailings = client.mailings.all()
    #
    #     # Удаление рассылок, если в них отсутствуют получатели
    #     for mailing in related_mailings:
    #         count_clients = mailing.clients.count() - 1
    #         print(count_clients)
    #
    #         # Проверка на наличие получателей
    #         if count_clients == 0:
    #             print("Получателей нет")
    #             mailing.delete()
    #
    #     return super().delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        print("Метод delete вызван")
        raise Exception("Прерывание выполнения метода delete")
        return super().delete(request, *args, **kwargs)


# =========================== Messages ======================================================

class MessageListView(ListView):
    model = Message
    template_name = "mailings/message/message_list.html"

    def get_queryset(self):
        return Message.objects.order_by("-id")


class MessageCreateView(CreateView):
    model = Message
    template_name = "mailings/message/message_form.html"
    fields = "__all__"
    success_url = reverse_lazy("mailings:message_list")


class MessageDetailView(DetailView):
    model = Message
    template_name = "mailings/message/message_detail.html"


class MessageUpdateView(UpdateView):
    model = Message
    template_name = "mailings/message/message_form.html"
    fields = "__all__"

    def get_success_url(self):
        return reverse_lazy("mailings:message_detail", kwargs={"pk": self.object.pk})


class MessageDeleteView(DeleteView):
    model = Message
    template_name = "mailings/message/message_confirm_delete.html"
    success_url = reverse_lazy("mailings:message_list")


# =========================== Mailings ======================================================

class MailingListView(ListView):
    model = Mailing
    template_name = "mailings/mailing/mailing_list.html"

    def get_queryset(self):
        return Mailing.objects.order_by("-id")


class MailingCreateView(CreateView):
    model = Mailing
    template_name = "mailings/mailing/mailing_form.html"
    fields = ["message", "clients"]
    success_url = reverse_lazy("mailings:mailing_list")


class MailingDetailView(DetailView):
    model = Mailing
    template_name = "mailings/mailing/mailing_detail.html"


class MailingUpdateView(UpdateView):
    model = Mailing
    template_name = "mailings/mailing/mailing_form.html"
    fields = ["message", "clients"]

    def get_success_url(self):
        return reverse_lazy("mailings:mailing_detail", kwargs={"pk": self.object.pk})


class MailingDeleteView(DeleteView):
    model = Mailing
    template_name = "mailings/mailing/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailings:mailing_list")
