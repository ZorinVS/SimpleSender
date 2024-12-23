from django import forms

from mailings.models import Client, Message, Mailing


class StyleFormMixin:
    """
    Миксин для стилизации полей формы

    По умолчанию применят класс стилизации формы form-control
    Для настройки атрибутов виджетов используется атрибут формы `FIELDS_WITH_ATTRIBUTES`
    В `FIELDS_WITH_ATTRIBUTES` помещается словарь вида: {'название_поля': {'название_атрибута': 'значение'}}
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fields_with_attributes = getattr(self, "FIELDS_WITH_ATTRIBUTES", {})

        for field_name, field in self.fields.items():
            # Получение атрибутов для конкретного поля
            attributes = fields_with_attributes.get(field_name, {})

            # Применение класса form-control по умолчанию, если класс не указан
            attributes.setdefault("class", "form-control")

            # Обновление атрибутов поля
            field.widget.attrs.update(attributes)


class ClientForm(StyleFormMixin, forms.ModelForm):
    FIELDS_WITH_ATTRIBUTES = {
        "email": {"placeholder": "Введите почту клиента (обязательно)", "title": "Обязательное поле"},
        "surname": {"placeholder": "Введите фамилию клиента (обязательно)", "title": "Обязательное поле"},
        "first_name": {"placeholder": "Введите имя клиента (обязательно)", "title": "Обязательное поле"},
        "patronymic": {"placeholder": "Введите отчество клиента"},
        "comment": {"placeholder": "Добавьте комментарий"},
    }

    class Meta:
        model = Client
        exclude = ["owner"]


class MessageForm(StyleFormMixin, forms.ModelForm):
    FIELDS_WITH_ATTRIBUTES = {
        "subject": {"placeholder": "Введите тему", "title": "Обязательное поле"},
        "body": {"placeholder": "Текст сообщения", "title": "Обязательное поле"},
    }

    class Meta:
        model = Message
        fields = ["subject", "body"]


class MailingForm(StyleFormMixin, forms.ModelForm):
    FIELDS_WITH_ATTRIBUTES = {
        "message": {"title": "Выберите сообщение"},
        "clients": {"title": "– Выбор подряд: Shift + ПКМ\n– Избирательный выбор: Command + ПКМ"},
    }

    class Meta:
        model = Mailing
        fields = ["message", "clients"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        # Фильтрация сообщений и клиентов по владельцу
        self.fields['message'].queryset = Message.objects.filter(owner=user)
        self.fields['clients'].queryset = Client.objects.filter(owner=user)


class ScheduleMailingForm(forms.Form):
    scheduled_time = forms.DateTimeField(
        label="Время отправки",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
        input_formats=["%Y-%m-%dT%H:%M"],
    )
