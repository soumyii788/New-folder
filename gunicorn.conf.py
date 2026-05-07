import multiprocessing
import os

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
threads = 4
worker_class = "sync" # or "uvicorn.workers.UvicornWorker" if using ASGI mostly
timeout = 120
keepalive = 5

loglevel = "info"
accesslog = "-"
errorlog = "-"

# Ensure Django environment is reachable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
