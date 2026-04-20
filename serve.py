import sys

if sys.version_info[:2] != (3, 12):
    sys.exit(
        f"[启动失败] 当前 Python 版本为 {sys.version.split()[0]}，"
        f"本项目要求 Python 3.12.x。\n"
        f"请安装 Python 3.12 后重试: https://www.python.org/downloads/"
    )

import os

from waitress import serve

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

from core.wsgi import application


def main():
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    threads = int(os.getenv("WAITRESS_THREADS", "4"))
    serve(application, host=host, port=port, threads=threads)


if __name__ == "__main__":
    main()
