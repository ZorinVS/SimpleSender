from django.contrib.auth.views import LogoutView
from django.urls import path

from users import views
from users.apps import UsersConfig

app_name = UsersConfig.name

urlpatterns = [
    path("", views.UserListView.as_view(), name="user_list"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("email-confirm/<str:token>/", views.email_verification, name="email_confirm"),
    path("password-reset/", views.PasswordResetView.as_view(), name="password_reset"),
    path("password-reset-confirm/<str:token>/", views.password_reset_confirm, name="password_reset-confirm"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/<int:pk>/edit/", views.UserUpdateView.as_view(), name="user_update"),
    path("profile/<int:pk>/block/", views.UserBlockView.as_view(), name="user_block"),
    path("profile/<int:pk>/", views.UserDetailView.as_view(), name="user_detail"),
]
