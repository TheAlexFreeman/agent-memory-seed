---
source: external-research
origin_session: chats/2026/03/18/chat-001
created: 2026-03-18
last_verified: 2026-03-18
trust: low
---

# Django 6.0 — What's New

Released December 3, 2025. Supports Python 3.12, 3.13, and 3.14 only (drops 3.10 and 3.11).

## Four headline features

### 1. Template Partials
Named, reusable template fragments within a single template file. Eliminates the need to split small components into separate files.

```django
{% partialdef user-card %}
  <div class="card">{{ user.name }}</div>
{% endpartialdef user-card %}

{# render it: #}
{% partial user-card %}

{# inline option: define and render in place #}
{% partialdef hero inline %}
  <h1>{{ title }}</h1>
{% endpartialdef %}
```

Cross-file reference via `template_name#partial_name` syntax works with `get_template()`, `render()`, `{% include %}`, and other template-loading tools.

Partials receive the current context, so they work naturally inside loops. Use the `with` tag to adjust context as needed.

**Relevance for React stack:** Mostly relevant for server-rendered pages or HTMX workflows. Less directly relevant for SPA setups, but useful for admin UIs or hybrid pages.

### 2. Background Tasks (`django.tasks`)
A standardized API for defining and enqueueing background work. See `django-tasks-framework.md` for full detail — this is the most architecturally significant feature for teams using Celery.

### 3. Content Security Policy (CSP)
Built-in CSP support via `django.middleware.csp.ContentSecurityPolicyMiddleware`. Previously required the third-party `django-csp` (Mozilla) package.

```python
MIDDLEWARE = [
    "django.middleware.csp.ContentSecurityPolicyMiddleware",
    ...
]

from django.utils.csp import CSP

SECURE_CSP = {
    "default-src": [CSP.SELF],
    "script-src": [CSP.SELF, CSP.NONCE],  # enables per-request nonces
    "style-src": [CSP.SELF],
}

# Report-only mode for testing without enforcement:
SECURE_CSP_REPORT_ONLY = {
    "default-src": [CSP.SELF],
}
```

Add the `csp()` context processor to TEMPLATES to make `csp_nonce` available in templates. The middleware generates a unique nonce per request automatically.

Existing `django-csp` users will need to migrate; the APIs are similar but not identical.

### 4. Modernized Email API
Django now uses Python's modern `email.message.EmailMessage` (not the legacy Compat32 MIME classes). Cleaner, Unicode-friendly, and consistent with Python 3.6+ email API.

```python
# Before (still works in 6.0, but deprecated):
from email.mime.text import MIMEText
msg.attach(MIMEText("body"))

# After (modern API):
from email.message import MIMEPart
part = MIMEPart()
part.set_content("body")
msg.attach(part)
```

`EmailMessage.message()` now returns `email.message.EmailMessage` (not `SafeMIMEText`/`SafeMIMEMultipart`, which are deprecated). The `BadHeaderError` exception is also deprecated (Python's modern email raises `ValueError` for bad headers).

---

## ORM and database changes

- **`DEFAULT_AUTO_FIELD` changed to `BigAutoField`** — long-telegraphed since Django 3.2. If your project sets this explicitly, no change needed. New projects default to 64-bit PKs.
  - **Watch out:** Switching this on existing projects triggers migrations that need careful handling for auto-created M2M through tables (requires manual `RunSQL` to handle existing tables).
- **`RETURNING` clause optimization** — `GeneratedField` and expression-assigned fields are now refreshed via a single `RETURNING` query after `save()` on SQLite, PostgreSQL, and Oracle. Eliminates a separate `SELECT` after insert/update.
- **`StringAgg` aggregate** now available on all backends (previously PostgreSQL-only).
- **`AnyValue` aggregate** — returns an arbitrary non-null value from a group. Supported on SQLite, MySQL, Oracle, PostgreSQL 16+.
- **`QuerySet.raw()` supports `CompositePrimaryKey` models.**
- **Subqueries with `CompositePrimaryKey`** can now be the target of lookups beyond `__in` (e.g., `__exact`).
- **JSON field** now supports negative array indexing on SQLite.
- **ORM expression `params`** must now be tuples, not lists. Breaking for custom expressions.
- **`return_insert_columns` renamed to `returning_columns`** in the Database API.
- **PostgreSQL `CreateExtension` and related operations** now support an optional `hints` parameter for database router hints.
- **`BaseDatabaseSchemaEditor`** no longer uses `CASCADE` when dropping a column (more conservative and correct behavior).

---

## Async improvements

- Async QuerySet methods now work natively without `sync_to_async()` wrappers in many more contexts.
- `AsyncPaginator` and `AsyncPage` available for async views — no need to wrap pagination in `sync_to_async`.
- Async views are now more production-ready; Django 6.0 is considered the version where async Django moves from experimental to mainstream.

---

## Deprecations introduced in 6.0

- `ADMINS` / `MANAGERS` as list of `(name, address)` tuples → change to list of email address strings.
- `OrderableAggMixin` (PostgreSQL) → use the `order_by` attribute on `Aggregate` class.
- `orphans` argument ≥ `per_page` in `Paginator` / `AsyncPaginator` is deprecated.
- Percent sign in column alias or annotation name is deprecated.
- `EmailMessage.attach()` with legacy `MIMEBase` objects → use `MIMEPart`.
- `SafeMIMEText`, `SafeMIMEMultipart`, `BadHeaderError` → deprecated.
- Default protocol in `urlize` / `urlizetrunc` will change from HTTP to HTTPS in Django 7.0; opt in now via `URLIZE_ASSUME_HTTPS = True`.

---

## Features removed in 6.0 (end of deprecation cycle from 5.x)

- Positional arguments to `BaseConstraint` removed.
- See Django 5.0/5.1/5.2 deprecation notes for the complete list.

---

## Upgrade notes

- Run with `-Wall` on Django 5.2 first to surface all deprecations.
- Check `DEFAULT_AUTO_FIELD` setting — if unset, add `DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"` explicitly to avoid silent migration changes.
- Audit any custom ORM expressions that return `params` as lists.
- If using `django-csp`, plan migration to built-in CSP.
- If using `SafeMIMEText`/`SafeMIMEMultipart` directly, switch to Python's `email.message` API.

Last updated: 2026-03-18
