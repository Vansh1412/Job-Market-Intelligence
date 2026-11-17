# JOBINTEL 2.0 — PREDICTION DISPLAY STANDARD
## Product-Wide User Interface Standards, Disclosure Patterns & Semantic Integrity

**Sprint:** 3B.3.2.2 — Global Prediction Reliability, Calibration & Claims Audit  
**Auditor Role:** Senior ML Reliability Engineer, Principal Frontend Architect  
**Standard Reference:** `JOBINTEL-STD-PRED-001`  

---

## 1. THE 7-ELEMENT PREDICTION DISPLAY CARD STANDARD

Where appropriate, any predictive or statistical insight card rendered across the JOBINTEL web application must be designed around seven standardized information layers:

```
+----------------------------------------------------------------------------------------------------+
| THE 7-ELEMENT PREDICTION DISPLAY PATTERN                                                           |
+----+-----------------------+----------------------------------+------------------------------------+
| #  | Element Name          | Information Rendered             | Example (Salary Intelligence)      |
+----+-----------------------+----------------------------------+------------------------------------+
| 1  | Estimated Result      | Central benchmark value (rounded)| ₹12.5 LPA (or $142,000 / year)     |
| 2  | Uncertainty Range     | Empirical residual interval      | Range: ₹10.4 – 14.6 LPA (P25–P75)  |
| 3  | Evidence Quality Tier | Qualitative confidence indicator | High Confidence (Verified Pattern) |
| 4  | Evaluation Quality    | Validated out-of-sample accuracy | Model R2 = 0.58 on holdout cohort  |
| 5  | Data Freshness        | Effective reference timestamp    | Based on FY2024–2025 Disclosures   |
| 6  | Supporting Source     | Originating statutory/ATS source | Source: SEC 10-K / WGEA / Ingested |
| 7  | Critical Limitation   | Mandatory contextual disclaimer  | Excludes equity bonuses & benefits |
+----+-----------------------+----------------------------------+------------------------------------+
```

### 1.1 Context-Appropriate Application Rule
The 7-element standard must **not** be rigidly forced into cards where elements are non-applicable:
- **Descriptive Statutory Observations (e.g. WGEA Size Band):** Does **not** require a machine learning confidence score or $R^2$ metric. Render: Factual Size Band + Statutory Source + Reference Period + Verification Date.
- **Pure Search Lookups (e.g. Employer ABN):** Does **not** require an uncertainty range. Render: Verified Sovereign Identifier + ABR Source Drawer.
- **Statistical Regression (Salary):** **Must** include Elements 1, 2, 3, 5, 6, and 7.

---

## 2. ELIMINATING THE FIVE CONFUSED STATISTICAL CONCEPTS

A severe product flaw in analytics dashboards is conflating different types of reliability indicators. JOBINTEL strictly isolates these five concepts:

```
====================================================================================================
THE FIVE DISTINCT RELIABILITY CONCEPTS
====================================================================================================
Concept                      Definition                                     Product Representation
----------------------------------------------------------------------------------------------------
1. Model Confidence          Model's internal score for a specific single   Qualitative tier ("High",
                             inference instance (e.g. ECE-calibrated prob). "Moderate", "Review Queue").
2. Evaluation Accuracy       Historical performance on an out-of-sample     Reported in Model Cards and
                             test set (e.g. 97.0% title mapping accuracy).  Provenance Drawers.
3. Data Completeness         Proportion of required profile attributes      Progress indicator (e.g. 
                             present in the record (e.g. 8 of 10 fields).   "Profile 80% Complete").
4. Source Reliability        Authoritativeness of originating publisher    Source badge ("Official
                             (e.g. SEC EDGAR vs. direct ATS portal).        Statutory", "First-Party ATS").
5. Prediction Uncertainty    Statistical dispersion around the estimated    Numerical interval bracket
                             conditional mean (e.g. P10–P90 residual band). (e.g. "₹10.4 – 14.6 LPA").
====================================================================================================
```

---

## 3. INSUFFICIENT EVIDENCE & FALLBACK PRESENTATION

When a query lacks adequate supporting data points (e.g. an obscure job title with $< 5$ market observations, or a geographic region without salary samples):

### 3.1 Prohibited Fallback Behavior
- ❌ Do **not** invent synthetic midpoints or extrapolate national averages without disclosure.
- ❌ Do **not** display "0.0" or "₹0 LPA" (which conflates unavailable data with a measured zero).

### 3.2 Mandated Insufficient Evidence Pattern
- Display an explicit **"Insufficient Market Evidence"** banner:
  > *"Fewer than 5 verified observations exist for this specific role and location combination. To maintain statistical reliability, an automated estimate is withheld. Explore related regional roles or canonical occupation aggregates."*
- Route the entity or query to an internal expansion backlog.
