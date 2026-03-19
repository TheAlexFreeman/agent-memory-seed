---
source: agent-generated
type: research-plan
origin_session: chats/2026/03/18/chat-001
created: 2026-03-18
last_verified: 2026-03-18
trust: medium
status: active
next_action: "Begin Phase 2 — write knowledge/_unverified/devops/nginx-django-react.md"
---

# Research Plan: DevOps — Docker, Vite, and Dev-Ops Tooling for the Full Stack

## Goals

Alex runs a Django + React + Celery + Redis + Postgres stack with multiple Celery worker roles. The goal is deep, practical coverage of how to compose, configure, run, and deploy that stack using Docker and related tooling — from local development ergonomics through CI/CD and zero-downtime production deploys.

This plan covers infrastructure and workflow; it is not a repeat of the Django or React knowledge files. Cross-references to existing files are noted throughout.

---

## Existing coverage (do not duplicate)

- `django-production-stack.md` — high-level architecture: service boundaries, startup ordering, Redis topology, static/media handling, health check philosophy, secrets discipline. **This plan goes deeper into the implementation of everything that file describes.**
- `django-observability-structlog-sentry.md` — structlog, django-structlog, Celery logging, Sentry tracing/sampling, cache spans
- `celery-advanced-patterns.md` — `on_commit`, idempotency, `acks_late`, queue design; Flower mentioned briefly
- `django-gunicorn-uvicorn.md` *(planned in django-stack-research Phase 6)* — gunicorn/uvicorn tuning, static files with whitenoise, multi-stage Docker build for Django, `django-environ`
- `vite-react-build.md` *(planned in react-stack-research Phase 7)* — Vite config, proxy for DRF in dev, multi-stage Docker build for React (node → nginx), `nginx.conf` for SPA fallback

**Important scope note**: `django-gunicorn-uvicorn.md` and `vite-react-build.md` cover their respective app-level Docker build concerns. This plan covers the *composition layer*: how all services are wired together in Compose, how nginx routes between them, how CI/CD builds and deploys the combined system, and how the development workflow is managed day-to-day.

---

## Output file structure: `knowledge/_unverified/devops/`

New top-level subject folder. Add a `SUMMARY.md` when writing the first file.

---

## Research phases and priority order

### Phase 1 — Local development environment (highest priority) · ☑ 2/2 complete

The daily development environment is where most friction lives and where the complexity of multiple Celery workers first becomes concrete. Getting this right has immediate payoff.

1. ☑ `docker-compose-local-dev.md`
   - **Full service definition**: `web` (Django + gunicorn or `runserver`), `celery-worker` (one or more), `celery-beat`, `postgres`, `redis`, optional `flower`; all sharing one backend image built from the same `Dockerfile`
   - **`depends_on` with health checks**: `service_healthy` condition, writing actual healthcheck commands for Postgres (`pg_isready`) and Redis (`redis-cli ping`); why `depends_on: [postgres]` alone is not enough
   - **Volume mounts for hot reload**: bind-mounting the Django source for `runserver --reload`, the Celery `--autoreload` flag, when to use it and its caveats in production-like setups
   - **`docker-compose.override.yml` pattern**: base `docker-compose.yml` that works for all environments, `override.yml` for dev-only settings (bind mounts, debugpy port exposure, `command` overrides), `.gitignore` for personal overrides
   - **Environment variable management in dev**: `.env` file, `env_file:` directive, `environment:` overrides, `docker compose config` to see resolved values, never committing `.env`
   - **Networking**: default bridge network, service DNS resolution (services reference each other by name), exposing ports selectively for local access vs. internal-only
   - **Named volumes vs. bind mounts**: Postgres data volume, node_modules exclusion pattern for React services, volume lifecycle (`docker compose down -v` implications)
   - **Running management commands**: `docker compose exec web python manage.py migrate`, `createsuperuser`, `shell_plus`; aliases and Makefile targets for common commands
   - **Log handling in dev**: `docker compose logs -f --tail=50 web celery-worker`, per-service log following, structlog's dev vs. production renderer (`ConsoleRenderer` in dev)

