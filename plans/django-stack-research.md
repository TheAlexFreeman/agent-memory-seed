---
created: 2026-03-18
last_verified: '2026-03-19'
next_action: null
origin_session: chats/2026/03/18/chat-001
source: agent-generated
status: complete
trust: medium
type: research-plan
---

# Research Plan: Django Stack — Gaps and Depth

## Goals

Alex's stack is React + Django + Postgres + Celery + Redis + Docker. The existing Django knowledge base (9 files in `knowledge/_unverified/django/`) covers the fundamentals well but has significant gaps in production depth. This plan targets those gaps in priority order, with Celery expertise called out explicitly as a long-term accumulation goal.

Alex will review the existing Django files "soon" for potential promotion from `_unverified/`. New files from this plan also land in `knowledge/_unverified/django/` and follow the same promotion path.

---

## Existing coverage (do not duplicate)

- `django-6.0-whats-new.md` — template partials, `django.tasks`, built-in CSP, modernized email API, ORM additions, deprecations
- `django-tasks-framework.md` — `django.tasks` API, decision boundary with Celery
- `django-orm-postgres.md` — QuerySet patterns, FTS/Lexeme, ArrayField, ranges, GIN/GIST, CompositePK, migrations intro
- `django-caching-redis.md` — native RedisCache, stampede control, KEY_PREFIX/VERSION, invalidation
- `django-react-drf.md` — session vs JWT auth, CSRF/CORS, serializer patterns, cursor pagination, error contracts, `drf-spectacular` referenced but thin
- `django-production-stack.md` — service boundaries, startup ordering, Redis topology, health checks
- `celery-advanced-patterns.md` — `on_commit`, idempotency, `acks_late`, Canvas briefly, queue design, Flower limitations
- `drf-testing-pytest-django-perf-rec.md` — APIClient, `force_authenticate`, pytest-django, django-perf-rec (maintenance mode as of Aug 2025), `inline-snapshot-django` as successor
- `django-observability-structlog-sentry.md` — structlog contextvars, django-structlog, Celery logging, Sentry tracing/sampling, cache spans

---

## Research phases and priority order

### Phase 1 — Celery depth (highest priority) · ☑ 2/2 complete

Alex explicitly wants deep Celery expertise accumulated over time. The existing file is a good foundation but Canvas (chain/group/chord) is only briefly mentioned and worker ops are absent entirely.

1. ☑ `celery-canvas-in-depth.md`
   - **chain**: linear pipelines, result passing, error propagation (link_error), partial chains
   - **group**: parallel execution, result aggregation with `GroupResult`, fault tolerance patterns
   - **chord**: fan-out/fan-in, the callback, chord header vs. body, the chord unlock task, Redis/database backend implications for chord reliability
   - **chunks** and **starmap**: bulk processing patterns
   - **Canvas composition**: nesting chains inside groups, chords inside chords, when composition breaks and why
   - **Immutable signatures** (`si()`): when to use them, preventing unwanted result injection
   - **Error handling in Canvas**: `on_error` callbacks, partial completion semantics, idempotency considerations for multi-step pipelines
   - Real-world patterns: fan-out processing pipeline, parallel API calls with aggregation, multi-step data transformation

2. ☑ `celery-worker-beat-ops.md`
   - **Worker pool types**: prefork (CPU-bound, fork safety, `CELERYD_MAX_TASKS_PER_CHILD`), gevent/eventlet (I/O-bound, patching caveats, Django ORM thread safety), solo (single-threaded, debug-friendly), threads
   - **Concurrency tuning**: how to choose pool type and concurrency for a mixed workload (CPU tasks vs. HTTP tasks vs. DB tasks)
   - **`django-celery-beat`**: database-backed periodic tasks, `PeriodicTask` model, dynamic schedule management, the beat lock problem in multi-replica deployments
   - **Celery beat configuration** without `django-celery-beat`: `beat_schedule` in settings, crontab/solar/clocked schedules
   - **Worker autoscaling**: `--autoscale` flag, min/max concurrency, when it helps and when it doesn't
   - **Graceful shutdown**: `SIGTERM` vs. `SIGQUIT`, `worker_cancel_long_running_tasks_on_connection_loss`, draining queues before deploys
   - **Priority queues**: `CELERY_TASK_QUEUES`, `task_routes`, routing by task name vs. decorator queue argument
   - **Dead letter / retry exhaustion patterns**: what happens after `max_retries`, routing to a dead-letter queue for inspection

---

### Phase 2 — DRF and API depth · ☑ 2/2 complete

The existing `django-react-drf.md` is solid on basics but `drf-spectacular` deserves its own file and the testing file's `django-perf-rec` entry needs updating.

