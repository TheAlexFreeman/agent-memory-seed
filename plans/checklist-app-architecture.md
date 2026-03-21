---
type: build
category: build
status: draft
next_action: Implement Phase 1 — Django project scaffold + Checklist/Item models
last_verified: 2026-03-21
trust: medium
---

# Checklist App — Django/React Architecture

Small task-management and progress-tracking tool. Aligned with Alex's stack: Django 6, DRF, React 19, Chakra UI 3, Postgres, TanStack Query.

## Scope

- **Checklists**: named lists of tasks (e.g. "Weekly review", "Release prep")
- **Tasks/Items**: title, completed flag, optional order, optional notes
- **Progress**: aggregate completion counts, per-checklist and global

## Architecture

### Decoupled SPA + API

- Django serves JSON only (DRF)
- React SPA deployed same-origin (nginx serves static; `/api/` proxies to Django)
- Session auth for simplicity (same-origin, CSRF token in header)
- No JWT; no Celery/Redis for MVP

### Tech choices

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Backend | Django 6 + DRF | Identity stack; `django-react-drf.md` patterns |
| DB | PostgreSQL | Identity stack |
| Frontend | React 19 + Vite | `vite-react-build.md`, `react-19-overview.md` |
| UI | Chakra UI 3 | `chakra-ui-3-overview.md`; compound components |
| Data | TanStack Query v5 | `tanstack-query.md`; server-state, mutations |
| Auth | Session + CSRF | Same-origin; `ensure_csrf_cookie()` on shell |
| Dev | Docker Compose | Postgres + Django + nginx; React dev server for HMR |

## Data model

### Checklist

- `id`, `title`, `created_at`, `updated_at`
- `user` (FK) — multi-user from day one; scope queryset by `request.user`

### ChecklistItem

- `id`, `checklist` (FK), `title`, `completed` (bool), `order` (int), `notes` (text, optional)
- `created_at`, `updated_at`

### Progress

- Derived: `completed_count` / `total_count` per checklist
- API: serializer annotations or computed fields; no extra table for MVP

## API surface

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/checklists/` | List user's checklists (ordered by `updated_at`) |
| POST | `/api/checklists/` | Create checklist |
| GET | `/api/checklists/{id}/` | Detail + items (nested or `?include=items`) |
| PATCH | `/api/checklists/{id}/` | Update title |
| DELETE | `/api/checklists/{id}/` | Delete checklist |
| GET | `/api/checklists/{id}/items/` | List items (ordered) |
| POST | `/api/checklists/{id}/items/` | Create item |
| PATCH | `/api/checklists/{id}/items/{item_id}/` | Toggle completed, update title/notes/order |
| DELETE | `/api/checklists/{id}/items/{item_id}/` | Delete item |

Pagination: `PageNumberPagination` (small lists). Cursor pagination only if lists grow large.

## Frontend structure

```
frontend/
├── src/
│   ├── main.tsx           # React root, QueryClient, Router, ChakraProvider
│   ├── App.tsx
│   ├── api/
│   │   ├── client.ts      # axios/fetch + CSRF, baseURL
│   │   ├── checklists.ts  # list, get, create, update, delete
│   │   └── items.ts       # list, create, update, delete
│   ├── hooks/
│   │   ├── useChecklists.ts
│   │   └── useChecklistItems.ts
│   ├── components/
│   │   ├── ChecklistCard.tsx
│   │   ├── ChecklistDetail.tsx
│   │   ├── TaskItem.tsx
│   │   └── ProgressBar.tsx
│   └── pages/
│       ├── ChecklistList.tsx
│       └── ChecklistDetail.tsx
├── package.json
└── vite.config.ts
```

TanStack Query keys: `['checklists']`, `['checklists', id]`, `['checklists', id, 'items']`.

## Implementation phases

### Phase 1 — Django scaffold

- `django-admin startproject checklist_project`
- `checklist` app: `Checklist`, `ChecklistItem` models
- User model: default `django.contrib.auth.User`
- DRF ViewSets, serializers, `get_queryset()` scoped to `request.user`
- Migrations, `manage.py runserver`
- CORS: `django-cors-headers` for dev (React on :5173, Django on :8000)

### Phase 2 — API

- Nested routers or flat `/checklists/{id}/items/` endpoints
- Pagination, filtering (optional: filter by `completed`)
- CSRF: `ensure_csrf_cookie` view for SPA shell
- Auth: login/logout views or DRF token for dev simplicity

### Phase 3 — React scaffold

- Vite + React + TypeScript
- Chakra UI 3 provider
- TanStack Query setup
- API client with credentials, `X-CSRFToken` header
- Router (TanStack Router or React Router)

### Phase 4 — UI

- Checklist list page
- Checklist detail with items
- Task toggle, add, edit, delete
- Progress display (X/Y completed)
- Responsive layout

### Phase 5 — Docker (optional)

- `docker-compose.yml`: postgres, web (Django), nginx
- React build served by nginx; `/api/` → gunicorn
- Same-origin for production

## Key references

- `knowledge/software-engineering/django/django-react-drf.md` — auth, CSRF, serializers
- `knowledge/software-engineering/django/django-production-stack.md` — service boundaries
- `knowledge/software-engineering/react/tanstack-query.md` — query keys, mutations
- `knowledge/software-engineering/react/chakra-ui-3-overview.md` — compound components
- `knowledge/software-engineering/devops/nginx-django-react.md` — nginx composition
