---
source: agent-generated
type: research-plan
origin_session: chats/2026/03/18/chat-001
created: 2026-03-18
last_verified: 2026-03-18
trust: medium
status: active
next_action: "Begin Phase 2 — write knowledge/_unverified/react/tanstack-router.md"
---

# Research Plan: React Stack — Gaps and Depth

## Goals

Alex's frontend is React with Chakra UI 3, paired with a Django/DRF backend. The existing React knowledge base (4 files in `knowledge/_unverified/react/`) covers React 19 and Chakra UI 3 well, but has essentially no coverage of the practical infrastructure layer: data fetching, forms, routing, TypeScript patterns, testing, auth state, performance, or build tooling. All of that is what this plan addresses.

---

## Existing coverage (do not duplicate)

- `react-19-overview.md` — React 19 stable/19.2; Actions, `useActionState`, `useFormStatus`, `useOptimistic`, `use`, DOM metadata/asset APIs, API cleanup, upgrade path, TypeScript changes, `useEffectEvent`, `Activity`, partial pre-rendering
- `chakra-ui-3-overview.md` — Ark UI primitives, compound components, state machines, performance improvements, color-mode → `next-themes`, ecosystem trimming
- `chakra-ui-3-styling-system.md` — `defineConfig`/`createSystem`, tokens, semantic tokens, recipes, slot recipes, `colorPalette`, `textStyles`/`layerStyles`/`animationStyles`, responsive design, cascade layers, Chakra CLI
- `chakra-ui-3-react-frontend-patterns.md` — 10 patterns for high-quality frontends: token layering, recipe-driven primitives, `asChild` composition, focus rings, `layerStyles`/`textStyles`, SSR color mode caution, server/client boundary

---

## Research phases and priority order

### Phase 1 — Data and server state (highest priority) · ☑ 2/2 complete

The biggest gap. Alex's frontend talks to a DRF API; without TanStack Query, server state is ad hoc. Forms are also unavoidable in any CRUD app. These two files unlock the most day-to-day practical value.

1. ☑ `tanstack-query.md`
   - **Why**: the standard solution for DRF-backed React UIs; eliminates ad hoc fetch/loading/error/cache state
   - **Core model**: `QueryClient`, `QueryClientProvider`, `useQuery`, `useMutation`, query keys and key factories, stale-while-revalidate, background refetching
   - **Fetching patterns**: `queryFn` with axios/fetch, DRF pagination (cursor pagination + `keepPreviousData`), conditional queries (`enabled`), dependent queries
   - **Mutations and cache invalidation**: `useMutation` + `onSuccess` invalidation vs. optimistic updates with `setQueryData`, mutation side effects, rollback on error
   - **Optimistic UI**: `onMutate` / `onError` / `onSettled` pattern, ensuring rollback correctness
   - **Prefetching**: `prefetchQuery`, loader-based prefetch with TanStack Router (`ensureQueryData` in route loaders)
   - **Error and loading states**: `isLoading` vs. `isFetching` vs. `isPending`, global error handling, `useQueryErrorResetBoundary`
   - **`useInfiniteQuery`**: infinite scroll, `getNextPageParam`, `fetchNextPage`, integration with TanStack Virtual
   - **TanStack Query DevTools**: configuration, using in development
   - **Integration with React 19 Suspense**: `useSuspenseQuery`, `ErrorBoundary` + `Suspense` pairing
   - **DRF-specific patterns**: CSRF token in headers for mutations, session auth vs. JWT in query config, handling 401 with global interceptor

2. ☑ `react-hook-form-zod.md`
   - **Why**: de facto standard for performant uncontrolled React forms; zod is the natural TypeScript-first validator
   - **react-hook-form core**: `useForm`, `register`, `handleSubmit`, `formState` (`errors`, `isSubmitting`, `isDirty`, `isValid`), `watch`, `setValue`, `reset`
   - **Controller pattern**: `<Controller>` for controlled inputs and Chakra UI integration — required for Chakra's `Input`, `Select`, `Checkbox`, `RadioGroup`
   - **`useFormContext`** and `FormProvider`: multi-step forms and deeply nested field components without prop drilling
   - **`useFieldArray`**: dynamic lists of fields, add/remove/reorder
   - **Zod schemas**: `z.object`, `z.string`, `z.number`, `z.enum`, `.optional()`, `.nullable()`, `.refine()`, `.superRefine()`, `.transform()`, discriminated unions for conditional field groups
   - **`zodResolver`**: wiring zod to react-hook-form, inferring TypeScript types from schemas (`z.infer`)
   - **Async validation**: `validate` function for server-side checks, debounce pattern
   - **Form submission and DRF error mapping**: handling DRF field error responses (`{ field: ["error"] }`), setting server errors with `setError`
   - **Multi-step forms**: maintaining state across steps, validating per-step subschemas
   - **Chakra UI integration patterns**: `FormControl`, `FormLabel`, `FormErrorMessage` wired to `formState.errors`, focus management