3. ☑ `drf-spectacular.md`
   - **Why**: `rest_framework`'s built-in schema generation is deprecated as of DRF 3.14; `drf-spectacular` is the community standard
   - **Setup**: `INSTALLED_APPS`, `SPECTACULAR_SETTINGS`, the `SpectacularAPIView` / `SpectacularSwaggerView` / `SpectacularRedocView` endpoints
   - **Schema annotation**: `@extend_schema`, `@extend_schema_view`, `OpenApiTypes`, `inline_serializer`
   - **Polymorphic responses**: `PolymorphicProxySerializer`, discriminator fields
   - **Customizing examples**: `OpenApiExample`, request/response examples by status code
   - **Handling JWT auth in the schema**: `SecurityScheme`, `SECURITY` setting
   - **Enum generation**: how drf-spectacular infers enums from `choices` fields; `ENUM_GENERATE_CHOICE_DESCRIPTION`
   - **Versioning**: URL-based vs. namespace-based versioning and how the schema reflects it
   - **CI validation**: `--validate` flag, checking schema drift in CI, `spectacular --file openapi.yaml`

4. ☑ `django-test-data-factories.md`
   - **factory_boy**: `DjangoModelFactory`, `Faker` integration, `SubFactory`, `RelatedFactory`, `LazyAttribute`, `LazyFunction`, `Trait`, `post_generation`
   - **Patterns for complex models**: many-to-many with `@factory.post_generation`, self-referential models, models with `unique_together`
   - **faker standalone**: generating realistic test data outside factories
   - **Mocking Celery tasks in tests**: `@override_settings(CELERY_TASK_ALWAYS_EAGER=True)` (legacy), `celery.contrib.pytest` fixtures (`celery_app`, `celery_worker`), `task.apply()` for synchronous testing, mocking with `unittest.mock.patch`
   - **freezegun**: `@freeze_time`, `freeze_time` context manager, freezing inside Celery tasks, interaction with `django.utils.timezone`
   - **responses / httpretty**: mocking outbound HTTP in tests (external API calls from tasks or views)
   - **Database state isolation**: `django_db` mark, `transaction=True` vs. default, `--reuse-db` behavior with factory state

---

### Phase 3 — Django async · ☑ 1/1 complete

The async model is absent from the current knowledge base entirely. Relevant because Alex may want to use async views for real-time features or high-concurrency endpoints.

5. ☑ `django-async.md`
   - **Async view basics**: `async def` views, `asgiref`, running under Daphne/uvicorn vs. gunicorn (sync workers)
   - **`sync_to_async` / `async_to_sync`**: when each is needed, thread sensitivity, `thread_sensitive=True` default behavior
   - **ORM in async context**: `sync_to_async(queryset.get)`, the `_default_manager` caveat, the coming native async ORM (Django roadmap)
   - **Async middleware**: the middleware stack in ASGI mode, which built-ins are async-safe
   - **Django Channels** (brief): websockets, `WebsocketConsumer` vs. `AsyncWebsocketConsumer`, channel layers with Redis, when to use Channels vs. SSE vs. polling
   - **Async vs. Celery**: decision guide — async views for fast I/O, Celery for background/slow/retryable work; the common mistake of using async views as a Celery substitute
   - **Testing async views**: `AsyncClient` (Django 4.1+), `pytest-asyncio` integration

---

### Phase 4 — Security · ☑ 1/1 complete

6. ☑ `django-security.md`
   - **Auth backends**: `ModelBackend`, custom auth backends, `authenticate()` / `get_user()` contract, `AUTHENTICATION_BACKENDS` multiple-backend chaining
   - **`django-allauth`**: setup for social auth (Google, GitHub), email verification flow, headless mode for DRF/SPA, account adapter customization
   - **Password security**: `PASSWORD_HASHERS`, Argon2 vs. PBKDF2, password validators
   - **HTTPS/HSTS in production**: `SECURE_SSL_REDIRECT`, `SECURE_HSTS_SECONDS`, `SECURE_HSTS_INCLUDE_SUBDOMAINS`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, Django's security check (`manage.py check --deploy`)
   - **Rate limiting**: `django-ratelimit` (view decorator approach), nginx-level rate limiting, rate limiting Celery task submission
   - **Secrets management**: `django-environ`, `python-decouple`, Vault/AWS Secrets Manager integration patterns, never committing secrets, rotating secrets without downtime
   - **Content Security Policy**: Django 6.0 built-in CSP (from `django-6.0-whats-new.md` — expand with nonce-based CSP, report-only mode)
   - **SQL injection surface**: ORM safety, `RawSQL` risks, `extra()` deprecation

---

### Phase 5 — Migrations depth · ☑ 1/1 complete

7. ☑ `django-migrations-advanced.md`
   - **`RunPython` data migrations**: forward and reverse functions, using `apps.get_model()` (not direct model imports), `atomic=False` for large tables
   - **`SeparateDatabaseAndState`**: zero-downtime rename pattern — add column in one deploy, backfill, switch code, drop old column
   - **Squashing migrations**: `squashmigrations` command, when to squash, `replaces` field, cleaning up squashed migrations after all instances upgraded
   - **Zero-downtime patterns**: adding nullable columns, removing columns safely (multi-step deploy), renaming models/fields without downtime
   - **Fake migrations**: `--fake`, `--fake-initial`, when legitimate vs. dangerous
   - **Migration conflicts**: concurrent branch development, resolving merge conflicts in migration files, `merge` migrations
   - **Large table migrations**: `pg_repack`, `django-pg-zero-downtime` approach, adding indexes concurrently (`AddIndexConcurrently`)
   - **Migration testing**: testing data migrations, testing `RunPython` reversibility

