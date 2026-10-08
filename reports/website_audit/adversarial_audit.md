# JOBINTEL — ADVERSARIAL PRODUCT & PLATFORM AUDIT
**Senior QA • Principal Frontend • Product Design • ML Integrity • Adversarial Review**

---

## 1. Executive Summary

This adversarial product audit was conducted on the **JobIntel** market intelligence platform (`http://localhost:5173/`, backed by FastAPI at `http://127.0.0.1:8000/`) under an explicit **adversarial bug-hunt mandate**. Rather than assuming passing test suites (59/59 unit tests, 65/65 project gates) constitute proof of product correctness, the application was subjected to hostile browser automation, state corruption attacks, network failure simulation, mobile viewport stress testing, and line-by-line source-of-truth code inspection.

### Key Finding & Verdict
The audit revealed **18 verified product defects**, categorized as:
- **4 Critical (P0)** issues
- **6 High (P1)** issues
- **5 Medium (P2)** issues
- **3 Low (P3)** issues

**The most alarming finding is a severe Data & Scientific Integrity violation (BUG-P0-001 & BUG-P0-002)** on the Indian Skills Explorer page (`/skills`). Because the backend API (`/api/india/skills`) failed to supply empirical co-occurrence and salary association metrics, frontend code silently fabricated synthetic values:
1. Step-function formulas compute fake "Observed Medians" (14.5, 12.0, or 10.5 LPA) and fake salary deltas.
2. Clicking **any** skill (whether SAP, React, C++, or Java) displays the **exact same hardcoded roles** (*Backend Developer, Data Engineer, Software Engineer*), **exact same archetypes** (*Python, Cloud Data & Applied AI/ML; Full Stack & Enterprise Engineering*), and **exact same co-occurring skills** (*Java, SQL, AWS, Docker*).
3. On page load, the table claims Python has 644 postings and 12.1% prevalence, while the adjacent detail card claims 1,923 postings and 32.8% prevalence.

Furthermore, three of four summary KPI cards on the Explore Market page are hardcoded strings, exploratory filters fail to cross-filter distributions, the application lacks URL routing (refreshing resets to Home; back button breaks navigation), and prediction API errors cause silent failures resulting in a blank screen.

**Overall Product Health:** **RED**  
**Can the current application be trusted by a layman?** **NO**  
**Can the current application be demonstrated to an evaluator?** **NO**  
**Should production code be changed?** **YES**

---

## 2. Environment

| Component | Version / Environment | Target / URI | Status |
|---|---|---|---|
| **Frontend Runtime** | Vite 5.x + React 18 (TypeScript) | `http://localhost:5173/` | Running (dev server) |
| **Backend API** | FastAPI + Uvicorn + Python 3.12 | `http://127.0.0.1:8000/` | Running |
| **Active OS** | Microsoft Windows 11 Enterprise | Local Workstation | Validated |
| **Browser Engines** | Chromium Headless & Headful | Viewports: 1536×730, 1440×900, 375×812 | Audited |
| **USA Modeling Cohort** | 43,847 cleaned postings / 22,176 modeling | LightGBM / Ridge / HistGradient | Frozen |
| **India Modeling Cohort** | 16,921 postings / 5,321 salary cohort | HistGradientBoosting / Ridge | Frozen |

---

## 3. Browser Tests

Browser automation sessions (`adversarial_qa_audit` and `adversarial_india_mobile_audit`) executed automated multi-step journeys against the live application:

### Journey A: USA Market End-to-End Walkthrough
- **Flow**: Home → Calculator → Select USA → Role (ML/AI Engineer) → 5 Yrs Experience → San Francisco → Skills (Python, ML, AWS) → Remote → Result Screen.
- **Findings**:
  - Prediction calculated successfully: `$262,303 / yr`.
  - Confidence interval and holdout MAE ($34,850) displayed.
  - Archetype match: *Systems & Core Backend Engineering* (note: unexpected archetype assignment for ML skills, detailed in Section 7).
  - Evaluator Mode accordion opened and verified.