2. ☑ `celery-multi-worker-docker.md`
   - **Why multiple worker containers**: different task types need different pool types and concurrency — a gevent worker for outbound HTTP tasks should not share a process with a prefork worker doing CPU-intensive PDF generation
   - **Naming and queue assignment in Compose**: `celery-worker-default`, `celery-worker-io`, `celery-worker-heavy` as separate services each running `celery -A app worker -Q <queue> --pool=<pool> --concurrency=<n>`
   - **Pool type per worker**: gevent for I/O-bound (HTTP, email, lightweight DB reads), prefork for CPU-bound (image processing, PDF, report generation), solo for debug/test, threads as occasional alternative
   - **Concurrency tuning**: prefork formula (`2 * CPU + 1` starting point), gevent high concurrency (100–500 depending on I/O wait), `CELERYD_MAX_TASKS_PER_CHILD` for prefork memory hygiene
   - **Resource limits in Compose**: `deploy.resources.limits` (memory, CPU), why memory limits matter for prefork workers, OOM kill behavior and task implications
   - **Scaling a single worker service**: `docker compose up --scale celery-worker-io=3` vs. separate named services; tradeoffs for local dev vs. production
   - **Shared image, different entrypoints**: one `Dockerfile`, `command:` override per service in Compose, entrypoint script pattern for `celery` vs. `gunicorn` vs. `beat` from the same image
   - **Beat in Compose**: one and only one beat container, `restart: unless-stopped`, why running beat on multiple containers is dangerous (duplicate task firing), `django-celery-beat` for DB-backed schedules in multi-replica environments
   - **Worker health checks**: Celery's `celery inspect ping`, writing a Compose healthcheck for a worker, `celery_worker_heartbeat` Prometheus metric
   - **Graceful shutdown in Compose**: `stop_grace_period`, `stop_signal: SIGTERM`, Celery warm shutdown vs. cold shutdown, `worker_cancel_long_running_tasks_on_connection_loss`

---

### Phase 2 — Nginx as the composition layer · ☐ 0/1 complete

3. ☐ `nginx-django-react.md`
   - **Role of nginx in this stack**: TLS termination, reverse proxy to gunicorn, serving React SPA static build, WebSocket proxying (if using Django Channels or similar), rate limiting, compression — keeps gunicorn and the React build cleanly separate
   - **Basic proxy to gunicorn**: `proxy_pass http://web:8000`, `proxy_set_header` for `Host`, `X-Real-IP`, `X-Forwarded-For`, `X-Forwarded-Proto`; `proxy_read_timeout` for long-running views
   - **Serving the React SPA**: `root /usr/share/nginx/html`, `try_files $uri $uri/ /index.html` for client-side routing, `index index.html`; the distinction between assets that get cache-busted filenames (immutable caching) and `index.html` (no-cache)
   - **Cache-control headers**: `location ~* \.(js|css|png|svg|woff2)$` with `Cache-Control: public, max-age=31536000, immutable` for fingerprinted assets; `Cache-Control: no-cache, no-store` for `index.html`
   - **API routing**: `location /api/` and `location /admin/` proxied to Django; `location /` serving React; order matters
   - **WebSocket proxying**: `proxy_http_version 1.1`, `Upgrade` and `Connection` headers for Django Channels (`/ws/`)
   - **TLS with Let's Encrypt**: certbot + `certbot/certbot` Docker image, Diffie-Hellman params, `ssl_protocols`, `ssl_ciphers`, HTTP → HTTPS redirect, HSTS header
   - **Gzip compression**: `gzip on`, `gzip_types`, `gzip_min_length`, `gzip_comp_level`, Brotli alternative
   - **Rate limiting**: `limit_req_zone` for login endpoints and API, `limit_req` directive, `burst` and `nodelay`
   - **nginx in Compose**: `nginx` or `nginx:alpine` image, `volumes` for the React build output and TLS certs, `ports: 80:80` and `443:443`, `depends_on: web`
   - **Static files from Django**: serving `STATIC_ROOT` via nginx `location /static/` vs. whitenoise — nginx is faster for high traffic, whitenoise is simpler for small deploys

---

### Phase 3 — Production Docker configuration · ☐ 0/1 complete

