# Платформа самообучения

## Описание

Платформа самообучения студентов предоставляет возможность пользователям (студентам и преподавателям) взаимодействовать с курсами, материалами и тестами. Платформа включает функционал для регистрации, аутентификации, управления курсами и тестирования знаний.

## Технологии

- Python 3.x
- Django 4.x
- Django Rest Framework
- PostgreSQL
- JWT для аутентификации
- Docker (опционально)

## Установка

1. Клонирование репозитория

git clone https://github.com/Anastasiya-Nikolaeva/self_study_project.git

2. Создание виртуального окружения

python -m venv venv

source venv/bin/activate  # Для Linux/Mac

venv\Scripts\activate  # Для Windows

3. Установка зависимостей

pip install -r requirements.txt

4. Настройка базы данных

Заполните файл .env.sample

5. Применение миграций

python manage.py migrate

6. Создание суперпользователя

python manage.py createsuperuser

7. Запуск сервера

python manage.py runserver

Теперь вы можете получить доступ к платформе по адресу http://127.0.0.1:8000/.

## Тестирование
Для запуска тестов используйте следующую команду:

python manage.py test