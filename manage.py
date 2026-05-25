#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


def create_superuser():
    """Создает суперпользователя при деплое на Render."""
    if not os.environ.get('RENDER'):
        return

    print("Running on Render, checking/creating superuser...")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    import django
    django.setup()

    from django.contrib.auth import get_user_model
    User = get_user_model()

    username = "angelina"
    email = "maley.gelya@mail.ru"
    password = "fyutkbyf"

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"Суперпользователь '{username}' успешно создан!")
    else:
        print(f"Суперпользователь '{username}' уже существует.")


if __name__ == '__main__':
    # Создаем суперпользователя ТОЛЬКО на Render
    if os.environ.get('RENDER'):
        create_superuser()
    main()