4. ☐ `docker-production-config.md`
   - **Multi-stage Dockerfile for Django**: `base` stage (Python deps), `dev` stage (dev tools, bind mounts), `production` stage (`collectstatic`, non-root user, no dev deps); `COPY --chown` for file ownership
   - **Image tagging and versioning**: tag by git SHA (`ghcr.io/org/app:${{ github.sha }}`), `latest` as a convenience alias, why pinning to SHAs in Compose files matters for rollback
   - **`docker-compose.prod.yml`**: no bind mounts, explicit image tags, `restart: unless-stopped` or `on-failure:3`, removed dev ports, production environment variables, `logging` driver (json-file with rotation, or `fluentd`/`loki`)
   - **Secrets at runtime**: never `COPY .env` or `ARG SECRET_KEY` in Dockerfile; pass secrets via environment variables injected by the deployment system (CI/CD secrets, AWS Secrets Manager + `envconsul`, Docker Swarm secrets, Kubernetes Secrets); `django-environ` reading from env
   - **Entrypoint script pattern**: `entrypoint.sh` that waits for Postgres (with `wait-for-it.sh` or `pg_isready` loop), runs `migrate`, then `exec "$@"` — used by `web` and `celery-*` services alike, with `command:` per service
   - **Non-root user**: `RUN adduser --disabled-password --gecos '' appuser`, `USER appuser`, file permission implications for `collectstatic` and `MEDIA_ROOT`
   - **Read-only containers**: `read_only: true` in Compose, `tmpfs:` for `/tmp` and cache dirs, security benefit vs. operational friction
   - **Resource limits**: `deploy.resources` in Compose v3, memory and CPU limits per service, implications for Celery prefork workers (memory per child process × concurrency)
   - **Log rotation**: `json-file` driver with `max-size` and `max-file`, avoiding unbounded log disk usage on long-running servers

---

### Phase 4 — CI/CD · ☐ 0/1 complete

5. ☐ `github-actions-cicd.md`
   - **Pipeline structure**: two-stage pipeline — (1) test + lint, (2) build + push + deploy; test stage runs on every push, deploy stage runs on merge to `main` (or tag)
   - **Django test job**: `services:` for Postgres and Redis in GH Actions, `pytest` with `--reuse-db`, coverage reporting, caching pip deps with `actions/cache`
   - **React test + build job**: `node` setup, `npm ci`, `vitest --run`, `vite build`, uploading the build artifact for the deploy job
   - **Docker build and push**: `docker/setup-buildx-action`, `docker/login-action` for GHCR, `docker/build-push-action` with `cache-from: type=gha` and `cache-to: type=gha,mode=max` for layer caching, tagging with git SHA
   - **Build matrix**: building Django and React images in parallel, `needs:` for sequencing test → build → deploy
   - **Deploy job**: SSH deploy (`appleboy/ssh-action`), `docker compose pull && docker compose up -d --no-build` pattern; or registry-based `watchtower` auto-deploy
   - **Pre-deploy migration**: running `docker compose exec web python manage.py migrate --check` before deploy, or a dedicated `migrate` job that runs before `up`
   - **Secrets in GH Actions**: `secrets.` context, `DOCKER_PASSWORD`, `SSH_PRIVATE_KEY`, `DATABASE_URL` for test job, never logging secrets, `gh secret set` for management
   - **Caching strategies**: pip cache, npm cache, Docker layer cache with buildx; cache invalidation on `requirements.txt` or `package-lock.json` changes
   - **Branch protection and required checks**: requiring CI pass before merge, enforcing deploy-only-from-main discipline
   - **Linting in CI**: `ruff check`, `mypy`, `eslint`, `prettier --check` as fast pre-test gates; `pre-commit run --all-files` as an alternative

---

### Phase 5 — Zero-downtime deploys · ☐ 0/1 complete

6. ☐ `zero-downtime-deploys.md`
   - **The fundamental problem**: old and new code run simultaneously during a rolling deploy; database schema, task signatures, and API contracts must be compatible across versions
   - **Migration strategy**: run `migrate` as a separate step *before* bringing up the new app containers; additive-first migrations (add nullable column → backfill → make non-null in a later deploy); `SeparateDatabaseAndState` for zero-downtime renames (cross-reference `django-migrations-advanced.md` from django plan)
   - **Celery task versioning**: tasks in flight during a deploy may use old or new signatures; use `bind=True` + kwargs for forward compatibility, avoid positional-only task args
   - **Graceful worker drain before deploy**: `SIGTERM` sends warm shutdown (finishes current task, rejects new ones); `stop_grace_period` in Compose; draining a queue before pulling new workers vs. letting in-flight tasks complete
   - **Blue-green with Docker Compose**: running two Compose stacks simultaneously on one host (or two hosts), switching nginx upstream, verifying the green stack before removing blue; teardown procedure
   - **Rolling update on a single host**: `docker compose up -d --no-deps web` to update only the web service, then workers, then beat; the risk window where web and worker run different versions
   - **Health check gates**: `--wait` flag (Docker Compose v2.22+), waiting for healthchecks to pass before sending traffic; nginx `upstream` with health checks
   - **Rollback procedure**: `docker compose pull web && docker compose up -d web` with the previous SHA tag; having the previous image locally cached or in registry; database rollback limitations (forward-only migrations)
   - **Smoke tests post-deploy**: a simple `curl /health/` check, a task dispatch + result poll, integrated into the CI/CD deploy job as a verification step

