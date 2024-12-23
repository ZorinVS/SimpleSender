from mailings.services.utils import is_manager


def create_key_part(user):
    """ Создание части ключа на основе пользователя """
    return "manager" if is_manager(user) else user.email.split("@")[0]


def create_cache_key_for_object_list(model, user, **kwargs):
    """ Создание ключа кеша для списка объектов заданной модели"""
    model_name = model.__name__.lower()
    key_part = create_key_part(user)
    add_parts = "_".join(f"{key}_{value}" for key, value in kwargs.items() if value)

    return f"{model_name}_list_{key_part}_{add_parts}".rstrip("_")
