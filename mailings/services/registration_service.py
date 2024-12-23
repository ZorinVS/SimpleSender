import secrets

from django.contrib import messages
from django.core.mail import send_mail

from users.models import User


class AuthActionService:
    """
    Сервис для управления процессами аутентификации

    Методы поддерживают два типа действий, определяемых параметром `action`:
    - "verification": подтверждение электронной почты пользователя
    - "password_reset": сброс пароля пользователя
    """

    @staticmethod
    def generate_token():
        """ Генерация ключа """
        return secrets.token_hex(16)

    @staticmethod
    def send_confirmation_email(user, host, request, action="verification"):
        """
        Отправка письма со ссылкой для подтверждения действия

        Параметры:
        - user (User): объект пользователя, которому отправляется письмо
        - host (str): хост для генерации ссылки подтверждения
        - request (HttpRequest): текущий запрос для добавления сообщений
        - action (str): тип действия, одно из следующих:
            - "verification": для подтверждения почты
            - "password_reset": для сброса пароля
        """
        token = AuthActionService.generate_token()
        user.token = token
        user.save()

        if action == "verification":
            massage_for_page = "Письмо с подтверждением отправлено! Проверьте вашу почту"

            url = f"http://{host}/users/email-confirm/{token}/"
            subject = "Активация вашего нового simpleSENDER аккаунта"
            message = (
                f"Вы почти у цели!\nПерейдите по ссылке, чтобы подтвердить свой адрес электронной почты "
                f"и завершить создание учетной записи на simpleSENDER:\n{url}"
            )
        elif action == "password_reset":
            massage_for_page = "Письмо для сброса пароля отправлено! Проверьте вашу почту"

            url = f"http://{host}/users/password-reset-confirm/{token}/"
            subject = "Восстановление пароля"
            message = f"Для сброса пароля перейдите по ссылке:\n{url}"
        else:
            raise ValueError("Некорректный тип действия")

        try:
            send_mail(subject, message, from_email=None, recipient_list=[user.email])
        except Exception as e:
            print(f"Ошибка отправки письма: {e}")
            messages.error(request, message="Не удалось отправить письмо. Попробуйте позже")
            return False
        else:
            messages.success(request, message=massage_for_page)
            return True

    @staticmethod
    def verify_token(token, request, action="verification"):
        """
        Верификация токена для подтверждения действия

        Параметры:
        - token (str): токен, отправленный пользователю
        - request (HttpRequest): текущий запрос для добавления сообщений
        - action (str): тип действия, одно из следующих:
            - "verification": активация пользователя
            - "password_reset": сброс пароля
        """
        if action not in ("verification", "password_reset"):
            raise ValueError("Некорректный тип действия")
        try:
            user = User.objects.get(token=token)
        except User.DoesNotExist:
            messages.error(request, message="Ошибка подтверждения! Перейдите по ссылке, указанной в письме")
            return None

        if not user.is_active and action == "verification":
            user.is_active = True
            user.token = None  # удаление токена после подтверждения почты
            user.save()
            messages.success(request, message="Ваш аккаунт успешно активирован! Вы можете авторизоваться")

        return user