---

### Phase 6 — Secrets and environment management · ☐ 0/1 complete

7. ☐ `environment-secrets-management.md`
   - **The three environments and their needs**: local dev (`.env` file, fake secrets fine), staging (real infrastructure, secrets from CI/deployment system), production (secrets from secrets manager or environment injection, never on disk in plaintext)
   - **`.env` file conventions**: `.env` (local, gitignored), `.env.example` (committed, all keys with placeholder values, documents required config), `.env.test` (test-specific overrides), Compose `env_file:` vs. `environment:` precedence
   - **`django-environ`**: `Env()` object, `env.db()`, `env.cache()`, `env.email()` URL-style parsers, `env.bool()` / `env.int()` / `env.list()`, `overwrite=True` for test env, `read_env()` call in `settings.py`
   - **Vite env vars in CI**: `VITE_` prefix requirement, injecting at build time (`--env-file` or env vars in GH Actions), the distinction between build-time baked values and runtime-fetched config (API base URL as build-time vs. runtime)
   - **Runtime config API pattern**: serving a `/config.json` endpoint from Django that the React app fetches on startup — allows changing API URLs, feature flags, and non-secret config without a rebuild
   - **Production secrets injection**: environment variables from CI/CD (GH Actions secrets → `docker compose up -e`), AWS Secrets Manager with `envconsul` or custom entrypoint fetching, Vault agent sidecar; when each approach makes sense
   - **Secret rotation without downtime**: dual-write period for credential rotation (old and new credentials accepted simultaneously), then swap, then revoke old; Django's `SECRET_KEY_FALLBACKS` for session/cookie key rotation
   - **What must never be in images**: `SECRET_KEY`, database passwords, API keys; enforcing via `.dockerignore` (exclude `.env`), Dockerfile `ARG` vs. `ENV` distinction (ARGs visible in image history)
   - **Audit and hygiene**: `git secrets` or `truffleHog` in pre-commit to catch accidental commits, `docker history --no-trunc` to check for leaked build args

---

### Phase 7 — Celery monitoring · ☐ 0/1 complete

8. ☐ `celery-flower-monitoring.md`
   - **Flower**: setup as a Compose service (`mher/flower` image or `celery -A app flower`), `--basic-auth` for access control, `--url-prefix` for nginx proxying, what it shows (active tasks, task history, worker status, queue lengths) and its limitations (in-memory state, restarts lose history)
   - **`django-prometheus`**: `django_prometheus` middleware, `ExportModelOperationsMixin` for ORM metrics, Celery task metrics via `celery-prometheus-exporter` or custom signals, `prometheus_client` for custom metrics
   - **Key Celery metrics to track**: `celery_task_received_total`, `celery_task_succeeded_total`, `celery_task_failed_total`, `celery_task_runtime_seconds` (latency histogram), `celery_worker_tasks_active`, queue depth via Redis `LLEN` on broker queues
   - **Prometheus scrape config**: `prometheus.yml` `scrape_configs` for Django, Celery exporter, Postgres exporter (`postgres_exporter`), Redis exporter
   - **Grafana dashboards**: Docker Compose Grafana service with provisioned datasources and dashboards, pre-built dashboards for Django/Celery from Grafana Labs
   - **Queue depth alerting**: alerting when a queue exceeds a depth threshold (tasks backing up), dead-letter queue depth as a critical alert, worker heartbeat loss detection
   - **Postgres monitoring**: `pg_stat_statements` for slow queries, `postgres_exporter` for connection count, cache hit rate, replication lag; integrating with Grafana
   - **Log aggregation**: Promtail + Loki as the lightweight ELK alternative for Compose-based stacks, `loki` Docker logging driver, querying logs in Grafana alongside metrics

---

### Phase 8 — Database operations · ☐ 0/1 complete

