#!/usr/bin/env python
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
import sys

if sys.version_info[:2] != (3, 12):
    sys.exit(
        f"[启动失败] 当前 Python 版本为 {sys.version.split()[0]}，"
        f"本项目要求 Python 3.12.x。\n"
        f"请安装 Python 3.12 后重试: https://www.python.org/downloads/"
    )


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
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