---

### Phase 2 — Routing · ☐ 0/1 complete

3. ☐ `tanstack-router.md`
   - **Why TanStack Router**: fully type-safe routing end-to-end (route params, search params, loader data, navigation); file-based or code-based route tree; built-in search param state management superior to React Router's `useSearchParams`
   - **Route tree setup**: `createRootRoute`, `createRoute`, `createRouter`, `RouterProvider`; file-based routing with Vite plugin (`@tanstack/router-plugin`) vs. code-based
   - **Type safety model**: how TanStack Router infers types from the route tree; `Link` component is fully type-checked (no invalid `to` paths); `useParams`, `useSearch`, `useLoaderData` all return correctly typed values without casting
   - **Loaders**: `loader` function on route definition, `context` (injecting `QueryClient`), `loaderDeps` for search-param-dependent loaders, `staleTime` to avoid redundant fetches
   - **TanStack Query integration**: `routerContext` with `QueryClient`, `ensureQueryData` in loaders, query prefetching pattern — the natural pairing since both are TanStack projects
   - **Search params as first-class state**: `validateSearch` with zod, typed search param schemas, `useSearch`, `Link` search prop, `navigate({ search })` — far more ergonomic than React Router's string-based `useSearchParams`
   - **Nested routes and layouts**: layout routes, `Outlet`, index routes, `NotFoundRoute`
   - **Protected routes**: `beforeLoad` for auth guards, redirecting with `redirect()`, storing `from` location for post-login redirect
   - **Navigation**: `Link`, `useNavigate`, `navigate()`, `replace` vs. `push`, `useRouter` for imperative access
   - **Pending UI and transitions**: `pendingComponent`, `pendingMs`, `pendingMinMs`, `useRouterState` for transition state
   - **Error handling**: `errorComponent` on routes, `useRouteContext`, integration with `react-error-boundary`
   - **Code splitting**: `lazyRouteComponent`, `lazy()` with route-level splitting, `Suspense` boundaries
   - **Devtools**: `TanStackRouterDevtools`

---

### Phase 3 — TypeScript patterns · ☐ 0/1 complete

4. ☐ `typescript-react-patterns.md`
   - **Component prop typing**: `React.FC` vs. plain function (prefer plain), `ReactNode` vs. `ReactElement`, `PropsWithChildren`, `ComponentPropsWithoutRef` / `ComponentPropsWithRef` for extending native element props
   - **Generic components**: generic list components, generic form field wrappers, variance constraints (`T extends object`, `T extends { id: string }`)
   - **Discriminated union props**: `type` discriminant for variant components, TypeScript narrowing in render, exhaustive checks with `never`
   - **Type-safe context**: context with a sentinel default, `createContext<T | null>(null)` + assertion hook pattern, typed dispatch with `useReducer`
   - **Type-safe API layer**: inferring types from zod schemas, sharing schema types between form validation and API response parsing, `z.infer` pattern, `satisfies` for API response objects
   - **Ref typing**: `useRef<HTMLInputElement>(null)`, `forwardRef<HTMLDivElement, Props>`, `useImperativeHandle`, React 19 ref-as-prop pattern
   - **Event handler typing**: `React.ChangeEvent`, `React.MouseEvent`, `React.FormEvent`, `React.KeyboardEvent` with correct generic
   - **Utility types in practice**: `Partial`, `Required`, `Pick`, `Omit`, `Readonly`, `Parameters`, `ReturnType` applied to common React patterns
   - **`satisfies` operator**: runtime type narrowing without widening, enum-like objects
   - **Module augmentation**: extending Chakra's theme types, extending third-party types

---

### Phase 4 — Testing · ☐ 0/1 complete