### Journey B: India Market End-to-End Walkthrough
- **Flow**: Home → Switch to India (₹ LPA) → Calculator → Software Engineer → 4 Yrs → Bengaluru → Skills (Python, Spark, SQL, AWS, Machine Learning) → Hybrid → Result Screen.
- **Findings**:
  - Prediction calculated successfully: `₹15.62 LPA` (≈ ₹1,561,605 / annum).
  - Indian tech hubs (Bengaluru, Delhi NCR, Mumbai, Hyderabad, Pune, Gurugram, Noida) loaded properly in Step 4.
  - Saffron/orange theming applied across most cards, but Info icon in "How should I read this?" remained hardcoded USA blue (`#38BDF8`).

### Journey C: Adversarial Stress & Edge Case Tests
1. **Zero-Skills Input**: Deselecting all skills in Step 5 and proceeding to calculate salary.
2. **Fast Country Switching**: Toggling country selector repeatedly during active wizard transitions.
3. **Hardcoded Strings Check**: Deep inspection of Explore Market and Skills Explorer DOM trees.
4. **Mobile Responsive Simulation**: Resizing viewport to 375×812 and inspecting element geometry.

---

## 4. Calculator Audit

### Step Flow Architecture
The Salary Calculator is structured as a 7-step wizard:
- Step 1: Country Selection (USA vs India)
- Step 2: Role Specialization
- Step 3: Experience Midpoint (Continuous Slider & Quick-Select Buttons)
- Step 4: Geographic Location (Metro Hubs)
- Step 5: Technical Skills (Multi-Select Taxonomy)
- Step 6: Work Mode (Remote, Hybrid, On-site)
- Step 7: Prediction Results & Evaluator Inspection

### Identified Bugs in Calculator
1. **BUG-P0-003**: In `PredictorPage.tsx` (`runPrediction()`), errors thrown during API calls are caught and logged via `console.error` without populating an error state. When `analyzing` completes, `result` is null, rendering `null` on line 1412. The user is stranded on a completely blank screen with no indication of failure or ability to retry.
2. **BUG-P1-005**: If zero skills are selected, the model returns `ZERO_SKILL` with `archetype_available: false`. The frontend ignores this boolean and presents a pink card stating: *"YOUR CLOSEST SKILL PATTERN: Archetype Unavailable (Zero Skills). Your selected skills resemble this recurring skill pattern..."* with an "Explore this archetype" button linking to `/archetypes`, where no such cluster exists.
3. **BUG-P2-001**: Progress header renders 7 dot indicators, while the card header at every step states "STEP 1 OF 6", "STEP 2 OF 6", ... "STEP 6 OF 6".
4. **BUG-P2-002**: Steps 1–4 provide no warning that skills are already pre-filled. Upon reaching Step 5, 3–4 default skills (Python, SQL, AWS, Spark) are already selected in component state, inflating initial salary estimates for unobservant users.
5. **BUG-P2-003**: The Info icon in the "How should I read this?" card on Step 7 hardcodes color `#38BDF8` (USA sky blue), failing to switch to Indian Saffron (`#F97316`).

---

## 5. API Audit

Inspection of backend routers (`src/backend/routers/`) and live HTTP contract verification:

| Endpoint | Method | Expected Contract | Actual Behavior | Integrity Status |
|---|---|---|---|---|
| `/api/usa/predict` | `POST` | Live inference on USA cohort | Returns `$262,303` with archetype object | Pass |
| `/api/india/predict` | `POST` | Live inference on India cohort | Returns `₹15.62 LPA` with archetype object | Pass |
| `/api/usa/options` | `GET` | Roles, cities, skills metadata | Returns full categorical choices | Pass |
| `/api/india/options` | `GET` | Categorical options & 284 skills | Returns 284 skills without category tags | Pass |
| `/api/india/market-summary` | `GET` | Macro market statistics & top skills | Returns 12 top skills with frequency only | Pass |
| `/api/india/skills` | `GET` | "Retrieve India technical skills with frequency, prevalence, and lifts" | Returns array of `{id, name, raw_key}` with zero stats | **FAIL (BUG-P1-006)** |
| `/api/cross-market/summary` | `GET` | Side-by-side macro comparison | Returns certified dual-market synthesis | Pass |

