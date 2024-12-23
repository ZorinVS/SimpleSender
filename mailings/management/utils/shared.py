from mailings.models import Client

# Переменная `emails` используется для валидации ввода пользователя при создании рассылки через командную строку
# В переменной хранятся почты:
# - существующих клиентов, полученных из БД
# - новых клиентов, добавленных в процессе выполнения команды `python3 manage.py send_mailing`

emails = set(client.email for client in Client.objects.all())
