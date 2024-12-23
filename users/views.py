from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as BaseLoginView
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import FormView, UpdateView, DetailView, View, ListView

from mailings.services.mailing_service import cancel_mailing
from mailings.services.mixins import OwnerActionMixin, UserListManagerRequiredMixin, OwnerDetailMixin
from mailings.services.registration_service import AuthActionService
from mailings.services.utils import is_manager
from users import forms
from users.models import User


class LoginView(BaseLoginView):
    """ Вход на сайт """
    form_class = forms.LoginForm
    template_name = "users/login.html"


class RegisterView(FormView):
    """ Регистрация на сайте """
    form_class = forms.RegisterUserCreationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # Отправка письма для подтверждения почты
        if not AuthActionService.send_confirmation_email(user, host=self.request.get_host(), request=self.request):
            return self.form_invalid(form)
        return super().form_valid(form)


def email_verification(request, token):
    """ Верификация пользователя """
    AuthActionService.verify_token(token, request)
    return redirect("users:login")


class PasswordResetView(FormView):
    """ Восстановление пароля """
    form_class = forms.PasswordResetForm
    template_name = "users/password_reset.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        user = get_object_or_404(User, email=email)

        # Отправка письма для сброса пароля
        if not AuthActionService.send_confirmation_email(
                user, host=self.request.get_host(), request=self.request, action="password_reset"
        ):
            return self.form_invalid(form)
        return super().form_valid(form)


def password_reset_confirm(request, token):
    """ Сброс пароля """
    user = AuthActionService.verify_token(token, request, action="password_reset")
    if user is None:
        return redirect("users:password_reset")

    if request.method == "POST":
        form = forms.SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Ваш пароль был успешно изменен. Вы можете войти в систему")
            user.token = None  # удаление токена после смены пароля
            user.save()
            return redirect("users:login")
    else:
        form = forms.SetPasswordForm(user)

    return render(request, "users/password_reset_confirm.html", {"form": form})


class UserUpdateView(LoginRequiredMixin, OwnerActionMixin, UpdateView):
    """
    Обновление профиля
    Права доступа: владелец; администратор
    """
    model = User
    form_class = forms.UserForm
    success_url = reverse_lazy("mailings:index_page")


@method_decorator(cache_page(60 * 15), name="dispatch")
class UserListView(UserListManagerRequiredMixin, ListView):
    """
    Просмотр списка пользователей
    Права доступа: менеджер; администратор
    """
    model = User


class UserDetailView(LoginRequiredMixin, OwnerDetailMixin, DetailView):
    """
    Просмотр профиля
    Права доступа: владелец; менеджер; администратор
    """
    model = User
    context_object_name = "obj_user"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["is_manager"] = is_manager(self.object)
        return context_data


class UserBlockView(LoginRequiredMixin, View):
    """
    Блокировка пользователя
    Права доступа: менеджер; администратор
    """

    def post(self, request, pk):
        user = self.request.user  # текущий пользователь
        obj_user = get_object_or_404(User, pk=pk)  # блокируемый пользователь

        if not is_manager(user) or is_manager(obj_user):
            raise PermissionDenied

        # Отмена запланированных рассылок
        for mailing in obj_user.mailings.all():
            cancel_mailing(mailing)

        # Блокировка
        obj_user.is_active = False
        obj_user.save()

        return redirect("users:user_list")
