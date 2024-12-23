from django.core.exceptions import PermissionDenied

from users.models import User


def is_manager(user):
    """ Проверка на менеджера """
    moderator_permissions = [
        "mailings.view_all_clients",
        "mailings.view_all_messages",
        "mailings.disable_mailing",
        "users.block_user",
    ]
    return user.has_perms(moderator_permissions)


def is_owner(obj, user):
    """ Проверка на владельца """
    if isinstance(obj, User):
        return obj == user
    return obj.owner == user


def can_cancel(obj, user):
    """ Проверка прав отмены рассылки """
    if not is_owner(obj, user) or is_manager(user) or user.is_superuser:
        raise PermissionDenied


def cleanup_mailings_on_client_delete(client):
    """
    Очистка рассылок, связанных с удаляемым клиентом

    Удаляет рассылки, которые больше не имеют получателей после удаления клиента,
    то есть если клиент был единственным получателем рассылки
    """
    # Перебор рассылок, связанных с удаляемым клиентом
    for mailing in client.mailings.all():
        # Удаление рассылки, если без текущего клиента она останется без получателей
        if mailing.clients.count() == 1:
            mailing.delete()
