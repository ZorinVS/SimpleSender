from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand

from mailings.models import Client, Message, Mailing
from users.models import User

GROUP_NAME = "Менеджеры"
GROUP_PERMISSIONS = [
    ("view_all_clients", ContentType.objects.get_for_model(Client)),
    ("view_all_messages", ContentType.objects.get_for_model(Message)),
    ("disable_mailing", ContentType.objects.get_for_model(Mailing)),
    ("block_user", ContentType.objects.get_for_model(User)),
]
USERS_DATA = (
    {
        "email": "colt@gmx.com",
        "avatar": "users/avatars/Colt.png",
        "country": "USA",
        "password": "manager",
    },
    {
        "email": "ken@gmx.com",
        "avatar": "users/avatars/Ken.png",
        "country": "USA",
        "password": "manager",
    },
)


class Command(BaseCommand):
    help = "Команда для наполнения базы данных группой Менеджеры"

    def handle(self, *args, **options):
        # Создание группы Менеджеры
        managers_group = self.create_group()

        # Добавление менеджеров
        self.add_managers(group=managers_group)

    def create_group(self):
        self.stdout.write("Создание группы Менеджеры...")
        try:
            managers_group = Group.objects.get(name=GROUP_NAME)
        except Group.DoesNotExist:
            managers_group = Group.objects.create(name=GROUP_NAME)
            for codename, content_type in GROUP_PERMISSIONS:
                permission = Permission.objects.get(codename=codename, content_type=content_type)
                managers_group.permissions.add(permission)
            managers_group.save()

        self.stdout.write(self.style.SUCCESS(" - Группа Менеджеры создана успешно"))
        return managers_group

    def add_managers(self, group):
        """ Добавление менеджеров из словаря USERS_DATA """
        self.stdout.write("Добавление менеджеров...")

        for user_data in USERS_DATA:
            # Получение данных пользователя
            email = user_data["email"]
            avatar = user_data["avatar"]
            country = user_data["country"]
            password = user_data["password"]

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                # Создание пользователя
                user = User.objects.create(
                    email=email,
                    avatar=avatar,
                    country=country,
                )
                user.set_password(password)

                # Добавление пользователя в группу Менеджеры
                user.groups.add(group)
                user.save()

            self.stdout.write(self.style.SUCCESS(f" - Добавлен модератор {email}. Пароль: {password}"))
