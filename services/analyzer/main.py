from celery import Celery
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
app = Celery("analyzer", broker=REDIS_URL, backend=REDIS_URL)
app.conf.task_routes = {"tasks.analyze.*": {"queue": "analysis"}}
app.autodiscover_tasks(["tasks"])
