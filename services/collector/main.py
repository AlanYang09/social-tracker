from celery import Celery
from celery.schedules import crontab
from config import REDIS_URL

app = Celery("collector", broker=REDIS_URL, backend=REDIS_URL)

app.conf.task_routes = {
    "tasks.scrape_*": {"queue": "celery"},
}

app.conf.beat_schedule = {
    "scrape-stocktwits-every-5min": {
        "task": "tasks.scrape_keywords.scrape_stocktwits",
        "schedule": 300.0,
    },
    "scrape-reddit-every-5min": {
        "task": "tasks.scrape_keywords.scrape_reddit",
        "schedule": 300.0,
    },
    "scrape-nitter-every-10min": {
        "task": "tasks.scrape_keywords.scrape_nitter",
        "schedule": 600.0,
    },
    "snapshot-trends-every-15min": {
        "task": "tasks.snapshot.snapshot_trends",
        "schedule": 900.0,
    },
}

app.autodiscover_tasks(["tasks"])
