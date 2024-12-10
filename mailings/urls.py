"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
"""

from django.urls import path

from mailings import views
from mailings.apps import MailingsConfig

app_name = MailingsConfig.name

urlpatterns = [
    path("clients/", views.ClientListView.as_view(), name="client_list"),
    path("clients/add/", views.ClientCreateView.as_view(), name="client_create"),
    path("clients/excel_upload/", views.ClientUploadView.as_view(), name="client_upload"),
    path("clients/<int:pk>/delete/", views.ClientDeleteView.as_view(), name="client_delete"),
    path("clients/<int:pk>/edit/", views.ClientUpdateView.as_view(), name="client_update"),
    path("clients/<int:pk>/", views.ClientDetailView.as_view(), name="client_detail"),

    path("messages/", views.MessageListView.as_view(), name="message_list"),
    path("messages/add/", views.MessageCreateView.as_view(), name="message_create"),
    path("messages/<int:pk>/delete/", views.MessageDeleteView.as_view(), name="message_delete"),
    path("messages/<int:pk>/edit/", views.MessageUpdateView.as_view(), name="message_update"),
    path("messages/<int:pk>/", views.MessageDetailView.as_view(), name="message_detail"),

    path("mailings/", views.MailingListView.as_view(), name="mailing_list"),
    path("mailings/add/", views.MailingCreateView.as_view(), name="mailing_create"),
    path("mailings/<int:pk>/delete/", views.MailingDeleteView.as_view(), name="mailing_delete"),
    path("mailings/<int:pk>/edit/", views.MailingUpdateView.as_view(), name="mailing_update"),
    path("mailings/<int:pk>/", views.MailingDetailView.as_view(), name="mailing_detail"),
]
