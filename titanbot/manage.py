#!/usr/bin/env python
import os
import sys

cwd = os.getcwd().split("\\")

if cwd not in sys.path:
    sys.path.append("\\".join(cwd))
if cwd[:-1] not in sys.path:
    sys.path.append("\\".join(cwd[:-1]))

sys.path.append("\\".join(cwd + ["titandash"]))

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'titanbot.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
