import os


bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
workers = int(os.getenv('GUNICORN_WORKERS', '2'))
accesslog = '-'
loglevel = os.getenv('GUNICORN_LOGLEVEL', 'info')
capture_output = True
enable_stdio_inheritance = True
