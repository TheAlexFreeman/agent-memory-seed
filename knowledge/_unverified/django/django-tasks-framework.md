---
source: external-research
origin_session: chats/2026/03/18/chat-001
created: 2026-03-18
last_verified: 2026-03-18
trust: low
---

# Django 6.0 Tasks Framework (`django.tasks`)

Django 6.0 introduces a standardized background task API. This file covers it in depth because it directly intersects with Alex's Celery usage.

## What it is (and isn't)

`django.tasks` provides:
- A standard API for **defining** and **enqueueing** background tasks.
- Built-in backends: `DatabaseBackend`, `ImmediateBackend`, `DummyBackend`.

`django.tasks` does **not** provide:
- A worker process. You still need something external to execute tasks.
- Scheduling / cron. No periodic tasks.
- Task chaining, grouping, chords (no Canvas equivalent).
- Retry logic with backoff.
- Real-time monitoring (no Flower equivalent).

The framework's explicit design goal is a **backend-agnostic standard API**, so third-party packages can implement Celery-backed or other backends against the same interface.

## Core API

```python
# tasks.py
from django.tasks import task

@task()
def send_welcome_email(user_id: int) -> None:
    user = User.objects.get(pk=user_id)
    send_email(user.email)

# Enqueue from a view or anywhere:
result = send_welcome_email.enqueue(user_id=42)

# Check status later:
task_result = send_welcome_email.get_result(result.task_id)
print(task_result.status)  # PENDING, RUNNING, COMPLETE, FAILED
```

Task functions must be importable at module level (same constraint as Celery).

## Backends

### `DatabaseBackend` (production-viable)
Stores tasks in your SQL database. Works with Django's existing DB (Postgres in Alex's case).

```python
TASKS = {
    "default": {
        "BACKEND": "django.tasks.backends.database.DatabaseBackend",
    }
}
```

Key advantage: tasks can be enqueued **atomically within a database transaction** — no risk of enqueuing a task for work that then rolls back. This is one of Celery's most common footguns (task fires before transaction commits).

Requires running migrations (`django_tasks_*` tables). Requires a separate worker process — Django doesn't ship one; you'll need to build or find a third-party worker.

### `ImmediateBackend` (testing / dev)
Executes tasks synchronously, in-process, at enqueue time. No worker needed.

```python
TASKS = {
    "default": {
        "BACKEND": "django.tasks.backends.immediate.ImmediateBackend",
    }
}
```

### `DummyBackend` (testing)
Accepts tasks but never executes them. Results stay in `READY` state forever. Useful for unit tests that just verify enqueuing happened.

## Architectural significance vs. Celery

| Capability | `django.tasks` | Celery |
|---|---|---|
| Standard API | ✅ | Celery-specific |
| Worker included | ❌ | ✅ (celery worker) |
| DB broker (atomic enqueue) | ✅ | Via django-celery-results / transaction.on_commit |
| Redis/RabbitMQ broker | ❌ built-in | ✅ |
| Scheduling / cron | ❌ | ✅ (Celery Beat) |
| Task chains, groups, chords | ❌ | ✅ (Canvas) |
| Retry with backoff | ❌ | ✅ |
| Monitoring (Flower) | ❌ | ✅ |
| Priority queues | ❌ built-in | ✅ |

**Bottom line for Alex's stack:** For projects already using Celery for anything beyond fire-and-forget emails, `django.tasks` is not a replacement. It's additive — useful for simpler jobs where you want atomic enqueuing without Celery overhead, or as a migration path to standardize task definitions across projects.

The most interesting scenario: a future third-party package that implements a Celery backend for `django.tasks`. That would let you use the standard Django API while keeping Celery as the execution engine.

## Atomic task enqueuing (key pattern)

The `DatabaseBackend` enables the cleanest solution to a classic problem:

```python
# Bad (classic Celery footgun):
def create_order(user_id):
    order = Order.objects.create(user_id=user_id)
    send_confirmation.delay(order.id)  # fires BEFORE transaction commits
    # if transaction rolls back, task already fired

# With django.tasks DatabaseBackend, tasks enqueued in a transaction
# are not visible to workers until the transaction commits — automatically.
# No need for transaction.on_commit() wrappers.
```

With Celery, you'd use `transaction.on_commit(lambda: send_confirmation.delay(order.id))` to get the same safety. `django.tasks` makes this the default.

## When to use django.tasks vs. Celery

- **Use `django.tasks`** for: simple fire-and-forget jobs (email sends, webhook delivery), projects not already on Celery, or when you want atomic enqueue guarantees without the Celery broker layer.
- **Keep Celery** for: periodic tasks, complex workflows (chains/chords/groups), retries with backoff, priority queues, large-scale distributed processing, monitoring.
- **They can coexist** in the same project.

Last updated: 2026-03-18