5. ☐ `vitest-rtl-msw.md`
   - **Vitest**: `describe`, `it`, `expect`, `beforeEach`/`afterEach`, `vi.fn()`, `vi.spyOn()`, `vi.mock()`, `vi.useFakeTimers()`, `--coverage` with v8/istanbul, `--reporter`, config in `vite.config.ts`
   - **React Testing Library**: `render`, `screen`, `userEvent` (prefer over `fireEvent`), query priority (`getByRole` > `getByLabelText` > `getByText` > `getByTestId`), `waitFor`, `findBy*` async queries, `within`
   - **Testing Chakra UI components**: common pitfalls with portals (modals, menus), `ChakraProvider` in test setup, `@testing-library/user-event` for keyboard and click interactions
   - **Mock Service Worker (MSW)**: `setupServer`, `http.get`/`http.post`/`http.put`/`http.delete`, `HttpResponse`, `server.use()` for per-test overrides, MSW v2 API (request/response handlers), global setup in `vitest.setup.ts`
   - **Testing TanStack Query**: `QueryClientProvider` with test `QueryClient` (`retries: false`), `renderHook`, resetting query cache between tests
   - **Testing react-hook-form**: `userEvent` for form interactions, triggering validation, testing submit behavior
   - **Testing routing**: TanStack Router's `createMemoryHistory` + `createRouter` for unit tests, route param and search param testing, mocking `loader` context
   - **Component interaction testing**: testing modal open/close, testing async loading states with MSW, testing error states
   - **Snapshot testing discipline**: when snapshots help vs. when they become maintenance burden

---

### Phase 5 — Auth state and protected routes · ☐ 0/1 complete

6. ☐ `react-auth-patterns.md`
   - **Token storage**: httpOnly cookie (set by DRF, no JS access, CSRF-protected, recommended) vs. localStorage (accessible to JS, XSS risk) vs. memory (safest but lost on refresh); practical recommendation for a DRF backend
   - **Auth state management**: global auth context (`user`, `isAuthenticated`, `isLoading`), initializing from `/api/me/` on app mount, TanStack Query for auth state (`useQuery` on the current user endpoint)
   - **JWT in React**: storing refresh tokens vs. access tokens, silent refresh pattern with axios interceptors, token expiry handling, `axios-auth-refresh`
   - **Protected route patterns**: TanStack Router `beforeLoad` redirect, higher-order `<RequireAuth>` wrapper, role-based route guards
   - **Login/logout flows**: redirecting after login (`from` location state), clearing query cache on logout (`queryClient.clear()`), broadcast channel logout across tabs
   - **OAuth / social login**: redirect flow vs. popup, handling the callback page in a SPA, integrating with `django-allauth` headless mode
   - **CSRF in practice**: DRF's session auth + CSRF: reading `csrftoken` cookie, setting `X-CSRFToken` header in axios defaults, `axios.defaults.withCredentials = true` for cross-origin
   - **Auth error handling**: global 401 interceptor pattern with axios, query error propagation to a login redirect

---

### Phase 6 — Performance · ☐ 0/1 complete

7. ☐ `react-performance.md`
   - **The memo discipline question**: when `React.memo` actually helps (stable props, expensive renders), when it doesn't (props change every render anyway), the cost of memo itself
   - **`useMemo` and `useCallback` discipline**: correct mental model (referential stability, not computation cost avoidance), common over-memoization anti-patterns
   - **React 19 compiler** (React Forget): what it does, current status (opt-in, shipped in React 19), how it changes the `useMemo`/`useCallback` calculus
   - **`useEffectEvent`** (React 19.2): solving the stale-closure-in-effect problem without over-widening effect dependencies
   - **Virtualization**: TanStack Virtual (`useVirtualizer`), row virtualization, dynamic row heights, windowing for large tables and lists
   - **Code splitting**: `React.lazy` + `Suspense`, route-level splitting with TanStack Router's `lazyRouteComponent`, component-level splitting for heavy modals/editors, `import()` for conditional loads
   - **Bundle analysis**: `rollup-plugin-visualizer` / `vite-bundle-analyzer`, identifying large dependencies, tree-shaking failures, dynamic import wins
   - **Image optimization**: lazy-loading with `loading="lazy"`, `<picture>` / `srcset`, next-gen formats, avoiding layout shift (explicit width/height)
   - **React DevTools Profiler**: flame graph, ranked chart, "why did this render?", React 19 Performance Tracks in Chrome DevTools
   - **Concurrency and Suspense**: `useTransition` for non-urgent updates (avoiding blocking the UI during slow renders), `useDeferredValue` for keeping inputs responsive during expensive child renders