### Root Cause of API Disconnect
In `src/backend/routers/india.py` line 98:
```python
@router.get("/skills")
def get_india_skills():
    """Retrieve India technical skills with frequency, prevalence, and lifts."""
    try:
        options = IndiaService.get_options()
        return {
            "country": "India",
            "currency": "INR",
            "skills": options["skills"],
        }
```
The docstring explicitly promises frequency, prevalence, and lift metrics, but the function merely forwards the bare options array (`options['skills']`), completely lacking analytical metrics. This API shortfall directly provoked the frontend fabrication in `SkillsPage.tsx`.

---

## 6. Data Integrity Audit

### P0 Violation: Fabricated Metadata in India Skills Explorer
In `frontend/src/pages/SkillsPage.tsx` lines 86–98:
```typescript
const handleSelectSkill = async (skillName: string) => {
  setActiveSkill(skillName);
  if (isUSA) {
    ...
  } else {
    const found = indiaSkills.find((s) => s.skill.toLowerCase() === skillName.toLowerCase());
    const prev = found ? found.prevalence_pct : 15.0;
    setSkillDetail({
      skill: skillName,
      prevalence: prev,
      postings: found ? found.postings : 600,
      median_with_lpa: prev > 20 ? 14.0 : 11.5,
      delta_lpa: prev > 20 ? 4.0 : 1.5,
      roles: ['Backend Developer', 'Data Engineer', 'Software Engineer'],
      archetypes: ['Python, Cloud Data & Applied AI/ML', 'Full Stack & Enterprise Engineering'],
      combos: ['Java', 'SQL', 'AWS', 'Docker'],
    });
  }
};
```
Every single skill in the Indian dataset displays:
- **Identical Roles**: `Backend Developer`, `Data Engineer`, `Software Engineer`
- **Identical Archetypes**: `Python, Cloud Data & Applied AI/ML`, `Full Stack & Enterprise Engineering`
- **Identical Co-occurring Skills**: `Java`, `SQL`, `AWS`, `Docker`

This means that a user selecting **SAP** or **React** is told that the skill co-occurs with Docker and leads to Backend Engineering. This is completely false.

### P0 Violation: Formulated Salary Medians
In `frontend/src/pages/SkillsPage.tsx` lines 331–335:
```typescript
const prev = s.prevalence_pct;
const obsMed = prev > 20 ? 14.5 : prev > 10 ? 12.0 : 10.5;
const delta = obsMed - 10.0;
```
Empirical observed salaries are replaced by a crude step function based solely on prevalence, assigning every Indian skill an arbitrary median of 14.5, 12.0, or 10.5 LPA.

---

## 7. Prediction Integrity Audit

### Prediction Plausibility
- **USA Inference**: A Mid-level Software Engineer in SF with Python, ML, and AWS yields `$262,303`. While high, this falls within the upper 75th percentile of the SF tech market in the 2024–2026 corpus.
- **India Inference**: A 4-year Mid-level Software Engineer in Bengaluru with Python, Spark, SQL, AWS, and ML yields `₹15.62 LPA` (baseline 10.0 LPA + skills premium). This is realistic for Indian tier-1 product/consulting hubs.

### Archetype Mapping Glitch
When selecting ML skills for USA (Python, ML, AWS), the archetype assigned was `USA_ARC_6` (*Systems & Core Backend Engineering*). Inspection of PCA embeddings indicates that high overlap between C++/Linux backend skills and certain infrastructure tokens in the training set pulled the vector toward cluster 6. While mathematically defensible under frozen model weights, it represents a minor conceptual dissonance.

---

## 8. Archetype Audit

| Dimension | USA Market | India Market | Status |
|---|---|---|---|
| **Discovered Clusters** | 7 Archetypes (K-Means, PCA) | 6 Archetypes (K-Means, PCA) | Verified |
| **Cluster Isolation** | Full empirical centroids | Full empirical centroids | Verified |
| **Card Presentation** | Signature skills, postings, salary | Signature skills, postings, salary | Verified |
| **Detail Inspection View** | Sticky right sidebar | Sticky right sidebar | Verified |
| **Mobile Collapse** | Broken (forced 1.2fr:1fr) | Broken (forced 1.2fr:1fr) | **FAIL (BUG-P1-004)** |

---

## 9. Chart Audit

In `ExploreMarketPage.tsx`, interactive Recharts visualizations display:
1. **Salary Distribution by Role**
2. **Salary Progression by Experience Tier**
3. **Geographic Metro Compensation**
4. **Top 12 Market Skills**

