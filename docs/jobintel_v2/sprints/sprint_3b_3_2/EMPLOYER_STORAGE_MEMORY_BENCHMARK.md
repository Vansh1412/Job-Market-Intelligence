# SPRINT 3B.3.2 — DELIVERABLE 12
# EMPLOYER STORAGE & MEMORY BENCHMARK
## Empirical Footprint Measurement, Scale Projections & Render Free Tier Feasibility

---

## 1. EXECUTIVE SUMMARY

An empirical storage, memory, and query performance benchmark was executed on the JOBINTEL 2.0 Sprint 3B.3.2 verified five-market employer pilot dataset (28 anchor employers across Australia, United States, United Kingdom, Singapore, and India, with 32 hiring/headcount observations, 22 canonical skill observations, and 14 qualified source catalog records).

All measurements were taken using Python's `tracemalloc`, `sys.getsizeof`, `gzip`, and high-resolution `time.perf_counter` timers over 1,000 iterations for each query pattern.

```
+----------------------------------------------------------------------------------------------------+
| EMPIRICAL MEASUREMENT HIGHLIGHTS                                                                   |
+----------------------------------+-----------------------+-----------------------------------------+
| Metric                           | Measured Value        | Normalized / Per Unit                   |
+----------------------------------+-----------------------+-----------------------------------------+
| Total Raw Dataset Size (JSON)    | 76,938 bytes          | 2,747.8 bytes / employer                |
| Total Compressed Size (gzip)     | 10,775 bytes          | 384.8 bytes / employer                  |
| Compression Ratio (gzip)         | 7.14x (86.0% savings) | -                                       |
| Core Employer Profile (Raw JSON) | 28,198 bytes          | 1,007.1 bytes / record                  |
| In-Memory Resident Footprint     | 247,473 bytes         | 8,838.3 bytes / employer (Dicts+Pydantic) |
| Peak Load Process Memory         | 247,521 bytes         | ~241.7 KB overhead                      |
| Query Latency: ID Lookup (p50)   | 3.10 microseconds     | p99: 4.20 microseconds                  |
| Query Latency: Domain (p50)      | 3.20 microseconds     | p99: 4.40 microseconds                  |
| Query Latency: Filter (p50)      | 10.40 microseconds    | p99: 13.80 microseconds                 |
+----------------------------------+-----------------------+-----------------------------------------+
```

---

## 2. REAL-DATA FOOTPRINT MEASUREMENT

### 2.1 File Storage Footprint (Disk)

The employer intelligence pilot encompasses four core JSON datasets and one CSV representation:

| File Name | Record Count | Raw Disk Size (Bytes) | Gzip Compressed Size (Bytes) | Compression Ratio |
| :--- | :--- | :--- | :--- | :--- |
| `employer_pilot_records.json` | 28 employers | 28,198 | 3,220 | 8.76x (88.6%) |
| `employer_hiring_observations.json` | 32 observations | 21,573 | 2,105 | 10.25x (90.2%) |
| `employer_skill_observations.json` | 22 skill requirements | 10,956 | 1,386 | 7.90x (87.3%) |
| `employer_source_catalog.json` | 14 source definitions | 16,211 | 4,064 | 3.99x (74.9%) |
| **Total JSON Repository Size** | **96 entities** | **76,938 bytes (75.1 KB)** | **10,775 bytes (10.5 KB)** | **7.14x (86.0%)** |
| `employer_pilot_records.csv` | 28 employers | 7,956 | 2,433 | 3.27x (69.4%) |

### 2.2 In-Memory Resident Footprint (`tracemalloc`)

Memory consumption was measured at each stage of ingestion into the Python 3 runtime:

| Data Structure / Memory Phase | Traced Resident Memory | Memory Share | Description |
| :--- | :--- | :--- | :--- |
| **Raw Python Dictionaries** | 150,097 bytes (146.6 KB) | 60.6% | Deserialized JSON objects, strings, lists, and dict hash tables |
| **Pydantic v2 Models (`EmployerProfile`)** | 87,664 bytes (85.6 KB) | 35.4% | Validated schema instances with typed fields and URL parsing |
| **Inverted In-Memory Indexes** | 9,624 bytes (9.4 KB) | 3.9% | Primary key, domain, market, and industry index hash tables |
| **Total Resident Memory Footprint** | **247,473 bytes (241.7 KB)** | **100.0%** | Combined active heap allocation for the full pilot dataset |
| **Peak Memory Allocation** | **247,521 bytes (241.7 KB)** | - | Peak allocation during JSON parsing and schema instantiation |

