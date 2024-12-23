import os

from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404

from mailings.models import Mailing
from mailings.services.cache_service import create_cache_key_for_object_list
from mailings.services.utils import is_manager, is_owner
from users.management.commands.create_managers import GROUP_NAME
from users.models import User


class OwnerQuerySetMixin:
    """ Фильтр QuerySet по владельцу """

    # Параметр для включения/выключения кеширования
    USE_CACHE = os.getenv("USE_CACHE_FOR_OBJECT_LIST") == "True"

    def get_queryset(self):
        user = self.request.user
        model = self.model

        if self.USE_CACHE:
            if model.__name__ == "Mailing":
                cache_key = create_cache_key_for_object_list(model, user, status=self.request.GET.get("status"))
            else:
                cache_key = create_cache_key_for_object_list(model, user)
            cached_queryset = cache.get(cache_key)

            if cached_queryset is None:
                # Получение данных для кеширования
                cached_queryset = model.objects.filter(owner=user) if not is_manager(user) else model.objects.all()
                cache.set(cache_key, cached_queryset, 60 * 15)
        else:
            # Если кеширование отключено, данные загружаются из БД без кеширования
            cached_queryset = model.objects.filter(owner=user) if not is_manager(user) else model.objects.all()

        return cached_queryset


class CreateMixin:
    """ Проверка на право создания с автоматическим указанием владельца """
    def form_valid(self, form):
        user = self.request.user
        instance = form.instance
        # Менеджеры не могут создавать объекты
        if is_manager(user) and not user.is_superuser:
            raise PermissionDenied
        instance.owner = user

        return super().form_valid(form)


class OwnerDetailMixin:
    """ Проверка на право просмотра """
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        if not (is_owner(obj, user) or is_manager(user)):
            raise PermissionDenied
        return obj


class OwnerActionMixin:
    """ Проверка на право удаления, обновления объекта """
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        can_do = is_owner(obj, user) or user.is_superuser
        if not can_do:
            raise PermissionDenied
        return obj


class MailingOwnerRequiredMixin:
    """ Проверка на право отправки рассылок """
    def dispatch(self, request, *args, **kwargs):
        mailing = get_object_or_404(Mailing, pk=kwargs.get("pk"))
        user = request.user
        if mailing.owner != user and not user.is_superuser:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class ActiveMailingRequiredMixin:
    """ Проверка на возможность взаимодействия с рассылкой """
    def dispatch(self, request, *args, **kwargs):
        mailing = get_object_or_404(Mailing, pk=kwargs.get("pk"))
        if not mailing.is_active:
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)


class UserListManagerRequiredMixin:
    """ Проверка на менеджера и формирование QuerySet """
    def get_queryset(self):
        user = self.request.user
        if not is_manager(user):
            raise PermissionDenied()
        queryset = User.objects.exclude(Q(is_staff=True) | Q(groups__name=GROUP_NAME))
        return queryset


class StatAccessControlMixin:
    """ Проверка на право просмотра статистики по рассылке """
    def dispatch(self, request, *args, **kwargs):
        obj_mailing = get_object_or_404(Mailing, pk=kwargs.get("pk"))
        user = request.user
        if not is_manager(user) and not is_owner(obj_mailing, user):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
