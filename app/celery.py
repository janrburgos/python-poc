import os
from celery import Celery

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

celery = Celery(
    "app",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["app.tasks"],
)

# Optional configuration, see the application user guide.
celery.conf.update(
    result_expires=3600,
    timezone="Asia/Manila",
)


if __name__ == "__main__":
    celery.start()
