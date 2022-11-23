#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testproject.settings.dev")

    from os.path import abspath, dirname, join

    PROJECT_ROOT = abspath(dirname(__file__))
    sys.path.append(join(PROJECT_ROOT, "../"))
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