### Filter Isolation Failure (BUG-P1-002)
Selecting a filter (e.g. Role = "Data Engineer") only filters the `Salary by Role` chart itself. The `Salary by Experience` and `Salary by Location` charts remain completely static, showing aggregate data for all roles combined. Users naturally expect dashboard filters to cross-filter across all analytical dimensions.

---

## 10. Navigation Audit

### Architectural Vulnerability: Zero URL Routing (BUG-P1-003)
The entire application routing in `App.tsx` is powered by:
```typescript
const [activePage, setActivePage] = useState<NavigationPage>('home');
```
Consequences:
1. **Refresh (F5)**: Forcibly navigates the user back to `'home'`, wiping wizard state and analytical context.
2. **Browser Back/Forward**: Fails completely; triggers browser navigation away from JobIntel to previously visited external domains.
3. **Deep Linking**: Impossible. A user cannot bookmark or share links to `/calculator`, `/explore`, `/skills`, or `/archetypes`.

---

## 11. State Management Audit

- **Market Isolation**: Managed cleanly via `MarketContext.tsx`. Toggling USA ↔ India triggers contextual re-renders and swaps data services.
- **Local Storage Persistence**: Active market preference is saved to `localStorage.getItem('jobintel_market')`.
- **Search State Leakage**: In `PredictorPage.tsx`, search input states (`roleSearch`, `citySearch`, `skillSearch`) persist when navigating back and forth across wizard steps. While not fatal, typing a role search query in Step 2 causes the query string to remain in memory when returning to Step 2 later.

---

## 12. Mobile Audit (Viewport: 375×812 iPhone / 412×915 Android)

1. **Header Navigation**: Collapses gracefully into a hamburger menu or scrollable bar.
2. **Explore Market Charts**: Recharts instances with `ResponsiveContainer width="100%"` render adequately, but chart legends wrap aggressively.
3. **Archetypes & Skills Dual-Column Collapse Failure (BUG-P1-004)**:
   - `gridTemplateColumns: '1.2fr 1fr'` forces both columns side-by-side into 375px screen width.
   - Each column is squeezed to ~175px, producing severe text overlap, clipped badges, and horizontal viewport overflow.

---

## 13. Desktop Audit (Viewport: 1440×900 & 1920×1080)

- Typography, glassmorphic atmospheric background, and spacing are visually appealing on high-resolution displays.
- Card padding and button hover states function smoothly.
- Zero horizontal layout shift (CLS) detected during standard desktop interaction.

---

## 14. Accessibility Audit (WCAG 2.1 AA)

1. **Semantic Controls (BUG-P3-002)**: In `PredictorPage.tsx`, selectable cards for Roles, Cities, and Work Modes are implemented as `<div>` elements with click handlers rather than accessible `<button>` or `<input type="radio">` controls.
2. **Keyboard Traversal**: Tab navigation cannot focus on role or location cards; pressing Space or Enter does not trigger selection.
3. **Contrast Ratios**: Primary accent `#38BDF8` (USA) and `#F97316` (India) provide > 4.5:1 contrast against dark background `#0B0D13`. Muted metadata (`#64748B`) occasionally dips below 3.5:1 on smaller 11px tags.

---

## 15. Console Audit

- **Clean Console on Normal Paths**: No uncaught React exceptions or React hydration warnings during standard navigation.
- **Error Swallowing**: During API rejection, `console.error('Prediction failed:', err)` logs silently without alerting the user interface.

---

## 16. Network Audit

- **Zero FX Isolation**: Verified. No requests make external currency conversion calls; USA and India endpoints run independently.
- **API Payloads**:
  - `POST /api/usa/predict`: Payload size ~350 bytes; response latency ~45ms.
  - `POST /api/india/predict`: Payload size ~320 bytes; response latency ~38ms.
- **Payload Validation**: Sending out-of-range experience (e.g. 99 years) properly triggers FastAPI Pydantic 422 Unprocessable Entity.

---

## 17. Scientific Language Audit

The platform generally maintains exemplary scientific language, using phrases such as:
- *"Observed compensation distributions"*
- *"Certified machine learning market models"*
- *"Holdout validation error (MAE)"*
- *"Strict Zero FX Isolation"*

