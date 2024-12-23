# simpleSENDER — сервис управления рассылками, администрирования и получения статистики

Этот проект представляет собой веб-приложение, разработанное с использованием Django, предназначенное для управления рассылками сообщений. Он позволяет пользователям создавать, редактировать и управлять рассылками, а также отправлять сообщения получателям как через интерфейс, так и через командную строку.

Проект состоит из двух частей:

- **Часть 1:** Разработка основы сервиса, включая модели для рассылок, сообщений и получателей, а также интерфейс для выполнения базовых CRUD-операций.
- **Часть 2:** Расширение функционала, добавление аутентификации и авторизации пользователей, управление правами доступа, настройка кеширования и планирование отправки сообщений.

## Основные возможности

- **Управление пользователями:**
  - Регистрация пользователей с подтверждением по email.
  - Аутентификация (вход/выход) и восстановление пароля.
  - Пользователи могут управлять только своими рассылками и получателями.

- **Управление рассылками и сообщениями:**
  - CRUD-операции для рассылок, сообщений и получателей.
  - Поддержка нескольких статусов рассылки: "Создана", "Запущена", "Завершена".
  - Возможность отправки сообщений по требованию через интерфейс или командную строку.
  
- **Попытки рассылки:**
  - Логирование каждой попытки рассылки, включая статус и ответ почтового сервера.
  
- **Отчеты и статистика:**
  - Страница с отчетами по рассылке каждого пользователя.
  - Статистика по успешным и неуспешным попыткам рассылки.
  
- **Управление доступом:**
  - Реализована система ролей с двумя основными ролями: обычный пользователь и менеджер.
  - Пользователи могут управлять только своими рассылками и получателями.
  - Менеджеры могут блокировать пользователей, отключать рассылки (с отменой отправки запланированных рассылок), просматривать все рассылки и получателей, но не могут изменять или удалять чужие данные.

- **Планирование:**
  - Реализована разовая отправка сообщений по запланированному времени с использованием `django-apscheduler`.

- **Кеширование:**
  - Добавлено серверное кеширование и кеширование целой страницы (users:user_list).

## Установка

1. Клонируйте репозиторий:
```bash
git clone git@github.com:ZorinVS/SimpleSender.git
```
2. Установите зависимости:
```bash
poetry install
```

## Подключение БД
1. Создайте БД
2. Создайте файл `.env` из файла `.env.sample`

## Применение миграций
```bash
python manage.py migrate
```

## Создание суперпользователя
- С помощью менеджера:
```bash
python3 manage.py createsuperuser
```
- С помощью кастомной команды:
```bash
python3 manage.py create_admin
```

## Создание группы Менеджеры
```bash
python3 manage.py create_managers
```

## Запуск
1. В командной строке: `redis-server`
2. В командной строке: `python3 manage.py runserver`
3. В браузере: http://127.0.0.1:8000/

## Отправка сообщений через командную строку
```bash
python3 manage.py send_mailing
```
