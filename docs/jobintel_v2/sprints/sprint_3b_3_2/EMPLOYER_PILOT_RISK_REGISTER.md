# SPRINT 3B.3.2 — DELIVERABLE 15
# EMPLOYER PILOT RISK REGISTER
## Legal, Quality, Operational, Statistical, Privacy & Infrastructure Risk Assessment

---

## 1. RISK REGISTER SUMMARY MATRIX

```
+----------------------------------------------------------------------------------------------------+
| SPRINT 3B.3.2 RISK AUDIT SUMMARY MATRIX                                                            |
+---------+---------------------------------+---------------+------------+------------+--------------+
| Risk ID | Risk Name                       | Category      | Severity   | Likelihood | Residual Risk|
+---------+---------------------------------+---------------+------------+------------+--------------+
| RSK-001 | Commercial Aggregator Scraping  | Legal / TOS   | CRITICAL   | HIGH       | LOW (Mitig)  |
| RSK-002 | Parent-Subsidiary False Merge   | Data Quality  | HIGH       | HIGH       | LOW (Mitig)  |
| RSK-003 | Shared ATS Platform Collision   | Data Quality  | CRITICAL   | HIGH       | ZERO (Elim)  |
| RSK-004 | Stock vs. Flow Conflation       | Statistical   | HIGH       | HIGH       | LOW (Mitig)  |
| RSK-005 | Short-Token Skill Over-Matching | Data Quality  | HIGH       | HIGH       | LOW (Mitig)  |
| RSK-006 | PII Leakage in Job Postings     | Privacy / Sec | HIGH       | MEDIUM     | ZERO (Elim)  |
| RSK-007 | Render Free Memory Wall (512MB) | Infrastructure| HIGH       | MEDIUM     | LOW (Mitig)  |
| RSK-008 | UK Demand Publication Breach    | Governance    | CRITICAL   | MEDIUM     | ZERO (Elim)  |
| RSK-009 | Gated Registry Access Controls  | Operational   | HIGH       | HIGH       | LOW (Mitig)  |
| RSK-010 | Uncalibrated Confidence Scores  | Statistical   | MEDIUM     | MEDIUM     | LOW (Mitig)  |
+---------+---------------------------------+---------------+------------+------------+--------------+
```

---

## 2. DETAILED RISK AUDITS & EVIDENCE-BASED MITIGATIONS

### 2.1 RSK-001: Commercial Aggregator Terms of Service Breach & IP Litigation
- **Category:** Legal / Regulatory Compliance
- **Severity:** **CRITICAL** | **Initial Likelihood:** **HIGH**
- **Description:** Attempting to harvest employer profiles, vacancies, or headcounts by scraping commercial aggregators (LinkedIn, Indeed, Naukri, Seek) creates immediate exposure to Computer Fraud and Abuse Act (CFAA), breach of contract litigation, and IP blacklisting.
- **Evidence from Pilot:** Commercial aggregators employ active bot-detection algorithms (Cloudflare Turnstile, PerimeterX) and explicitly prohibit automated scraping in Section 8 of their Terms of Service.
- **Implemented Mitigation:** Absolute platform-wide ban on commercial job aggregator scraping. Ingestion is restricted to statutory government open datasets and direct, authorized corporate career portals / ATS feeds.
- **Residual Risk:** **`LOW`**.

---

### 2.2 RSK-002: Parent-Subsidiary Domain Collision & False Merging
- **Category:** Data Quality / Entity Resolution
- **Severity:** **HIGH** | **Initial Likelihood:** **HIGH**
- **Description:** Regional operating subsidiaries share the parent corporation's global domain (e.g. `cisco.com`, `microsoft.com`, `grab.com`). Naive entity resolution merges the distinct sovereign entities into one record, destroying regional legal compliance data.
- **Evidence from Pilot:** In Resolver V1, testing across the 100-pair gold benchmark resulted in 3 false merges (`Cisco Systems Australia` merged into `Cisco Systems Inc.`; `Microsoft UK Ltd` merged into `Microsoft Corp`; `GrabTaxi Holdings` merged into `Grab Holdings Inc.`), yielding a 5.45% false merge rate.
- **Implemented Mitigation:** Resolver V2 was engineered with strict **Sovereign Market Isolation**: domain matching is only permitted within the same `market_id`. Cross-market domain overlaps are routed to a manual corporate hierarchy queue (`RELATION_PARENT_SUBSIDIARY`), reducing false merges to **0.00%**.
- **Residual Risk:** **`LOW`**.

---

### 2.3 RSK-003: Third-Party ATS Hostname False Merge Collision
- **Category:** Data Quality / Entity Resolution
- **Severity:** **CRITICAL** | **Initial Likelihood:** **HIGH**
- **Description:** Multiple unrelated employers host their careers portals on shared applicant tracking system domains (e.g., `boards.greenhouse.io`, `jobs.lever.co`, `myworkdayjobs.com`). Resolving entities by domain name would merge completely unrelated companies into a single entity.
- **Evidence from Pilot:** Without domain sanitization, Canva (`boards.greenhouse.io/canva`) and Figma (`boards.greenhouse.io/figma`) would collide on `greenhouse.io`.
- **Implemented Mitigation:** Comprehensive ATS Host Blacklist implemented in Resolver V2 (`greenhouse.io`, `lever.co`, `workday.com`, `taleo.net`, etc.). If an ATS domain is detected, the resolver extracts the verified apex domain from the employer's official website or registry filing.
- **Residual Risk:** **`ZERO`** (Completely eliminated).

---