However, **BUG-P1-005** contradicts this standard: when zero skills are provided, claiming that *"Your selected skills resemble this recurring skill pattern"* is scientifically untruthful.

---

## 18. Source-of-Truth Audit

Comparing UI assertions against the certified Phase 6 / Phase 7 registries:

| Metric Claimed in UI | Source Code Location | Certified Registry Ground Truth | Status |
|---|---|---|---|
| USA Median: `$180,413 / yr` | `ExploreMarketPage.tsx:119` | `$180,413.00` (Phase 6 registry) | Match |
| India Median: `₹10.0 LPA` | `ExploreMarketPage.tsx:120` | `₹10.00 LPA` (India cohort) | Match |
| USA Typical Exp: `Senior (5–8 yrs)` | `ExploreMarketPage.tsx:122` | Hardcoded string | **FAIL (BUG-P1-001)** |
| India Most Common Skill: `Python (32.8%)` | `ExploreMarketPage.tsx:123` | Ground truth: `Development (13.6%)`, `Java (12.5%)`, `Python (12.1%)` | **FAIL (BUG-P1-001)** |
| India Skills Observed Median | `SkillsPage.tsx:332` | Hardcoded step formula (14.5, 12.0, 10.5) | **FAIL (BUG-P0-002)** |

---

## 19. Hardcoded Data Audit

Line-by-line audit of hardcoded static data across frontend code:

1. `ExploreMarketPage.tsx:122`: `typicalExperience = isUSA ? 'Senior (5–8 yrs)' : '5.0 Years'`
2. `ExploreMarketPage.tsx:123`: `mostCommonSkill = isUSA ? 'Python (47.2%)' : 'Python (32.8%)'`
3. `ExploreMarketPage.tsx:124`: `largestRoleGroup = isUSA ? 'Software Engineer' : 'Full Stack Developer'`
4. `SkillsPage.tsx:52-61`: Hardcoded Python initial state (`prevalence: 32.8`, `postings: 1923`, `median_with_lpa: 14.5`)
5. `SkillsPage.tsx:86-98`: Hardcoded roles, archetypes, and co-occurring skills arrays for all India skills.
6. `SkillsPage.tsx:300`: Hardcoded fallback baseline salary `180413`.
7. `PredictorPage.tsx:1060`: Hardcoded blue color `#38BDF8` on India results.

---

## 20. Bug Matrix