9. ☐ `docker-database-ops.md`
   - **`pg_dump` / `pg_restore` in Docker**: `docker compose exec postgres pg_dump -U $USER $DB > backup.sql`, restoring with `psql`, automating with a cron container or host cron job, storing backups to S3 with `aws s3 cp`
   - **Seeding dev data**: `manage.py loaddata` with fixtures, `manage.py seed` custom command with `factory_boy`, loading a sanitized production dump for realistic local development, `--flush` before seed discipline
   - **Migration execution in CD**: dedicated `migrate` step before app rollout, `manage.py migrate --check` as a CI gate (fails if unapplied migrations exist), `manage.py showmigrations` for debugging
   - **Management commands via Compose**: `docker compose run --rm web python manage.py <cmd>` for one-off commands in production, `--rm` to avoid accumulating stopped containers, logging output to CI/CD job
   - **Database initialization on first start**: Postgres `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` env vars, init scripts in `/docker-entrypoint-initdb.d/`, `migrate` + `createsuperuser` in entrypoint for fresh environments
   - **Backup automation**: `prodrigestivill/postgres-backup-local` or `offen/docker-volume-backup` for automated daily backups, retention policies, off-site copy to S3, backup verification (restore-and-check in staging)
   - **Volume inspection and data recovery**: `docker volume ls`, `docker volume inspect`, accessing volume data from a temporary container, disaster recovery checklist

---

### Phase 9 — Development workflow tooling · ☐ 0/1 complete

10. ☐ `dev-workflow-tooling.md`
    - **Makefile as the dev interface**: `make up`, `make down`, `make logs`, `make shell`, `make migrate`, `make test`, `make lint`, `make build` — a standard Makefile that wraps Docker Compose commands; `.PHONY` declarations; self-documenting targets with `##` comments and a `help` target
    - **pre-commit hooks**: `pre-commit` framework, `.pre-commit-config.yaml`, hooks for `ruff` (lint + format), `mypy`, `djhtml` (Django template formatting), `eslint`, `prettier`, `detect-secrets`; `pre-commit install`, running in CI with `pre-commit run --all-files`
    - **`ruff` configuration**: replacing `black` + `isort` + `flake8` + `pyupgrade` with one tool, `ruff.toml` or `pyproject.toml` config, `ruff check --fix`, `ruff format`, Django-specific rules (`DJ` codes), line length, per-file ignores
    - **`mypy` in Django**: `django-stubs`, `djangorestframework-stubs`, `mypy.ini` / `pyproject.toml` config, `strict = true` path, incremental type checking, `reveal_type` debugging, common Django patterns that trip up mypy
    - **Remote debugging Django in Docker**: `debugpy` (`python -m debugpy --listen 0.0.0.0:5678 --wait-for-client -m gunicorn ...`), VS Code `launch.json` `Remote Attach` config, exposing debug port in `docker-compose.override.yml` only, `import debugpy; debugpy.breakpoint()` in code
    - **Frontend dev server alongside Docker backend**: Vite dev server on the host (not in Docker) proxying to Django in Docker, `vite.config.ts` proxy config pointing to `localhost:8000`, HMR working without Docker overhead
    - **`watch` mode in Compose** (Docker Compose v2.22+): `develop.watch:` with `action: sync` for hot reload without bind mounts — alternative to bind mounts that avoids file permission issues on some host OSes
    - **Environment parity checklist**: keeping dev, CI, staging, and production as close as possible; documenting divergences explicitly; `docker compose config` to verify resolved config, `docker inspect` for runtime verification

---

## Progress log

| Date | Action |
|---|---|
| 2026-03-18 | Plan created; existing coverage reviewed, scope defined to avoid duplication with django-production-stack.md, django-gunicorn-uvicorn.md (planned), and vite-react-build.md (planned) |
| 2026-03-18 | Created knowledge/_unverified/devops/ folder and SUMMARY.md |
| 2026-03-18 | Wrote docker-compose-local-dev.md: full service definition, depends_on health checks, override pattern, env management, networking, volumes, management commands, hot reload, Vite-outside-Docker pattern |
| 2026-03-18 | Wrote celery-multi-worker-docker.md: three-worker pattern, queue routing, pool selection, concurrency tuning, gevent patching, resource limits, shared image/entrypoint, beat singleton, worker healthchecks, graceful shutdown, scaling; Phase 1 complete |

---

## Notes

- **Scope boundary**: `django-gunicorn-uvicorn.md` (django plan) covers the Django app's Dockerfile and process model. `vite-react-build.md` (react plan) covers the React build Dockerfile and nginx SPA config. This plan covers how all services are *composed*, *wired*, *deployed*, and *operated* together.
- **Cross-references**: Several files here will link to `django-migrations-advanced.md` (zero-downtime), `celery-worker-beat-ops.md` (pool types, graceful shutdown), and `django-security.md` (secrets) from the django plan.
- **File count**: 10 files planned. All go to `knowledge/_unverified/devops/`.
- **New folder**: `knowledge/_unverified/devops/` does not yet exist; create `SUMMARY.md` when writing the first file.
