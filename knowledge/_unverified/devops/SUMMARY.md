# DevOps Knowledge — Summary

Infrastructure and workflow knowledge for Alex's Django + React + Celery + Redis + Postgres stack. Covers the composition layer: how services are wired together, deployed, and operated. App-level Dockerfiles are covered separately in `knowledge/_unverified/django/django-gunicorn-uvicorn.md` and `knowledge/_unverified/react/vite-react-build.md`.

## Files

| File | Topics |
|---|---|
| `docker-compose-local-dev.md` | Full-stack Compose setup, depends_on health checks, override pattern, env management, volumes, management commands, log handling |
| `celery-multi-worker-docker.md` | Multiple worker containers by queue/pool type, concurrency tuning, resource limits, beat singleton, graceful shutdown |

## Cross-references

- `../django/celery-worker-beat-ops.md` — pool type detail, beat configuration, graceful shutdown signals
- `../django/django-production-stack.md` — high-level service architecture (this folder goes deeper on implementation)
- `../django/django-migrations-advanced.md` — zero-downtime migration patterns (referenced from zero-downtime-deploys.md)
- `../django/django-observability-structlog-sentry.md` — structlog/Sentry (referenced from celery-flower-monitoring.md)
