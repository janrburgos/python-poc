import time
import datetime
from celery.schedules import crontab
from app.celery import celery


@celery.task(name="sample_task")
def sample_task(a: int, b: int, c: int) -> int:
    print("Running sample task...")
    time.sleep(a)
    print("End sample task...")
    return b + c


@celery.task(name="say_something")
def say_something(msg: str = None) -> None:
    print(f"{datetime.datetime.now()} {msg or 'Hello'}")


@celery.on_after_configure.connect
def setup_periodic_tasks(sender: celery, **kwargs):
    sender.add_periodic_task(
        5.0, say_something.s("Holla!"), name="run every 5 second interval"
    )

    sender.add_periodic_task(
        crontab(minute="*"),
        say_something.s("Uh oh! Hotdog!"),
        name="run every minute schedule",
    )
