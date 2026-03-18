---
source: external-research
origin_session: chats/2026/03/18/chat-001
created: 2026-03-18
last_verified: 2026-03-18
trust: low
---

# Celery Advanced Patterns

Covers Celery beyond the basics: Canvas workflows, routing, retries, and deployment. Focused on the Redis broker / Django / Postgres / Docker stack.

## Setup (Django + Celery + Redis)

```python
# myproject/celery.py
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
app = Celery("myproject")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# settings.py
CELERY_BROKER_URL = "redis://redis:6379/0"
CELERY_RESULT_BACKEND = "redis://redis:6379/0"
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True  # required in Celery 6+
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TIMEZONE = "UTC"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 300  # hard kill after 5 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 240  # raises SoftTimeLimitExceeded at 4 min
```

## Defining tasks

```python
from celery import shared_task
from myproject.celery import app

# With @shared_task (decoupled from app):
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_order(self, order_id: int) -> dict:
    try:
        order = Order.objects.get(pk=order_id)
        result = run_processing(order)
        return {"status": "ok", "order_id": order_id}
    except TemporaryError as exc:
        raise self.retry(exc=exc, countdown=2 ** self.request.retries * 10)
    except Exception as exc:
        raise  # don't retry; let Celery mark as FAILURE

# Explicit app registration:
@app.task(name="orders.process_order")
def process_order(order_id: int) -> dict:
    ...
```

**`bind=True`** gives access to `self` (the task instance), needed for `self.retry()`, `self.request.id`, etc.

## Retries with exponential backoff

```python
@shared_task(bind=True)
def call_external_api(self, payload: dict):
    try:
        return requests.post("https://api.example.com/", json=payload).json()
    except requests.RequestException as exc:
        # Exponential: 10s, 20s, 40s, 80s...
        raise self.retry(exc=exc, countdown=10 * (2 ** self.request.retries))
```

Or use Celery's built-in autoretry:

```python
@shared_task(
    autoretry_for=(requests.RequestException,),
    retry_kwargs={"max_retries": 5},
    retry_backoff=True,          # exponential
    retry_backoff_max=600,       # cap at 10 minutes
    retry_jitter=True,           # add randomness to prevent thundering herd
)
def call_external_api(payload: dict):
    ...
```

## Canvas: complex workflows

Celery Canvas is the workflow composition system. Three primitives:

### chain (sequential)
```python
from celery import chain

# Execute in order, passing result of each to next:
result = chain(
    fetch_data.s(user_id),
    process_data.s(),
    store_results.s(),
).apply_async()
```

### group (parallel)
```python
from celery import group

# Execute all in parallel, collect results:
result = group(
    process_item.s(item_id) for item_id in item_ids
).apply_async()

results = result.get()  # blocks until all complete
```

### chord (parallel → callback)
```python
from celery import chord

# Run group in parallel, then call callback with all results:
result = chord(
    group(process_item.s(item_id) for item_id in item_ids),
    aggregate_results.s()
).apply_async()
```

**Redis broker note:** Chords require the result backend (Redis here). `CELERY_RESULT_BACKEND` must be set.

**Redis priority note:** Redis broker sorts priorities **inversely** — 0 is highest priority, 9 is lowest. This is opposite to RabbitMQ.

### map / starmap
```python
# Simpler parallel: like group but more concise for uniform tasks:
process_item.map([1, 2, 3, 4]).apply_async()
process_pair.starmap([(1, "a"), (2, "b")]).apply_async()
```

## Task routing

Route different task types to different queues, then run specialized workers per queue:

```python
# settings.py
CELERY_TASK_ROUTES = {
    "myapp.tasks.send_email": {"queue": "email"},
    "myapp.tasks.generate_report": {"queue": "reports"},
    "myapp.tasks.scrape_*": {"queue": "scraping"},
}

CELERY_TASK_QUEUES = {
    "celery": {"exchange": "celery", "routing_key": "celery"},
    "email": {"exchange": "email", "routing_key": "email"},
    "reports": {"exchange": "reports", "routing_key": "reports"},
}
```

