from django.core.management import BaseCommand

from mailings.management.utils.utils import create_mailing, get_clients, get_message
from mailings.services.mailing_service import send_mailing


class Command(BaseCommand):
    help = "Команда для отправки рассылки вручную через командную строку"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Запуск команды для отправки рассылки"))

        # 1/4 Создание сообщения
        self.stdout.write("1/4 Создание сообщения:")
        message = get_message()
        self.stdout.write(self.style.SUCCESS("     - Сообщение создано успешно"))

        # 2/4 Добавление получателей
        self.stdout.write("2/4 Добавление получателей рассылки:")
        recipients = get_clients()
        if recipients:
            self.stdout.write(self.style.SUCCESS(f"     - Получатели добавлены в количестве: {len(recipients)}"))

            # 3/4 Создание рассылки
            self.stdout.write("3/4 Создание рассылки:")
            mailing = create_mailing(message, recipients)
            self.stdout.write(self.style.SUCCESS("     - Рассылка успешно создана"))

            # 4/4 Отправка рассылки
            self.stdout.write("4/4 Отправка рассылки:")
            server_response = send_mailing(mailing)
            style = self.style.SUCCESS if "successfully" in server_response else self.style.ERROR
            self.stdout.write(style(f"     - Рассылка завершена с ответом сервера: {server_response}"))

        else:
            self.stdout.write(self.style.WARNING("     - Получатели не были добавлены. Завершение команды..."))

        self.stdout.write(self.style.SUCCESS("Команда выполнена"))
