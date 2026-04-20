import os
import sys

if sys.platform == "win32":
    sys.exit(
        "[错误] Gunicorn 不支持 Windows 系统。\n"
        "请改用 Waitress 启动: python serve.py"
    )

bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
workers = int(os.getenv('GUNICORN_WORKERS', '2'))
accesslog = '-'
loglevel = os.getenv('GUNICORN_LOGLEVEL', 'info')
capture_output = True
enable_stdio_inheritance = True
