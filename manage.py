#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path

def main():
    try:    
        from dotenv import load_dotenv
    except ImportError as exc:
        raise ImportError("Couldn't import dotenv. Check if it is installed.") from exc

    env_dir = Path(__file__).resolve().parent / '.env'
    
    if env_dir:
        load_dotenv(dotenv_path='.env')
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ODSMAP.settings.dev')
        print('Could not load the env vars using dotenv.load_dotenv. Setting default settings module to ODSMAP.settings.dev.')
    """Run administrative tasks."""
    # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ODSMAP.settings')
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