```bash
# Run workers bound to specific queues:
celery -A myproject worker -Q email --concurrency=4
celery -A myproject worker -Q reports --concurrency=2
celery -A myproject worker -Q celery,scraping --concurrency=8
```

## Priority queues (Redis)

```python
from kombu import Queue

CELERY_TASK_QUEUES = [
    Queue("default", routing_key="default", queue_arguments={"x-max-priority": 10}),
]

# Enqueue with priority (0 = highest in Redis):
my_task.apply_async(priority=0)   # high
my_task.apply_async(priority=5)   # medium
my_task.apply_async(priority=9)   # low
```

## Celery Beat (periodic tasks)

```python
# settings.py
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "cleanup-expired-sessions": {
        "task": "myapp.tasks.cleanup_expired_sessions",
        "schedule": crontab(hour=2, minute=0),  # daily at 2am
    },
    "sync-external-data": {
        "task": "myapp.tasks.sync_external_data",
        "schedule": 300.0,  # every 5 minutes
    },
}
```

```bash
# Run beat scheduler (one instance only):
celery -A myproject beat --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

Use `django-celery-beat` for DB-driven schedules you can edit at runtime without redeployment.

## Transaction safety (critical pattern)

Tasks that depend on DB state must fire **after** the transaction commits:

```python
from django.db import transaction

def create_order(user_id):
    with transaction.atomic():
        order = Order.objects.create(user_id=user_id)
        # Fires only after commit:
        transaction.on_commit(lambda: process_order.delay(order.id))
```

Without `on_commit`, the task may run before the transaction commits and fail to find the order (race condition). This is the most common Celery + Django bug.

Note: `django.tasks` `DatabaseBackend` solves this automatically.

## Concurrency tuning

```bash
# Prefork (default): CPU-bound work
celery -A myproject worker --pool=prefork --concurrency=4

# Gevent: I/O-bound (HTTP calls, DB-heavy tasks)
celery -A myproject worker --pool=gevent --concurrency=100

# Threads: mixed
celery -A myproject worker --pool=threads --concurrency=20
```

Rule of thumb:
- CPU-bound: `--concurrency` = number of CPU cores
- I/O-bound: `--concurrency` = 8–12× cores (with gevent)

## Docker Compose deployment

```yaml
# docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes

  django:
    build: .
    depends_on: [redis, postgres]

  celery_worker:
    build: .
    command: celery -A myproject worker --loglevel=info --concurrency=4
    depends_on: [redis, postgres]
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0

  celery_beat:
    build: .
    command: celery -A myproject beat --loglevel=info
    depends_on: [redis, postgres]
    # Only ever run ONE instance of beat

  flower:
    image: mher/flower
    command: celery --broker=redis://redis:6379/0 flower
    ports:
      - "5555:5555"
    depends_on: [redis]
```

## Monitoring with Flower

Flower provides real-time monitoring: active tasks, worker status, task history, queue lengths.

```bash
pip install flower
celery -A myproject flower --port=5555
```

In production, put Flower behind authentication and a reverse proxy.

## Task result management

Results stored in Redis expire by default. Configure:

```python
CELERY_RESULT_EXPIRES = 3600  # 1 hour (default: 1 day)
CELERY_TASK_IGNORE_RESULT = True  # for tasks where result doesn't matter (saves memory)
```

## Error handling patterns

```python
@app.task(bind=True)
def my_task(self, data):
    ...

# Override on_failure for alerting:
@app.task(bind=True)
def critical_task(self, data):
    ...

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        # Send alert, log to Sentry, etc.
        notify_team(f"Task {task_id} failed: {exc}")
```

Or use Celery signals:

```python
from celery.signals import task_failure

@task_failure.connect
def handle_task_failure(sender=None, task_id=None, exception=None, **kwargs):
    sentry_sdk.capture_exception(exception)
```

Last updated: 2026-03-18
