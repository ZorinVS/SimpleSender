from django.db.utils import IntegrityError

from mailings.management.utils.shared import emails
from mailings.management.utils.validators import do_stop, has_value, is_alpha, is_email
from mailings.models import Client, Mailing, Message


def get_valid_input(prompt_string, validation_functions):
    """ Проверка ввода пользователя """
    while True:
        is_valid = True
        user_input = input(prompt_string).strip()

        for func in validation_functions:
            if not func(user_input):
                is_valid = False
                break

        if is_valid:
            return user_input


def get_message():
    """ Добавление сообщения """
    subject = get_valid_input("     - Введите тему сообщения: ", [has_value])
    body = get_valid_input("     - Введите сообщение: ", [has_value])

    return Message.objects.create(subject=subject, body=body)


def get_clients():
    """ Добавление получателей рассылки """
    print("     - Для прекращения добавления наберите '*' в полях создания клиента")

    clients = []

    client_count = 0
    while True:
        client_count += 1

        print(f"     - Клиент №{client_count}:")
        while True:
            # Сбор данных от пользователя
            email = get_valid_input("          - Введите email: ", [has_value, is_email])
            surname = get_valid_input("          - Введите фамилию: ", [has_value, is_alpha])
            first_name = get_valid_input("          - Введите имя: ", [has_value, is_alpha])
            patronymic = get_valid_input("          - Введите отчество (при наличии): ", [is_alpha])
            comment = input("          - Введите комментарий (при наличии): ").strip()

            if do_stop(email, surname, first_name, patronymic, comment):
                return clients

            try:
                client = Client.objects.create(
                    email=email,
                    surname=surname.capitalize(),
                    first_name=first_name.capitalize(),
                    patronymic=patronymic.capitalize() if patronymic else "",
                    comment=comment,
                )
            except (UnicodeEncodeError, IntegrityError):
                continue
            else:
                print(f"          - Клиент с почтой {email} добавлен успешно")
                emails.add(email)
                clients.append(client)
                break


def create_mailing(message, recipient_list):
    """ Создание рассылки """
    mailing = Mailing.objects.create(message=message)
    mailing.clients.set(recipient_list)

    return mailing