The complete bug matrix has been generated at [`reports/website_audit/bug_matrix.csv`](file:///e:/Job%20Market/reports/website_audit/bug_matrix.csv). Below is the comprehensive catalog:

| Bug ID | Severity | Page | Category | Summary Description | Status |
|---|---|---|---|---|---|
| **BUG-P0-001** | **P0** | Skills Explorer | Data Integrity | Fabricated roles, archetypes, and co-occurring skills for all Indian skills | OPEN |
| **BUG-P0-002** | **P0** | Skills Explorer | Data Integrity | Fabricated step-function formulas for India observed median salaries & deltas | OPEN |
| **BUG-P0-003** | **P0** | Calculator | Error Handling | Silent failure & blank card when prediction API throws an error | OPEN |
| **BUG-P0-004** | **P0** | Skills Explorer | Data Integrity | Contradictory Python metrics on initial load (table says 12.1%; card says 32.8%) | OPEN |
| **BUG-P1-001** | **P1** | Explore Market | Hardcoded Data | Top summary KPI tiles (Experience, Top Skill, Top Role) are static strings | OPEN |
| **BUG-P1-002** | **P1** | Explore Market | Functional Filters | Filters only filter their own chart; do not cross-filter joint distributions | OPEN |
| **BUG-P1-003** | **P1** | Global Navigation | Routing | No URL routing; refresh resets to Home; Back button exits application | OPEN |
| **BUG-P1-004** | **P1** | Archetypes & Skills | Responsive | Forced dual columns (`1.2fr 1fr`) crush content on mobile screens < 768px | OPEN |
| **BUG-P1-005** | **P1** | Calculator | Data Integrity | Misleading archetype match copy and broken button when 0 skills selected | OPEN |
| **BUG-P1-006** | **P1** | Backend API | API Integrity | `/api/india/skills` docstring claims statistics but returns empty metadata | OPEN |
| **BUG-P2-001** | **P2** | Calculator | UX / Copy | Step numbering discrepancy: progress bar has 7 stages, card says "STEP X OF 6" | OPEN |
| **BUG-P2-002** | **P2** | Calculator | UX Defaults | Pre-selected default skills in Step 5 are invisible in prior steps and skew estimates | OPEN |
| **BUG-P2-003** | **P2** | Calculator | Theming | Hardcoded blue `#38BDF8` icon on India result card breaks color isolation | OPEN |
| **BUG-P2-004** | **P2** | Skills Explorer | Feature Parity | Category filter pills completely absent for India skills | OPEN |
| **BUG-P2-005** | **P2** | Skills Explorer | Code Quality | Fallback baseline constant ($180,413) hardcoded into USA delta formula | OPEN |
| **BUG-P3-001** | **P3** | Calculator | Typography | Minor floating-point rounding difference in annual LPA subtext | OPEN |
| **BUG-P3-002** | **P3** | Calculator | Accessibility | Selection cards implemented as non-semantic `<div>` elements without ARIA roles | OPEN |
| **BUG-P3-003** | **P3** | Skills Explorer | UX Edge Case | Missing empty-state message when search matches zero skills | OPEN |

---

## 21. Severity Summary

```
============================================================
JOBINTEL ADVERSARIAL AUDIT SEVERITY BREAKDOWN
============================================================
Critical P0:    4
High P1:        6
Medium P2:      5
Low P3:         3
False Alarms:   0
------------------------------------------------------------
TOTAL BUGS:     18
============================================================
```

---

## 22. Recommended Fix Order (Top 10 Priority Roadmap)

1. **FIX-1 (BUG-P0-001 & BUG-P1-006)**: Update backend `/api/india/skills` to compute and return true co-occurring skills, role associations, and archetype affinities from the India job corpus; remove hardcoded mock arrays from `SkillsPage.tsx`.
2. **FIX-2 (BUG-P0-002)**: Bind the India skills table directly to empirical median salaries and deltas from the backend rather than using the hardcoded ternary operator `prev > 20 ? 14.5 : 12.0`.
3. **FIX-3 (BUG-P0-004)**: Synchronize the initial Python skill detail state with real summary data (`postings: 644`, `prevalence: 12.1%`).
4. **FIX-4 (BUG-P0-003)**: Implement an explicit error state, alert banner, and "Retry Calculation" button in `PredictorPage.tsx` when prediction API calls fail.
5. **FIX-5 (BUG-P1-001)**: Bind Explore Market summary KPI cards (`typicalExperience`, `mostCommonSkill`, `largestRoleGroup`) to real dynamic metrics calculated by the backend summary endpoint.
6. **FIX-6 (BUG-P1-003)**: Introduce client-side hash routing (`/#/calculator`, `/#/explore`, `/#/skills`, `/#/archetypes`) with `window.addEventListener('hashchange')` so page state survives browser refresh and back/forward navigation.
7. **FIX-7 (BUG-P1-005)**: Guard the archetype result card in `PredictorPage.tsx` with `if (!result.archetype.archetype_available)` to display an informative zero-skill educational notice rather than claiming skills resemble an unassigned cluster.
8. **FIX-8 (BUG-P1-004)**: Add CSS media queries (`@media (max-width: 768px) { grid-template-columns: 1fr; }`) to `ArchetypesPage.tsx` and `SkillsPage.tsx`.
9. **FIX-9 (BUG-P1-002)**: Implement cross-filtering in `ExploreMarketPage.tsx` so selecting a role updates experience, location, and KPI metrics.
10. **FIX-10 (BUG-P2-002 & BUG-P2-001)**: Make default skills explicit in Calculator Step 5 with a "Clear all" button, and align step numbering to consistently reflect 6 input steps plus 1 result screen.

---

## 23. Final Verdict

The JobIntel application exhibits an elegant visual design, sophisticated atmospheric styling, and robust underlying machine learning models for its primary prediction workflows. However, **the application fails adversarial scrutiny due to critical scientific and data integrity lapses in secondary exploratory views**. Presenting fabricated formulas as empirical observations and repeating hardcoded skill associations directly undermines the project's credibility as a certified market intelligence system.

Production code **must be corrected** before demonstrating this platform to academic evaluators or releasing it to layman users.
