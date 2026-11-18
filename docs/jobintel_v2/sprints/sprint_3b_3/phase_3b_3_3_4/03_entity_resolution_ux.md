# SPRINT 3B.3.3.4: ENTITY RESOLUTION SAFETY & UX PATTERNS

**Date:** 2026-11-17  
**Working Branch:** `staging/sprint2c3`  
**Feature:** Corporate Legal Entity Resolution UX & Governance Enforcement  
**Status:** **SAFETY INVARIANTS RIGOROUSLY ENFORCED**

---

## 1. LEGAL ENTITY INTEGRITY & RESOLUTION OUTCOMES

A central architectural mandate of JOBINTEL 2.0 is that **corporate brands, operating subsidiaries, and parent entities are legally distinct entities**. Naive search algorithms that group or collapse entities by common trading name or brand introduce serious legal identity misattribution vulnerabilities.

The `EmployersPage` implements clear visual states reflecting the exact decision engine of the backend:

```
                                  Resolution Request
                                           │
                                           ▼
                           ┌───────────────────────────────┐
                           │   Exact Statutory Match?      │
                           └───────┬───────────────┬───────┘
                                   │               │
                              YES  │               │ NO
                                   ▼               ▼
                   ┌───────────────────────┐   ┌───────────────────────┐
                   │ Collision or Conflict?│   │ Strong String Match?  │
                   └───────┬───────┬───────┘   └───────┬───────┬───────┘
                      NO   │       │ YES          YES  │       │ NO
                           ▼       ▼                   ▼       ▼
                     [State 1]   [State 2]           [State 3] [State 4]
                    AUTOMATIC    COLLISION/           MANUAL     NO MATCH
                    RESOLVED     MANUAL REVIEW        REVIEW    CONFIRMED
                                                                DISTINCT
```

---

## 2. DETAILED RESOLUTION STATES IN THE UI

### 2.1 State 1: Authoritative Automatic Match (`AUTOMATICALLY_RESOLVED`)
- **Backend Condition:** Exact statutory identifier verified in the authoritative sovereign registry, with compatible jurisdiction, and zero candidate name contradictions or collisions.
- **Visual Presentation:**
  - Status Banner: Emerald green badge (`#34D399`, `rgba(16, 185, 129, 0.15)`) with `CheckCircle2` icon.
  - Resolved Entity ID: Prominently displayed in emerald text.
  - Evidence Card: Confirms authoritative match with source link.
  - Human Approval Flag: Marked as `False` (safe for automated workflows).

### 2.2 State 2: Duplicate Identifier Collision Defense (`MANUAL_REVIEW_REQUIRED`)
- **Backend Condition:** A statutory identifier matches more than one distinct registered employer entity (e.g. corporate group sharing registration numbers across operating entities).
- **Governance Invariant:** The system **must fail closed**. It is strictly forbidden to choose an arbitrary primary candidate.
- **Visual Presentation:**
  - Status Banner: Amber yellow badge (`#FBBF24`, `rgba(245, 158, 11, 0.15)`) with `AlertTriangle` icon.
  - Resolved Entity ID: Explicitly displays `None (Unresolved)` in slate text. Never coerced to an arbitrary ID or zero.
  - Prominent Warning: *"Statutory identifier is duplicated across distinct registered employers. Automatic resolution prohibited; manual review required."*
  - Candidates List: All colliding candidates displayed with identical matching scores, allowing a human auditor to review differences in incorporation dates, jurisdictions, and legal suffixes.

### 2.3 State 3: Subsidiary vs Parent Symmetrical Distinction (`MANUAL_REVIEW_REQUIRED`)
- **Backend Condition:** Candidate name contains a subsidiary marker (e.g. "Google India Private Limited", "Amazon Australia Services Pty Ltd") matching a target with a shared brand.
- **Governance Invariant:** Symmetrical protection prevents collapsing domestic operating subsidiaries into foreign parent corporations.
- **Visual Presentation:**
  - Status Banner: Amber yellow badge (`MANUAL REVIEW REQUIRED`).
  - Resolved Entity ID: Preserved as `null` / `None (Unresolved)`.
  - Badges: `Shared Brand Detected` (amber) and `Subsidiary Distinction` (pink).
  - Evidence Summary: Explicitly discloses: *"Shared brand detected. Cross-market entity distinction: Subsidiary relationship indicated. Automatic collapsing prohibited by governance."*

### 2.4 State 4: Confirmed Distinct / No Match (`CONFIRMED_DISTINCT`)
- **Backend Condition:** Zero statutory matches and zero lexical candidates meeting the 70% threshold.
- **Visual Presentation:**
  - Status Banner: Slate badge (`#94A3B8`, `rgba(148, 163, 184, 0.15)`) with `XCircle` icon.
  - Resolved Entity ID: `None (Unresolved)`.
  - Informational Card: Clean message confirming that the queried entity does not match any registered employers and is confirmed distinct.

---

## 3. STATISTICAL TRANSPARENCY & DATA PRIVACY RULES

### Rule 1 — Matching Score vs Calibrated Probability
Whenever a similarity score is rendered (e.g. `98.5%`), it is labeled unambiguously:
```
Normalized Matching Score: 98.5%
(Lexical similarity score; not a calibrated probability.)
```
The UI strictly avoids claims such as *"99% probability of match"* or *"Guaranteed identity"*.

### Rule 2 — Suppression of Fabricated Workforce Metrics
In adherence to the JOBINTEL Prediction Realism Standard, the UI never fabricates employee headcounts, active vacancy numbers, recruitment velocity, or skill distributions. When an employer profile is viewed in the Detail Modal, an explicit disclosure card is rendered:
> **Data Publication Disclosure:** Workforce headcount, active vacancy counts, and hiring trends are not published for this legal entity. In accordance with JOBINTEL prediction realism standards, unsupported metrics are suppressed.

### Rule 3 — Data Leakage Prevention
Public error boundaries and response parsers suppress:
- Operating system file paths (e.g. `E:\Job Market\...`)
- Database connection strings or internal SQL traces
- Cloud container environmental variables
All errors are normalized into clean, user-facing error envelopes.
