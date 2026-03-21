---
source: agent-generated
origin_session: manual
created: 2026-03-21
type: build-plan
category: build
status: active
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
| UI | Chakra UI 3 | `chakra-ui-3-overview.md`; compound components, Ark UI |
| Data | TanStack Query v5 | `tanstack-query.md`; server-state, mutations |
| Auth | Session + CSRF | Same-origin; `ensure_csrf_cookie()` on shell |
| Dev | Docker Compose | Postgres + Django; React dev server on host (Vite proxy avoids CORS) |

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
| GET | `/api/me/` | Current user (for auth state; see `react-auth-patterns.md`) |
| POST | `/api/auth/login/` | Login (Django session) |
| POST | `/api/auth/logout/` | Logout |
| GET | `/api/checklists/` | List user's checklists (ordered by `updated_at`) |
| POST | `/api/checklists/` | Create checklist |
| GET | `/api/checklists/{id}/` | Detail + items (nested or `?include=items`) |
| PATCH | `/api/checklists/{id}/` | Update title |
| DELETE | `/api/checklists/{id}/` | Delete checklist |
| GET | `/api/checklists/{id}/items/` | List items (ordered) |
| POST | `/api/checklists/{id}/items/` | Create item |
| PATCH | `/api/checklists/{id}/items/{item_id}/` | Toggle completed, update title/notes/order |
| DELETE | `/api/checklists/{id}/items/{item_id}/` | Delete item |

- Pagination: `PageNumberPagination` (small lists). Cursor pagination only if lists grow large.
- DRF: separate read/write serializers; `get_queryset()` scoped to `request.user`; override exception handler for stable error envelope (`{ field: [...], non_field_errors: [...] }`).

## Frontend structure

```
frontend/
├── src/
│   ├── main.tsx           # React root, QueryClient, Router, ChakraProvider
│   ├── App.tsx
│   ├── api/
│   │   ├── client.ts      # axios with withCredentials, X-CSRFToken, 401 interceptor
│   │   ├── checklists.ts
│   │   └── items.ts
│   ├── hooks/
│   │   ├── useCurrentUser.ts   # useQuery(['me']); invalidate on login, clear on logout
│   │   ├── useChecklists.ts
│   │   └── useChecklistItems.ts
│   ├── contexts/
│   │   └── AuthContext.tsx     # thin wrapper over useCurrentUser
│   ├── components/
│   │   ├── ChecklistCard.tsx   # Chakra 3: Card.Root, Card.Header, etc.
│   │   ├── ChecklistDetail.tsx
│   │   ├── TaskItem.tsx        # optimistic toggle via useMutation
│   │   └── ProgressBar.tsx
│   └── pages/
│       ├── Login.tsx
│       ├── ChecklistList.tsx
│       └── ChecklistDetail.tsx
├── .env                    # VITE_API_URL (dev: /api; Vite proxies to Django)
├── package.json
└── vite.config.ts          # proxy /api → localhost:8000 (avoids CORS in dev)
```

- **Query keys** (factory pattern per `tanstack-query.md`): `checklistKeys.all`, `checklistKeys.detail(id)`, `checklistKeys.items(id)` — enables targeted invalidation.
- **API client**: `withCredentials: true`; read `csrftoken` from cookie for `X-CSRFToken`; 401 → `queryClient.clear()` + redirect to login.
- **DRF errors**: `onError` in mutations maps `{ field: ["msg"] }` to `form.setError(field, ...)` (see `react-hook-form-zod.md`).
- **Optimistic toggle**: `onMutate` snapshot → `setQueryData` → rollback in `onError`; `onSettled` invalidate.
- **TanStack Query v5**: use `isPending` (not `isLoading`), `gcTime` (not `cacheTime`).

## Dev workflow

- Django in Docker (postgres + web) or native; React on host: `npm run dev` → Vite :5173.
- Vite proxy `/api` → Django :8000 → no CORS in dev; `VITE_API_URL` can stay `/api` (relative).
- `.env.example` committed; `.env` gitignored.
- Node 20.x for Chakra 3.

## Implementation phases

### Phase 1 — Django scaffold

- `django-admin startproject checklist_project`
- `checklist` app: `Checklist`, `ChecklistItem` models
- DRF ViewSets with separate read/write serializers; `get_queryset()` scoped to `request.user`
- Migrations, `manage.py runserver`
- `ensure_csrf_cookie()` view for SPA shell; Django login/logout views (or `django.contrib.auth.views`)
- Optional: `drf-spectacular` for OpenAPI (`drf-spectacular.md`)

### Phase 2 — API

- Flat `/checklists/{id}/items/` endpoints (IDs over nested writes)
- Override DRF exception handler for stable error envelope
- `select_related`/`prefetch_related` on checklist detail for items
- Pagination, optional `DjangoFilterBackend` for `completed` filter
- `/api/me/` endpoint for auth state

### Phase 3 — React scaffold

- Vite + React + TypeScript; `@vitejs/plugin-react-swc`; path alias `@/`
- Vite proxy: `/api` → `http://localhost:8000` (avoids CORS in dev; `vite-react-build.md`)
- Chakra UI 3: `createSystem`, compound components; `react-icons` or `lucide-react` (no `@chakra-ui/icons`)
- TanStack Query: `staleTime`, `gcTime`; `ReactQueryDevtools`
- API client: axios + CSRF + 401 interceptor
- Router with protected-route `beforeLoad` (redirect unauthenticated to `/login`)

### Phase 4 — UI

- Checklist list; checklist detail with items
- Task toggle with optimistic update; add, edit, delete
- Progress display; responsive layout
- Login page; post-login redirect via `?from=` param

### Phase 5 — Docker (optional)

- `docker-compose.yml`: postgres (healthcheck), web (Django); `depends_on: condition: service_healthy`
- React dev server on host (not in container) for HMR; Vite proxies to Dockerized Django
- Production: nginx serves React build; `/api/` → gunicorn; same-origin

## Key references

| File | Use |
|------|-----|
| `django/django-react-drf.md` | Auth, CSRF, serializers, error envelope, pagination |
| `django/django-production-stack.md` | Service boundaries, startup order |
| `django/drf-spectacular.md` | OpenAPI schema (optional) |
| `react/tanstack-query.md` | Query keys, mutations, optimistic updates, DRF pagination |
| `react/chakra-ui-3-overview.md` | Compound components, Ark UI, `react-icons` |
| `react/react-auth-patterns.md` | useCurrentUser, protected routes, login/logout flow |
| `react/react-hook-form-zod.md` | DRF error mapping to `setError` |
| `react/vite-react-build.md` | Dev proxy, env vars, path aliases |
| `devops/nginx-django-react.md` | Production nginx composition |
| `devops/docker-compose-local-dev.md` | Healthchecks, React on host, `.env.example` |