---

### Phase 7 — Build tooling · ☐ 0/1 complete

8. ☐ `vite-react-build.md`
   - **Vite for React**: `@vitejs/plugin-react` (Babel + SWC options), `@vitejs/plugin-react-swc` for faster builds, environment variables (`import.meta.env`, `.env` files, `VITE_` prefix)
   - **Dev server**: `proxy` config for DRF API (avoids CORS in development), HMR, `server.port`, `server.https`
   - **Build optimization**: `build.target`, `build.rollupOptions`, manual chunks for vendor splitting, `assetsInlineLimit`, `sourcemap` options
   - **Path aliases**: `resolve.alias` with `@/` for clean imports, TypeScript `paths` config alignment
   - **Code splitting strategy**: when to use manual chunks vs. dynamic imports vs. route-level splitting, the `rollupOptions.output.manualChunks` API
   - **Bundle analysis and size budgets**: `rollup-plugin-visualizer`, size-limit integration in CI
   - **Environment-specific configuration**: `vite.config.ts` with `mode`, `loadEnv`, different API base URLs per environment
   - **PWA and service worker**: `vite-plugin-pwa` for offline support, caching strategies
   - **Testing integration**: Vitest config sharing `vite.config.ts`, browser mode vs. jsdom mode
   - **Docker integration**: multi-stage Dockerfile for React (node build stage → nginx serve stage), `nginx.conf` for SPA fallback (`try_files $uri /index.html`)

---

### Phase 8 — Error handling and Suspense · ☐ 0/1 complete

9. ☐ `react-error-boundaries-suspense.md`
   - **Error boundaries**: class component requirement, placement strategy (per-page vs. per-feature vs. per-data-region), `getDerivedStateFromError` vs. `componentDidCatch`, `react-error-boundary` library (`ErrorBoundary`, `useErrorBoundary`, `withErrorBoundary`)
   - **React 19 error handling changes**: `onUncaughtError` / `onCaughtError` on `createRoot`, errors no longer rethrown the same way, implications for Sentry integration
   - **Suspense boundaries**: placement strategy (granular vs. coarse), skeleton screens vs. spinner vs. content placeholders, avoiding layout shift during loading
   - **Suspense + TanStack Query**: `useSuspenseQuery`, `useSuspenseInfiniteQuery`, nesting Suspense + ErrorBoundary correctly
   - **Deferred / streaming data**: TanStack Router's `defer()` in loaders, `Await` component, error handling for deferred rejections
   - **`useTransition` and non-urgent Suspense**: keeping the old UI visible during navigation (no accidental loading flash), `startTransition` wrapping navigations
   - **Error monitoring integration**: Sentry `ErrorBoundary`, `captureException` in catch blocks, correlation with backend Sentry tracing (shared `traceId`)
   - **User-facing error UX**: retry buttons, partial failure states, toast notifications vs. inline errors vs. full-page errors

---

## Progress log

| Date | Action |
|---|---|
| 2026-03-18 | Plan created; existing 4 React files reviewed and gaps identified |
| 2026-03-18 | Wrote `knowledge/_unverified/react/tanstack-query.md`; covers v5 API, query keys, useQuery, useMutation, optimistic updates, DRF patterns, useInfiniteQuery, useSuspenseQuery, useQueries |
| 2026-03-18 | Wrote `knowledge/_unverified/react/react-hook-form-zod.md`; covers RHF v7 + zod v3, Controller/Chakra integration, useFieldArray, multi-step forms, DRF error mapping; Phase 1 complete |

---

## Notes

- **Stack context**: Alex's React frontends talk to DRF APIs. TanStack Query and react-hook-form are the most load-bearing gaps; they should be researched first.
- **Chakra integration**: Several files (forms, performance, error handling) should include specific Chakra UI 3 integration notes where relevant.
- **TanStack Router vs. Next.js**: Alex's stack is a standalone React SPA + Django backend, not Next.js. Files should avoid framework-mode Next.js assumptions. TanStack Router is chosen over React Router for its end-to-end type safety and first-class search param schema support.
- **File count**: 9 files planned. All go to `knowledge/_unverified/react/`.
