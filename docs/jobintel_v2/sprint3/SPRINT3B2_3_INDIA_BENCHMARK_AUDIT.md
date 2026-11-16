# JOBINTEL 2.0 — SPRINT 3B.2.3 INDIA BENCHMARK AUDIT REPORT
## Scope Delimitation, MoSPI National Survey Disclaimers & Empirical Sample Authenticity

**Audit Date:** November 16, 2026  
**Auditor:** Independent Labour Market Statistics Specialist & Data Governance Auditor  
**Audit Scope:** Independent inspection of `src/backend/data/demand/observations.json`, `src/backend/data/demand/sources.json`, `src/backend/schemas/demand.py`, `src/backend/services/demand_service.py`, and `frontend/src/pages/DemandPage.tsx`.

---

### 1. AUDIT OBJECTIVE & CONTEXT

Unlike the United States (BLS), Australia (JSA), and Singapore (MOM), the Republic of India does not maintain a statutory, quarterly enterprise vacancy survey or an official national online job advertisement time-series at the Ministry of Statistics and Programme Implementation (MoSPI) or Periodic Labour Force Survey (PLFS) level.

The Sprint 3B.2.1 independent audit identified a critical risk: if Indian job posting figures were displayed alongside official Western vacancy figures without explicit framing, users might assume they represent an official government census.

Sprint 3B.2.2 introduced strict provenance bounding for India. This independent audit evaluated:
1. Whether all India demand records are properly categorized as `JOBINTEL_CURATED`.
2. Whether public responses disclaim official MoSPI national census status.
3. Whether geographic and sectoral selection bias is documented.
4. Whether the frontend UI reinforces these limitations.

---

### 2. RECORD AUDIT OF INDIAN OBSERVATIONS

The audit inspected all 3 Indian demand observations in `src/backend/data/demand/observations.json`:

| Observation ID | National Occupation (NCO-2015) | Metric Type | Metric Value & Unit | Provenance Category | Source ID |
|---|---|---|---|---|---|
| `dmd-in-2512.0100-2024` | `IN_NCO_2015:2512.0100` (Software Engineer) | `OBSERVED_JOB_ADVERTISEMENTS` | 24,500 Benchmark Postings (Sample) | `JOBINTEL_CURATED` | `in.jobintel.tech-demand` |
| `dmd-in-2511.0100-2024` | `IN_NCO_2015:2511.0100` (Systems Analyst) | `OBSERVED_JOB_ADVERTISEMENTS` | 3,800 Benchmark Postings (Sample) | `JOBINTEL_CURATED` | `in.jobintel.tech-demand` |
| `dmd-in-2521.0100-2024` | `IN_NCO_2015:2521.0100` (Database Admin) | `OBSERVED_JOB_ADVERTISEMENTS` | 2,600 Benchmark Postings (Sample) | `JOBINTEL_CURATED` | `in.jobintel.tech-demand` |

#### Key Verification Findings:
1. **Provenance Classification:** 3/3 records are explicitly tagged `DemandProvenance.JOBINTEL_CURATED` (`"provenance": "JOBINTEL_CURATED"`).
2. **Metric Unit Specification:** The unit string is `"Benchmark Online Postings (Sample)"`, avoiding misleading units like "Official Vacancies".
3. **Source Attribution:** Sourced to `in.jobintel.tech-demand`, with publisher identified as `"JobIntel Research Engineering"`.

---

### 3. MANDATORY DISCLOSURES & MOSPI SURVEY DISCLAIMERS

The audit inspected `src/backend/services/demand_service.py` (lines 380–384) to verify the automatic attachment of India-specific disclaimers:

#### Benchmark Disclosure String:
> *"Based on a JobIntel empirical technology-hub job-posting sample. This is not an official MoSPI national vacancy census and does not represent every occupation or region in India."*

#### Regional Breakdown Disclosure:
> *"Regional breakdowns reflect technology-hub posting sample shares across Bangalore, Hyderabad, NCR, and Pune."*

#### Methodological Limitations Injected:
- *"Does not measure offline vacancies, informal hiring, or net hires."*
- *"Biased toward digital-first and professional occupations."*
- *"India tech demand figures represent a calibrated sample benchmark of online tech postings across major tech hubs, not an exhaustive national census of informal employment."*

---

### 4. SELECTION BIAS & SAMPLING FRAME LIMITATIONS

The audit verified that the documentation and metadata acknowledge known sampling limitations:
1. **Sectoral Concentration:** The sample covers only formal corporate technology employers posting online. It omits India's massive informal workforce, small and medium enterprises (MSMEs), and public sector / PSU hiring.
2. **Geographic Concentration:** Postings are sampled strictly from Tier-1 technology corridors:
   - Bangalore (Karnataka): ~34%
   - Hyderabad (Telangana): ~21%
   - Pune (Maharashtra): ~15%
   - Delhi NCR (Gurgaon / Noida): ~14%
   - Chennai (Tamil Nadu): ~10%
   - Mumbai (Maharashtra): ~6%
3. **Temporal Scope:** Calibrated for 2024 hiring telemetry.

---

### 5. FRONTEND PRESENTATION AUDIT

The audit verified `frontend/src/pages/DemandPage.tsx` live rendering:
1. **Benchmark Alert Banner:** Displays an amber alert banner titled:
   `CALIBRATED BENCHMARK — EMPIRICAL TECH SAMPLE`
   containing the full MoSPI disclaimer text.
2. **Provenance Badge:** The pill renders amber with label `"JobIntel research benchmark"` and a clickable explanation modal.
3. **Market Overview Card:** Market 1 card displays coverage status `"Validated Tech Demand Benchmark"`.

---

### 6. AUDIT VERDICT

```text
INDIA BENCHMARK AUDIT VERDICT: VERIFIED CLOSED
Status: PASS
Provenance: 100% JOBINTEL_CURATED.
MoSPI Survey Disclaimer: Enforced across API and UI.
Selection Bias: Formally documented in metadata and disclaimers.
```
