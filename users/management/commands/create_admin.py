from django.core.management import BaseCommand
from users.models import User


class Command(BaseCommand):
    help = "Команда для создания администратора"

    def handle(self, *args, **options):
        admin_email = "joi@gmx.com"
        admin_avatar = "users/avatars/Joi.png"
        admin_password = "icanfixthat"

        admin = User.objects.filter(email=admin_email)
        if admin.exists():
            self.stdout.write(self.style.WARNING("Администратор уже создан"))
        else:
            user = User.objects.create(email=admin_email, avatar=admin_avatar)
            user.set_password(admin_password)
            user.is_active = True
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(self.style.SUCCESS("Администратор успешно создан"))

        self.stdout.write(f"Данные для входа:\n"
                          f" - email: {admin_email}\n"
                          f" - password: {admin_password}")
