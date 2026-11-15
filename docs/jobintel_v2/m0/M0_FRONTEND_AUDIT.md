# M0 Frontend Audit

## Entry points and routing

**VERIFIED FROM SOURCE CODE:** `frontend/src/main.tsx` mounts `App` in `StrictMode`; `App.tsx` wraps `AppContent` in `MarketProvider`. Routing is hand-written with `ROUTE_MAP`, `PAGE_TO_ROUTE`, `history.pushState`, `popstate`, and `hashchange`, not a router library. Unknown locations resolve to home and are rewritten to `/` on initialization.

| Public path | Page | Purpose / calls |
|---|---|---|
| `/` | `HomePage` | Product overview; navigation to other sections; APIs are not evidenced as direct calls from its source beyond app navigation |
| `/salary` | `PredictorPage` | Guided salary estimator; market options and market-specific prediction POST |
| `/calculator` | `PredictorPage` | Alias of `/salary` |
| `/explore` | `ExploreMarketPage` | Filterable market salary summaries for USA or India |
| `/skills` | `SkillsPage` | USA skill landscape/detail or India skill analytics/detail |
| `/archetypes` | `ArchetypesPage` | Market archetype list |
| `/cross-market` | `CrossMarketPage` | USA/India comparative summary |
| `/comparison` | `CrossMarketPage` | Alias of `/cross-market` |
| `/how-it-works` | `MethodologyPage` | Methodology, limitations, leakage controls, pipeline stages |
| `/howitworks` | `MethodologyPage` | Alias of `/how-it-works` |

## Architecture and dependencies

- Market state: React Context in `context/MarketContext.tsx`; localStorage key `jobintel_market`, default USA; supported types only `USA | India`.
- API: `services/api.ts` wraps `fetch`, reads build-time `VITE_API_BASE_URL`, defaults to `/api`, throws an Error for non-2xx response, parses JSON. There is one API module but it also exposes legacy analytics endpoints.
- Types: `types.ts`; broad use of `any` remains for several API payloads and metadata. Market union explicitly excludes new markets.
- Styling: global CSS (`index.css`, `App.css`) plus inline styles and component-local style objects; no Tailwind setup or Tailwind dependency was found. Current product styling is not the Tailwind stack described in the initial project hypothesis.
- Charts: Recharts; animation: Framer Motion; icons: Lucide React. No 3D dependency found.
- Tests/build: Vitest, React Testing Library, jsdom; TypeScript project build via `tsc -b`, Vite; Oxlint. Test baseline is in `M0_TEST_BASELINE.md`.
- Shared UI: `AppHeader`, `MarketSwitcher`, `PageHero`, `AtmosphericBackground`, `ScientificDisclaimer`, `SourceFooter`; pages under `pages/`.

## Route-level implementation and states

`PredictorPage`, `ExploreMarketPage`, `SkillsPage`, and `ArchetypesPage` have asynchronous fetches and component state. The source includes loading/error/result handling in some flows, but the repository audit did not render every state in a live browser. A route-by-route visual/mobile/accessibility pass is therefore **NOT VERIFIED**. No claim that a page is broken is made. `HomePage`, `CrossMarketPage`, and `MethodologyPage` are distinct components; there is no evidence of duplicate page components. Alias routes intentionally map to the same view.

## Findings to carry forward

- **INFERRED:** custom History API navigation and Vercel catch-all rewrites are compatible for direct links, but route behavior should remain covered by tests; browser refresh behavior was not live-verified.
- **VERIFIED FROM SOURCE CODE:** error mapping is generic (`API error (status): response text`); API types are partly permissive (`any`); market context persists selection only in localStorage.
- **NOT VERIFIED:** keyboard behavior, screen-reader semantics, contrast, mobile layout at representative widths, and actual empty-state completeness were not browser-tested during M0.
- No unused component or duplicated API helper was declared based on static name matching alone. Oxlint reports unused imports/locals and hook dependency warnings; see baseline.

## Files inspected

`frontend/src/App.tsx`, `main.tsx`, all files under `components/`, `context/`, `pages/`, `services/`, `types.ts`, `utils/`, CSS, tests, `package.json`, Vite/Vitest/TypeScript/Oxlint config, and Vercel config.

## Route implementation matrix

This fills the route-level state/interaction inventory from static source. Visual responsiveness and accessibility remain **NOT VERIFIED** without a rendered browser audit.

| Route | State/API | Visualization / interaction | Loading, error, empty | Mobile / accessibility | Status |
|---|---|---|---|---|---|
| `/` | Local navigation state; no page data fetch found | Product cards and CTA buttons; navigates to salary, explore, skills, archetypes, methodology, comparison | No request loading/error; content is static | Responsive CSS is present in app styles; no browser/device verification. Buttons used; full keyboard/semantic review not run | Implemented; browser behavior not verified |
| `/salary`, `/calculator` | Local form/result state; market context; market options + prediction POST | Search/select role, seniority or India experience, city, skills, work-mode/remote; submits prediction; displays result and distribution context | Options loading state; catches option/prediction errors (console logging in source). No live API failure visual inspection. | Extensive button controls; mobile not rendered. Label/keyboard/readout semantics need browser audit | Implemented for India/USA |
| `/explore` | Selected market/filters; market-summary API | Role/experience-or-seniority/location/skill filters, reset; Recharts bar visuals; empty combination message observed (“No sufficient postings…”) | Loading state; fetch catch/log; empty-filter state exists. User-visible error state not established by static review | `ResponsiveContainer` charts; mobile layout not live-verified; chart accessibility not evaluated | Implemented for India/USA |
| `/skills` | Market context; USA landscape/detail and India skills/detail APIs; search/category/selection | Search, category buttons, skill detail; chart-like skill and cooccurrence summaries | Loading state; fetch/detail errors logged; explicit empty messages for no prominent clusters/no recurring pairs | No browser verification. Clickable skills and controls require keyboard/name review | Implemented for India/USA |
| `/archetypes` | Market context; USA/India archetype list APIs; selected archetype state | Select archetype; toggle technical explanation; profile visualizations | Loading state; fetch errors logged; user-visible error/empty handling not confirmed | No browser/mobile/a11y run | Implemented for India/USA |
| `/cross-market`, `/comparison` | Cross-market summary API; local data/error/loading state | Recharts comparison bars | Explicit loading; error or no-data message on failure | Responsive chart container; no live mobile/a11y run | USA/India only |
| `/how-it-works`, `/howitworks` | Static methodology content; toggle state | Expand/collapse methodology sections | No API loading/error/empty states | Buttons exist; no live keyboard/a11y check | Implemented, static |

Global header has desktop/mobile navigation, `aria-label`, `aria-expanded`, `aria-controls` on mobile-menu toggle, and labeled mobile navigation region. This is source evidence of some accessibility provisions, not conformance certification. The API client throws on non-2xx and attaches response text; error-message design and retry behavior have not been tested in browser. `App.tsx` aliases routes manually; direct-link/reload behavior is covered by routing tests in source, although Vitest execution could not start workers in this environment.
