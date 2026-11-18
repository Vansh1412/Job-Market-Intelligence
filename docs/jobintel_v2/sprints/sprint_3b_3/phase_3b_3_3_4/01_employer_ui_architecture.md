# SPRINT 3B.3.3.4: EMPLOYER UI ARCHITECTURE & ROUTING INTEGRATION

**Date:** 2026-11-17  
**Working Branch:** `staging/sprint2c3`  
**Feature:** Dedicated Route `/employers` & Navigation Integration  
**Status:** **IMPLEMENTATION COMPLETE**

---

## 1. ROUTE DEFINITION & SPA INTEGRATION

To satisfy acceptance requirement **E01**, the employer intelligence experience is mounted at the dedicated route `/employers` in `frontend/src/App.tsx`.

### 1.1 Route Mapping & Bi-Directional Synchronization
In `frontend/src/App.tsx`, `ROUTE_MAP` and `PAGE_TO_ROUTE` were updated with the new `employers` navigation token:
```typescript
const ROUTE_MAP: Record<string, NavigationPage> = {
  '/': 'home',
  '/salary': 'calculator',
  '/calculator': 'calculator',
  '/explore': 'explore',
  '/skills': 'skills',
  '/archetypes': 'archetypes',
  '/cross-market': 'comparison',
  '/comparison': 'comparison',
  '/occupations': 'occupations',
  '/demand': 'demand',
  '/employers': 'employers',          // Dedicated primary route
  '/how-it-works': 'howitworks',
  '/howitworks': 'howitworks',
};

const PAGE_TO_ROUTE: Record<NavigationPage, string> = {
  home: '/',
  calculator: '/salary',
  explore: '/explore',
  skills: '/skills',
  archetypes: '/archetypes',
  comparison: '/cross-market',
  occupations: '/occupations',
  demand: '/demand',
  employers: '/employers',            // URL pushState sync
  howitworks: '/how-it-works',
};
```

### 1.2 Dynamic Component Mounting
Inside `renderActivePage()` in `App.tsx`:
```tsx
case 'demand':
  return <DemandPage />;
case 'employers':
  return <EmployersPage />;
case 'howitworks':
  return <MethodologyPage />;
```
When a user navigates to `/employers`, the application automatically activates the `employers` page state, mounts `<EmployersPage />`, and syncs browser history using HTML5 `pushState` and `popstate` listeners.

---

## 2. NAVIGATION HEADER INTEGRATION

To satisfy acceptance requirement **E02**, the navigation header (`frontend/src/components/AppHeader.tsx`) was updated with a primary link:
- **Navigation Identifier:** `'employers'`
- **Visual Label:** `Employer Intelligence`
- **Icon:** `Building2` from `lucide-react`
- **Responsive Behavior:** Displayed seamlessly in both desktop sticky header and mobile sliding drawer menu.

```typescript
export type NavigationPage =
  | 'home'
  | 'calculator'
  | 'explore'
  | 'skills'
  | 'archetypes'
  | 'comparison'
  | 'occupations'
  | 'demand'
  | 'employers'
  | 'howitworks';

const NAV_ITEMS = [
  ...
  { id: 'demand', label: 'Demand Intelligence', icon: TrendingUp },
  { id: 'employers', label: 'Employer Intelligence', icon: Building2 },
  { id: 'howitworks', label: 'How It Works', icon: BookOpen },
];
```

---

## 3. INFORMATION ARCHITECTURE & PAGE STRUCTURE

The `EmployersPage` (`frontend/src/pages/EmployersPage.tsx`) is architected into three specialized tabs:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        EMPLOYER INTELLIGENCE                          │
│     Header, Sovereign Jurisdiction Badges (IN, US, UK, AU, SG)        │
│     JOBINTEL Legal Identity Standard Principle Card                   │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         ▼                           ▼                           ▼
┌───────────────────┐       ┌───────────────────┐       ┌───────────────────┐
│ TAB 1: RESOLUTION │       │  TAB 2: REGISTRY  │       │ TAB 3: STANDARDS  │
│  - Candidate Form │       │  - Catalog List   │       │  - Sovereign Auth │
│  - Market Dropdown│       │  - HQ Filters     │       │  - ID Syntax Regex│
│  - Authority / ID │       │  - Pagination     │       │  - Collision Rules│
│  - Preset Buttons │       │  - Empty / Error  │       │  - Parent vs Sub  │
│  - Outcome Panel  │       │  - Profile Trigger│       │  - Zero Fabricat. │
│  - Candidate Table│       └───────────────────┘       └───────────────────┘
│  - Evidence Detail│
└───────────────────┘
```

### 3.1 Overview Section
- Prominent H1 title with styled icon container (`rgba(139, 92, 246, 0.25)`).
- Sovereign jurisdiction pills indicating authoritative statutory authorities:
  - 🇮🇳 India (MCA)
  - 🇺🇸 United States (SEC)
  - 🇬🇧 United Kingdom (Companies House)
  - 🇦🇺 Australia (ASIC)
  - 🇸🇬 Singapore (ACRA)
- Governance Standard Card establishing upfront that trading names and subsidiaries do not constitute identical legal identities.

### 3.2 Entity Resolution & Verification Panel
- Interactive form with real-time autofocus, field validation, and dynamic placeholder adaptation.
- 5 preset query buttons allowing one-click execution of verified corporate queries.
- Result card rendering distinct status banners (`AUTOMATICALLY_RESOLVED`, `MANUAL_REVIEW_REQUIRED`, `CONFIRMED_DISTINCT`).
- Multi-candidate evidence cards with normalized matching scores and explicit statistical disclaimers.

### 3.3 Employer Registry Explorer Panel
- Paginated table/card browser with headquarters jurisdiction filtering.
- Fully handled empty, loading, and error states with retry capabilities.
- Detail drawer modal displaying verified locations, official websites, and statutory source references.

### 3.4 Statutory Standards & Governance Panel
- Sovereign registers reference table outlining regulatory bodies, syntax requirements, and collision defense.
- Four core safety invariant disclosures: Duplicate collision defense, parent vs subsidiary preservation, similarity score honesty, and zero data fabrication.