---

### Phase 6 — Deployment and infrastructure · ☑ 2/2 complete

8. ☑ `django-gunicorn-uvicorn.md`
   - **gunicorn**: sync workers (`gthread`, `gevent`), `--workers` formula (2*CPU+1), `--timeout`, `--keep-alive`, `--max-requests` (memory leak mitigation), graceful reload with `HUP`
   - **uvicorn**: `uvicorn.workers.UvicornWorker` under gunicorn (recommended production pattern), `--loop`, `--http`, lifecycle events
   - **ASGI vs. WSGI**: when to switch to ASGI (websockets, async views, streaming responses), running Django in WSGI + Channels in ASGI side-by-side
   - **Static files in production**: `whitenoise` vs. nginx, `collectstatic` in CI/CD, S3 for static files
   - **Docker multi-stage builds**: base → deps → dev/prod split, non-root user, health check `CMD`, minimizing layer cache invalidation
   - **`django-environ`**: `.env` file pattern, `Env` object, casting types, `db_url()` / `cache_url()` / `email_url()`, CI/CD environment injection

9. ☑ `django-database-pooling.md`
   - **Why pooling**: Django opens a new DB connection per thread/process per request; high traffic → connection exhaustion
   - **`CONN_MAX_AGE`**: persistent connections, the `CONN_HEALTH_CHECKS` setting (Django 4.1), when persistent connections hurt (pgBouncer + persistent = bad)
   - **pgBouncer**: session vs. transaction vs. statement pooling, why transaction pooling breaks `SET` statements and prepared statements (`DISCARD ALL`), Django's pgBouncer compatibility setting (`DISABLE_SERVER_SIDE_CURSORS`)
   - **`django-db-geventpool`**: gevent-based connection pooling for async/gevent workers
   - **Postgres parallel query**: `max_parallel_workers_per_gather`, when it engages, when it hurts (OLTP), `SET max_parallel_workers_per_gather = 0` for connection-heavy apps
   - **Table partitioning**: range/list/hash partitioning in Postgres, Django support via raw SQL migrations, when it helps (large time-series tables), `pg_partman` for automated partition management
   - **Monitoring connections**: `pg_stat_activity`, connection count alerts, `pg_stat_statements` for slow query identification

---

### Phase 7 — Storage and media files · ☑ 1/1 complete

10. ☑ `django-storages.md`
    - **`django-storages`**: S3/GCS/Azure backends, `DEFAULT_FILE_STORAGE` / `STORAGES` dict (Django 4.2+ new style), `STATICFILES_STORAGE`
    - **S3 setup**: `boto3`, `AWS_STORAGE_BUCKET_NAME`, `AWS_S3_REGION_NAME`, `AWS_S3_CUSTOM_DOMAIN` for CDN, `AWS_DEFAULT_ACL`
    - **Signed URLs**: `generate_presigned_url()` via boto3, time-limited access for private files, DRF endpoint pattern for returning signed URLs
    - **Direct upload to S3**: presigned POST approach (frontend uploads directly to S3, bypassing Django), `django-s3-file-field` / `s3direct` patterns
    - **User upload handling**: file type validation (magic bytes, not just extension), size limits (`FILE_UPLOAD_MAX_MEMORY_SIZE`), `django-cleanup` for deleting orphaned files
    - **Local dev fallback**: `django-storages`'s `FileSystemStorage` in development, `.env`-gated backend switching
    - **GCS alternative**: `django-storages[google]`, service account key vs. Workload Identity

---

## Progress log

| Date | Action |
|---|---|
| 2026-03-18 | Plan created; existing 9 Django files reviewed and gaps identified |
| 2026-03-18 | Wrote `knowledge/_unverified/django/celery-canvas-in-depth.md`; next up is `celery-worker-beat-ops.md` |
| 2026-03-18 | Wrote `knowledge/_unverified/django/celery-worker-beat-ops.md`; Phase 1 complete, next up is `drf-spectacular.md` |
| 2026-03-18 | Wrote `knowledge/_unverified/django/drf-spectacular.md`; covers setup, @extend_schema, JWT auth, enum/versioning/CI validation |
| 2026-03-18 | Wrote `knowledge/_unverified/django/django-test-data-factories.md`; covers factory_boy 3.3, Celery mocking patterns, freezegun, responses; Phase 2 complete |
| 2026-03-19 | Completed django-async.md (django-stack-research 5/10) |
| 2026-03-19 | Wrote django-security.md (Phase 4); django-migrations-advanced.md (Phase 5); django-gunicorn-uvicorn.md, django-database-pooling.md (Phase 6); django-storages.md (Phase 7) — all 10/10 complete |

---

## Notes

- **Promotion queue**: Alex will review the existing 9 Django files for promotion from `_unverified/` to `knowledge/django/`. New files from this plan land in `_unverified/django/` and join the same queue.
- **Celery accumulation goal**: phases 1–2 of Celery research are planned here; as Alex uses Celery in real projects, further files should be added organically.
- **File count**: 10 files planned. All go to `knowledge/_unverified/django/`.