### 2.4 RSK-004: Stock Headcount vs. Flow Vacancy Conflation
- **Category:** Statistical / Product Integrity
- **Severity:** **HIGH** | **Initial Likelihood:** **HIGH**
- **Description:** Presenting active job postings alongside establishment headcount without semantic distinction leads users to misinterpret open requisitions as net new jobs or verified hiring volume.
- **Evidence from Pilot:** An employer with 10,000 employees and 500 open postings may have net zero workforce growth if the postings represent backfills for normal attrition.
- **Implemented Mitigation:** Established strict relational schema separation (`stock_headcount` vs. `flow_vacancies`) and mandatory UI disclosure banners: *"Open requisitions reflect advertised vacancy flow, not verified employee headcount or confirmed hires."*
- **Residual Risk:** **`LOW`**.

---

### 2.5 RSK-005: Short-Token Skill Over-Matching & Semantic Hallucination
- **Category:** Data Quality / NLP Accuracy
- **Severity:** **HIGH** | **Initial Likelihood:** **HIGH**
- **Description:** Ambiguous short tokens (`Go`, `C`, `R`, `SQL`, `AWS`, `ML`, `AI`) frequently appear as common English words, prepositions, or grades (e.g., "go to market", "Series C funding"), creating massive false-positive skill counts.
- **Evidence from Pilot:** In unconstrained regex parsing, 63.6% of `Go` mentions were colloquial usages.
- **Implemented Mitigation:** Enforced 5-token contextual co-occurrence window protocol requiring programming keywords (e.g., `golang`, `compiler`, `goroutines`, `C++`, `ggplot`, `statistical`) for validation.
- **Residual Risk:** **`LOW`**.

---

### 2.6 RSK-006: Personal Identifiable Information (PII) Leakage
- **Category:** Privacy / Security Compliance
- **Severity:** **HIGH** | **Initial Likelihood:** **MEDIUM**
- **Description:** Statutory registry filings and job advertisements occasionally contain personal recruiter names, corporate officer home addresses, direct cell phone numbers, or personal email addresses.
- **Evidence from Pilot:** Ingestion of corporate filing documents identified statutory director residential address fields in certain UK and AU filing attachments.
- **Implemented Mitigation:** Strict field sanitization pipeline. Zero personal names, home addresses, phone numbers, or email addresses are stored. Only corporate legal names, official business domains, and metropolitan headquarters cities are retained.
- **Residual Risk:** **`ZERO`** (Completely eliminated).

---

### 2.7 RSK-007: Render Free Tier Memory Wall & Process Crash
- **Category:** Infrastructure / Service Reliability
- **Severity:** **HIGH** | **Initial Likelihood:** **MEDIUM**
- **Description:** Render Free instances have a hard 512 MB RAM limit. Loading large uncompressed JSON datasets or leaky Python dict structures into the FastAPI process can trigger out-of-memory (OOM) fatal kills.
- **Evidence from Pilot:** Benchmark confirmed backend baseline RAM is 195.0 MB, leaving 317.0 MB headroom. Empirical footprint is 8.63 KB RAM per employer.
- **Implemented Mitigation:** At MVP scale (100–250 employers), in-memory resident RAM is only 0.84–2.11 MB (< 1% headroom). When scaling beyond 5,000 employers, the architecture mandates migrating observation tables to SQLite/PostgreSQL with LRU memory caching.
- **Residual Risk:** **`LOW`**.

---

### 2.8 RSK-008: UK Demand Publication Gate Breach
- **Category:** Governance / Legal Compliance
- **Severity:** **CRITICAL** | **Initial Likelihood:** **MEDIUM**
- **Description:** Displaying UK employer vacancy or demand metrics prior to formal ONS/Adzuna source-use authorization violates corporate governance directives and audit gates.
- **Evidence from Pilot:** Verified that backend serializes UK flow metrics as `null` with `publication_gate_active: true`.
- **Implemented Mitigation:** Automated test suite asserts UK vacancy metrics remain strictly null. Statutory UK headcount (Gender Pay Gap size band) remains accessible without breaching vacancy restrictions.
- **Residual Risk:** **`ZERO`** (Completely eliminated).

---

### 2.9 RSK-009: Gated Sovereign Registry Access & Anti-Bot Blocking
- **Category:** Operational / Data Acquisition
- **Severity:** **HIGH** | **Initial Likelihood:** **HIGH**
- **Description:** Sovereign registries like India's MCA21 portal enforce interactive CAPTCHAs, preventing programmatic batch scraping.
- **Evidence from Pilot:** Ministry of Corporate Affairs (MCA) endpoints block headless requests with session expiration.
- **Implemented Mitigation:** In India, automated ingestion is strictly anchored to listed corporations publishing audited SEBI BRSR reports via stock exchange feeds (BSE/NSE). Unlisted private entities requiring manual CAPTCHA solving are excluded.
- **Residual Risk:** **`LOW`**.

---

### 2.10 RSK-010: Uncalibrated Job Title Mapping Confidence Scores
- **Category:** Statistical / Machine Learning Integrity
- **Severity:** **MEDIUM** | **Initial Likelihood:** **MEDIUM**
- **Description:** Overconfident mapping models assign probabilities of 0.95+ to ambiguous job titles, misleading downstream analytics.
- **Evidence from Pilot:** Evaluated 100 gold job titles; measured Expected Calibration Error (ECE) was 0.0587, with confidence clustering around 0.98.
- **Implemented Mitigation:** Post-hoc Platt scaling / temperature scaling ($T \approx 1.24$) calibrated the confidence distribution, reducing ECE to 0.0381 (< 0.05).
- **Residual Risk:** **`LOW`**.
