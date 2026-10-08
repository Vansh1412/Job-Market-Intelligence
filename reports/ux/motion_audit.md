# JOBINTEL — UX & MOTION AUDIT REPORT

**Audit Date**: October 8, 2026  
**Auditor**: Antigravity UX & Motion Systems  
**Product Standard**: Premium, Smooth, Fast, Calm, Intuitive, Professional Modern Analytics Product  
**Accessibility Target**: Full WCAG 2.1 AA Compliance including `prefers-reduced-motion: reduce`  

---

## 1. Executive Summary

A comprehensive audit was performed across all 7 views, layout headers, navigation bars, interactive forms, and data visualization canvases in JobIntel. 

Currently, `framer-motion` is installed in `package.json` (`^14.0.0`) but is **completely unused** in `frontend/src`. The interface relies on a patchwork of raw inline CSS transitions (`transition: 'all 0.2s ease'`) and three CSS background drift keyframes (`atmosphericDrift1..3`).

While the visual foundation (typography, palette, card styling) is high-quality, the user experience feels rigid and abrupt due to:
1. **Zero page transition choreography**: Switching between pages causes sudden visual replacement.
2. **Abrupt wizard steps**: The 7-step salary prediction wizard replaces inputs instantly without spatial direction awareness.
3. **No staggered entrances**: Landing hero, KPI metrics, and cards appear in an unchoreographed flash.
4. **Static result reveal**: The critical moment of truth (salary prediction) snaps into place without calm progressive disclosure.
5. **Missing accessibility**: Zero `prefers-reduced-motion` accommodations exist in CSS or JavaScript.

---

## 2. Motion Inventory & Defect Register

