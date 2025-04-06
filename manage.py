#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import os
from dotenv import load_dotenv

load_dotenv()
if not os.getenv("DATABASE_URL"):
    raise Exception("❌ Не найдена переменная окружения DATABASE_URL. Проверь .env файл!")

if not os.getenv("SECRET_KEY"):
    raise Exception("❌ Не найдена переменная окружения SECRET_KEY. Проверь .env файл!")

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exchange_rates.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
