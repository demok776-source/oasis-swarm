import multiprocessing
import os

bind = os.getenv("BIND", "0.0.0.0:8080")
workers = int(os.getenv("WORKERS", multiprocessing.cpu_count() * 2))
worker_class = "uvicorn.workers.UvicornWorker"
keepalive = int(os.getenv("KEEPALIVE", 65))
timeout = int(os.getenv("TIMEOUT", 600))
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info")