### 2.3 Query Performance & Latency Benchmarks

Latencies were sampled over 1,000 warm-up and measured iterations on an AMD/Intel x86_64 host:

| Query Type | Index Structure Utilized | p50 Latency | p95 Latency | p99 Latency | Mean Latency | Target SLA | Compliance |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Lookup by Employer ID** (`EMP_AU_001`) | Hash map `dict[str, dict]` | 3.10 µs | 3.10 µs | 4.20 µs | 3.12 µs | < 1,000 µs (1 ms) | **PASS (322x faster)** |
| **Lookup by Primary Domain** (`atlassian.com`) | Hash map `dict[str, dict]` | 3.20 µs | 3.30 µs | 4.40 µs | 3.26 µs | < 1,000 µs (1 ms) | **PASS (312x faster)** |
| **Filter by Market + Industry** (`AU` + `Tech`) | Inverted index + predicate filter | 10.40 µs | 10.60 µs | 13.80 µs | 10.51 µs | < 5,000 µs (5 ms) | **PASS (480x faster)** |

All queries resolve in **under 15 microseconds**, ensuring zero frontend latency impact.

---

## 3. SCALE PROJECTIONS — EVIDENCE VS. PHASE 0 ASSUMPTIONS

### 3.1 Phase 0 Claims vs. Real Empirical Evidence

In Sprint 3B.3 Phase 0, a theoretical estimate was recorded:
- *Phase 0 Claim:* 2,500 employers = ~2.5 MB raw JSON, ~0.5 MB compressed JSON, ~5.0 MB resident RAM.

Based on the actual measured footprint of **2,747.8 bytes raw JSON** and **8,838.3 bytes resident RAM per employer** (inclusive of normalized observations, provenance ledgers, and indexing), the empirical mathematical projections are as follows:

| Scale Horizon | Employer Count | Raw JSON Footprint | Gzip Compressed Disk | In-Memory Heap (`tracemalloc`) |
| :--- | :--- | :--- | :--- | :--- |
| **Current Pilot** | 28 | 75.1 KB | 10.5 KB | 0.24 MB (241.7 KB) |
| **Target MVP** | 100 | 268.3 KB | 37.6 KB | 0.84 MB (863.1 KB) |
| **Extended Cohort** | 250 | 670.8 KB | 94.0 KB | 2.11 MB |
| **Commercial Scale** | 1,000 | 2.68 MB | 375.8 KB | 8.43 MB |
| **Phase 0 Scale** | **2,500** | **6.71 MB** | **0.94 MB** | **21.07 MB** |

### 3.2 Discrepancy Analysis & Evaluation

```
+----------------------------------------------------------------------------------------------------+
| PHASE 0 ESTIMATE DISCREPANCY AUDIT                                                                |
+--------------------------+--------------------+--------------------+-------------------------------+
| Dimension                | Phase 0 Assumption | Empirical Measured | Discrepancy Assessment        |
+--------------------------+--------------------+--------------------+-------------------------------+
| Raw JSON (2,500 emps)    | 2.50 MB            | 6.71 MB            | UNDERESTIMATED (+168.4%)      |
| Compressed (2,500 emps)  | 0.50 MB            | 0.94 MB            | UNDERESTIMATED (+88.0%)       |
| In-Memory RAM (2,500 emps| 5.00 MB            | 21.07 MB           | UNDERESTIMATED (+321.4%)      |
+--------------------------+--------------------+--------------------+-------------------------------+
```

**Verdict:** **UNDERESTIMATED** (Actual measurements are > 20% larger across all three dimensions).

