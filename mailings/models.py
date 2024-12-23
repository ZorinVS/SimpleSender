from django.db import models

from users.models import User


class Client(models.Model):
    email = models.EmailField(unique=True, verbose_name="Электронная почта")
    surname = models.CharField(max_length=30, verbose_name="Фамилия")
    first_name = models.CharField(max_length=30, verbose_name="Имя")
    patronymic = models.CharField(
        blank=True,
        null=False,  # если клиент не имеет фамилии, то Django создает пустое значение ""
        max_length=30,
        verbose_name="Отчество"
    )
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Владелец", related_name="clients")

    def __str__(self):
        return f"{self.first_name} {self.surname}: {self.email}"

    class Meta:
        verbose_name = "Получатель рассылки"
        verbose_name_plural = "Получатели рассылки"
        ordering = ["surname"]
        permissions = [
            ("view_all_clients", "Can view all clients"),
        ]


class Message(models.Model):
    subject = models.CharField(max_length=255, verbose_name="Тема письма")
    body = models.TextField(verbose_name="Тело письма")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Владелец", related_name="messages")

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ["subject"]
        permissions = [
            ("view_all_messages", "Can view all messages"),
        ]


class Mailing(models.Model):
    STATUS_CREATED = "created"
    STATUS_LAUNCHED = "launched"
    STATUS_COMPLETED = "completed"

    STATUS_CHOICES = [
        (STATUS_CREATED, "Создана"),
        (STATUS_LAUNCHED, "Запущена"),
        (STATUS_COMPLETED, "Завершена"),
    ]
    start_datetime = models.DateTimeField(null=True, verbose_name="Дата и время первой отправки")
    end_datetime = models.DateTimeField(null=True, verbose_name="Дата и время окончания отправки")
    status = models.CharField(max_length=9, choices=STATUS_CHOICES, default=STATUS_CREATED, verbose_name="Статус")
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="mailings", verbose_name="Сообщение")
    clients = models.ManyToManyField(Client, related_name="mailings", verbose_name="Получатели")
    job_id = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name="активна")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Владелец", related_name="mailings")

    def __str__(self):
        return f"Тема рассылки: {self.message.subject}"

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        permissions = [
            ("disable_mailing", "Can disable mailing"),
        ]


class MailingAttempt(models.Model):
    STATUS_SUCCESS = "successfully"
    STATUS_FAIL = "unsuccessfully"

    STATUS_CHOICES = [
        (STATUS_SUCCESS, "Успешно"),
        (STATUS_FAIL, "Не успешно"),
    ]

    attempt_datetime = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время попытки")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, verbose_name="Статус попытки")
    server_response = models.TextField(verbose_name="Ответ почтового сервера")
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name="attempts", verbose_name="Рассылка")

    def __str__(self):
        return f"{self.attempt_datetime}: {self.status}"

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылки"
        ordering = ["-attempt_datetime", "status"]