| Component / Surface | Current Motion Implementation | Duration | Trigger | Identified UX Problem | Recommended Action |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Global Page Transitions** (`App.tsx`) | None (instant React component swap) | 0ms | Tab / URL change | Abrupt page flashing; feels like a disjointed series of pages rather than a cohesive single-page application. | **MODIFY**: Implement lightweight Framer Motion `<AnimatePresence mode="wait">` transition: exit opacity $1 \rightarrow 0.96$, enter opacity $0 \rightarrow 1$ + `translateY` $6 \rightarrow 0$, duration 200–240ms. |
| **Landing Hero** (`HomePage.tsx`) | Static elements, inline CSS button hovers | 0ms / 200ms | Load / Hover | Entire hero arrives simultaneously; lacks modern product elegance. | **MODIFY**: Implement calm staggered entrance: eyebrow (0–150ms) $\rightarrow$ headline (100–350ms) $\rightarrow$ subtitle (200–450ms) $\rightarrow$ CTA (300–500ms) $\rightarrow$ preview visual (400–650ms). |
| **Hero Background** (`index.css`) | 3 keyframes (`atmosphericDrift1..3`) | 12s–20s | Infinite continuous | Effective, but can be softened with subtle radial breathing for a calm, premium depth. | **KEEP & REFINE**: Keep slow ambient drift; ensure GPU acceleration (`will-change: transform`). Suppress under reduced-motion. |
| **Primary CTAs** (`.ji-btn-primary`) | `transition: all 0.2s ease`, `translateY(-1px)` | 200ms | Hover / Active | Functional but slightly stiff; lacks subtle scale (1.015) and refined soft glow on hover. | **MODIFY**: Standardize micro-interaction: hover `translateY(-1.5px)` + scale `1.015`, active scale `0.985`, smooth cubic-bezier easing. |
| **Navigation Active State** (`Navbar.tsx`, `AppHeader.tsx`) | Instant background color switch | 0ms | Click | Tab indicator snaps abruptly without spatial continuity. | **MODIFY**: Add smooth layout indicator (`layoutId="nav-pill"`) so the active background pill glides between tabs. |
| **Macro KPI Cards** (`ExploreMarketPage.tsx`) | None (static arrival) | 0ms | Data load | All 4 metric cards appear instantaneously with zero hierarchy. | **MODIFY**: Add subtle staggered card entrance: opacity $0 \rightarrow 1$, `translateY` $8 \rightarrow 0$, staggered by 60ms per card. |
| **KPI Metric Numbers** (`ExploreMarketPage.tsx`) | Static text string | 0ms | Data load | Important numbers lack arrival polish; hardcoded numbers were fixed, but presentation is static. | **MODIFY**: Implement a subtle count-up / calm numerical fade when values first arrive. Suppress re-triggering on small rerenders. |
| **Chart Canvases** (`ExploreMarketPage.tsx`) | Default Recharts animation | Default | Canvas render | Recharts animates bars on mount, but filter changes cause harsh DOM replacement. | **MODIFY**: Wrap chart cards in calm crossfades; ensure Recharts bar growth duration is calibrated to 400–600ms with ease-out. |
| **Location Chart** (`ExploreMarketPage.tsx`) | None / Bar rendering | Default | Data load | Previously empty due to key mismatch; now verified with 8 bars, but needs smooth entrance animation. | **MODIFY**: Ensure bars grow smoothly from 0 with valid labels; maintain honest empty state if data is 0. |
| **Skills Explorer** (`SkillsPage.tsx`) | Row hover `0.12s ease`; static drawer | 120ms | Hover / Row click | Drawer details snap immediately into place; switching skills (Python $\rightarrow$ AWS) causes jarring text pop. | **MODIFY**: Wrap skill details drawer in `<motion.div>` with a 180ms crossfade/slide so switching skills feels fluid. |
| **Archetype Cards** (`ArchetypesPage.tsx`) | `.ji-card:hover` translateY(-2px) | 220ms | Hover / Select | Opening archetype details causes layout jump. | **MODIFY**: Animate card expansion and detail panel entrance with subtle stagger for skills list. |
| **Salary Wizard Steps** (`PredictorPage.tsx`) | Instant step swap (`step === 1 ? ... : ...`) | 0ms | Next / Back click | User lacks spatial perception of progress through the 7 steps. | **MODIFY**: Implement direction-aware slide transition: forward enters from +20px, backward enters from -20px, 220ms duration. |
| **Wizard Progress Indicator** (`PredictorPage.tsx`) | Static discrete dots | 0ms | Step change | Step indicator snaps between steps with zero interpolation. | **MODIFY**: Add smooth animated width transition to the progress track (`transition: width 0.3s cubic-bezier(...)`). |
| **Salary Result Reveal** (`PredictorPage.tsx`) | Loading spinner snaps to full result | 0ms | Prediction return | The most critical moment in the product is dumped on screen without narrative build. | **MODIFY**: Orchestrated reveal: "Analyzing your profile..." $\rightarrow$ card enters with subtle scale (0.98 $\rightarrow$ 1.0) $\rightarrow$ salary number reveals with count-up $\rightarrow$ supporting context fades in. Zero confetti / zero fireworks. |
| **Accessibility** (All pages) | Missing `prefers-reduced-motion` | N/A | OS preference | Violates WCAG 2.1 guideline 2.3.3. Users with motion sensitivities experience unwanted motion. | **CRITICAL ADDITION**: Full `prefers-reduced-motion` media query in CSS and React hook in motion tokens to instantly disable transitions. |

---

## 3. Motion System Design Tokens

To prevent scattered, arbitrary animation values, all transitions will adhere to a unified token system:

### Timing Constants
- **Fast (`motionFast`)**: `150ms` (tooltips, micro-hovers, tag selections)
- **Normal (`motionNormal`)**: `240ms` (page transitions, wizard steps, dropdowns, drawer reveals)
- **Slow (`motionSlow`)**: `400ms – 500ms` (chart bar entrance, hero sequence completion, modal reveal)

### Easing Curves
- **Entrance**: `cubic-bezier(0.16, 1, 0.3, 1)` (snappy ease-out, settles smoothly)
- **Transition**: `cubic-bezier(0.4, 0, 0.2, 1)` (balanced ease-in-out)
- **Ambient**: `linear` (continuous atmospheric drift only)

---

## 4. Next Implementation Steps

1. Create `frontend/src/utils/motionTokens.ts` defining centralized variants, timing, and reduced-motion utilities.
2. Add `@media (prefers-reduced-motion: reduce)` to `frontend/src/index.css`.
3. Wrap main tab rendering in `App.tsx` with `<AnimatePresence mode="wait">`.
4. Refine Hero entrance sequence in `HomePage.tsx`.
5. Implement direction-aware wizard transitions and orchestrated result reveal in `PredictorPage.tsx`.
6. Add smooth detail transitions to `SkillsPage.tsx` and `ArchetypesPage.tsx`.
7. Browser-test across desktop (1440×900) and mobile (390×844) viewports.