#### Why Did the Discrepancy Occur?
1. **Relational Entity Normalization:** Phase 0 assumed a flat single-record profile of ~1 KB. Real data architecture requires multiple linked entity tables: core entity, statutory hiring/headcount observations (with stock/flow metadata), skill requirements (with short-token protection tags), and source catalog entries.
2. **Provenance & Governance Rigor:** Each record carries complete cryptographic SHA-256 evidence citations, statutory registration IDs (ABN, CIK, UEN, CIN, Company Number), legal entity names, trading names, and publication gate flags.
3. **Dual Representation Overhead:** Storing both categorical size bands (`"1000 to 4999"`) and verified scalar headcounts (`12,000`) with verification timestamps and measurement scopes adds structural field overhead.
4. **Python Object & Hash Table Overhead:** CPython dicts allocate memory in power-of-two blocks and store 64-bit pointers, keys, hash values, and PyObject headers. Pydantic v2 models add Rust-based core validator structures.

---

## 4. RENDER DEPLOYMENT FEASIBILITY (512 MB CEILING)

### 4.1 Headroom Analysis

The JOBINTEL 2.0 backend runs on the Render Free Tier with a hard memory limit of **512 MB RAM**.

- **Current Backend Baseline RAM Usage:** Measured during Sprint 3B.2.3.5 staging deployment at **195.0 MB** (FastAPI, Uvicorn, Pandas/Numpy runtimes, salary intelligence, demand intelligence, and market modules).
- **Available Usable Headroom:** $512.0\text{ MB} - 195.0\text{ MB} = \mathbf{317.0\text{ MB}}$.
- **Safe 50% Threshold Headroom (256 MB total):** $256.0\text{ MB} - 195.0\text{ MB} = \mathbf{61.0\text{ MB}}$.
- **OOM Risk Threshold Headroom (400 MB total):** $400.0\text{ MB} - 195.0\text{ MB} = \mathbf{205.0\text{ MB}}$.

### 4.2 Employer Capacity Under Memory Ceilings

Using the measured empirical rate of **8.63 KB (0.00843 MB) RAM per employer**:

| Operating Threshold | Target Total RAM | Available Memory for Employers | Maximum Supported Employers | Feasibility Status |
| :--- | :--- | :--- | :--- | :--- |
| **Current Pilot** | 195.24 MB | 0.24 MB consumed | 28 employers | **100% SAFE (< 0.1% headroom)** |
| **MVP Release** | 195.84 MB | 0.84 MB consumed | 100 employers | **100% SAFE (0.27% headroom)** |
| **Extended Cohort** | 197.11 MB | 2.11 MB consumed | 250 employers | **100% SAFE (0.67% headroom)** |
| **Phase 0 Scale** | 216.07 MB | 21.07 MB consumed | 2,500 employers | **SAFE (6.65% headroom)** |
| **50% RAM Threshold** | 256.00 MB | 61.00 MB available | **7,237 employers** | **Upper limit for zero-GC drift** |
| **Render OOM Threshold**| 400.00 MB | 205.00 MB available | **24,321 employers** | **Absolute memory wall** |

### 4.3 Architecture Feasibility Decision for MVP (100–250 Employers)

**Decision:** **YES — 100% FEASIBLE WITH IN-MEMORY DATA STORAGE**.

- Loading 100 employers adds only **0.84 MB** to backend RAM (0.27% of available headroom).
- Loading 250 employers adds only **2.11 MB** to backend RAM (0.67% of available headroom).
- Even loading the full Phase 0 cohort of 2,500 employers consumes only **21.07 MB**, leaving **295.93 MB of safety buffer** below the 512 MB ceiling.

### 4.4 Future Scale Architecture Strategy (> 5,000 Employers)

When scaling beyond 5,000 employers, the following tiered architecture must be implemented:
1. **SQLite / PostgreSQL Offloading:** Store historical hiring observations and granular job postings in a relational database with indexes on `company_id`, `market_id`, and `canonical_occ_code`.
2. **LRU Cache for Profiles:** Maintain an in-memory LRU cache (`cachetools.TTLCache`) capped at 1,000 active employer profiles (~8.5 MB RAM).
3. **Response Compression:** Enable `GZipMiddleware` on FastAPI endpoints, reducing payload transit sizes from ~75 KB to ~10.5 KB per 100-record response.
