#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import environ

def main():
    """Run administrative tasks."""
    # Initialize environment reader
    env = environ.Env()

    # Read the .env file (located in project root, alongside manage.py)
    env.read_env()

    # Set DJANGO_SETTINGS_MODULE from env var or fallback to development
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        env.get("DJANGO_SETTINGS_MODULE", "agrosphere.settings.development")
    )

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()
