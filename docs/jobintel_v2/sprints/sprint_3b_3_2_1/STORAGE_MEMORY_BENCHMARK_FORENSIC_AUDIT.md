# SPRINT 3B.3.2.1 — DELIVERABLE 9
# STORAGE & MEMORY BENCHMARK FORENSIC AUDIT
## Independent Verification of Footprint Calculations, Tracemalloc Semantics & Render 512 MB Feasibility

**Sprint:** 3B.3.2.1 — Forensic Artifact Verification & Independent Evidence Audit  
**Auditor Role:** Independent Principal Data Auditor, Systems Performance & QA Lead  
**Artifacts Under Audit:**  
- `scratch/benchmark_storage_memory.py`  
- `scratch/storage_benchmark_results.json`  
- `docs/jobintel_v2/sprints/sprint_3b_3_2/EMPLOYER_STORAGE_MEMORY_BENCHMARK.md`  

---

## 1. EMPIRICAL BENCHMARK AUDIT SUMMARY

An independent verification of the storage and memory benchmark was conducted, reconciling disk file sizes, in-memory allocations, query latencies, and scaling projections.

```
+----------------------------------------------------------------------------------------------------+
| STORAGE AND MEMORY BENCHMARK AUDIT RECONCILIATION                                                  |
+--------------------------+-----------------------+-----------------------+-------------------------+
| Benchmark Dimension      | Sprint 3B.3.2 Claim   | Independent Audit     | Audit Assessment        |
+--------------------------+-----------------------+-----------------------+-------------------------+
| Total Raw JSON Disk Size | 76,938 bytes (75.1 KB)| 76,938 bytes          | PASS — Exact byte match |
| Gzip Compressed Disk Size| 10,775 bytes (10.5 KB)| 10,775 bytes          | PASS — Exact byte match |
| Gzip Compression Ratio   | 7.14x (86.0% savings) | 7.14x                 | PASS                    |
| Traced Resident Heap     | 247,473 bytes (241 KB)| 247,473 bytes         | PASS — Exact match      |
| Per-Employer Heap Usage  | 8,838.3 bytes (8.6 KB)| 8,838.3 bytes         | PASS — Correct average  |
| ID Lookup Latency (p50)  | 3.10 µs               | 3.10 µs               | PASS                    |
| Domain Lookup Latency    | 3.20 µs               | 3.20 µs               | PASS                    |
| Filter Latency (p50)     | 10.40 µs              | 10.40 µs              | PASS                    |
| Render Free RAM Margin   | "Zero OOM Risk"       | OVERSTATED CLAIM      | CORRECTED TO LOW RISK   |
+--------------------------+-----------------------+-----------------------+-------------------------+
```

---

## 2. CRITICAL AUDIT DISTINCTION: TRACEMALLOC VS. PROCESS RSS

### The Defect Identified in Previous Reporting
Sprint 3B.3.2 interchangeably used the terms *"Resident In-Memory Footprint"*, *"RAM Usage"*, and *"tracemalloc"*, creating the impression that total process memory overhead was only 241 KB.

### Independent Systems Engineering Correction
1. **What `tracemalloc` Actually Measures:**
   Python's `tracemalloc` module tracks memory blocks allocated directly by CPython through `PyObject_Malloc` and `PyMem_Malloc`.
2. **What `tracemalloc` Does NOT Measure:**
   - Native C/C++ heap allocations outside Python allocators (e.g. underlying buffers in NumPy, Pandas, or `pydantic-core` Rust memory).
   - Python runtime interpreter executable overhead, shared libraries (`.so`/`.dll`), and thread stacks.
   - OS-level memory fragmentation and memory allocated in arenas but not released back to the OS by glibc `free()`.
   - Temporary JSON serialization buffers during high-concurrency HTTP request handling.
3. **Audit Finding:**
   The measured **241.67 KB** is strictly the **Python Traced Object Heap** for the 28-record dataset, Pydantic schemas, and inverted index hash tables. Real OS Process Resident Set Size (RSS) will include standard runtime overhead.

---

## 3. RENDER DEPLOYMENT FEASIBILITY & BASELINE VERIFICATION

### 3.1 Baseline Memory Qualification
- The claimed backend baseline RAM of **195.0 MB** was derived from telemetry during the Sprint 3B.2.3.5 staging deployment (FastAPI + Uvicorn + Salary/Demand modules on Render Free).
- **Audit Status:** Marked as **ESTIMATED FROM STAGING TELEMETRY (UNVERIFIED IN CURRENT READ-ONLY SPRINT)**. Live Render process RSS cannot be queried without deploying new instrumentation or accessing cloud container metrics.

### 3.2 Measured vs. Extrapolated Scale Projections

```
+----------------------------------------------------------------------------------------------------+
| COHORT SCALE PROJECTIONS: MEASURED VS. EXTRAPOLATED                                                |
+--------+--------------+---------------+-------------------+--------------------+-------------------+
| Cohort | Status       | Raw JSON Disk | Gzip Compressed   | Traced Python Heap | Estimated RSS     |
+--------+--------------+---------------+-------------------+--------------------+-------------------+
| 28     | MEASURED     | 75.1 KB       | 10.5 KB           | 241.7 KB           | ~0.5 - 1.0 MB     |
| 100    | EXTRAPOLATED | 268.3 KB      | 37.6 KB           | 863.1 KB (~0.84 MB)| ~2.0 - 3.5 MB     |
| 250    | EXTRAPOLATED | 670.8 KB      | 94.0 KB           | 2.11 MB            | ~4.5 - 7.0 MB     |
| 500    | EXTRAPOLATED | 1.34 MB       | 187.9 KB          | 4.22 MB            | ~9.0 - 14.0 MB    |
| 2,500  | EXTRAPOLATED | 6.71 MB       | 939.5 KB          | 21.07 MB           | ~35.0 - 50.0 MB   |
+--------+--------------+---------------+-------------------+--------------------+-------------------+
```

### 3.3 Correction of "Zero OOM Risk" Claim
Sprint 3B.3.2 claimed *"Zero OOM Risk"* on Render Free.  
**Auditor Rejection & Correction:**
- On Render Free (512 MB hard ceiling), out-of-memory kills occur not only from static dataset storage, but from **dynamic request bursts, simultaneous user queries, large unpaginated JSON serialization responses, and memory fragmentation**.
- At MVP scale (100–250 employers), the incremental memory footprint of 0.84–2.11 MB is **negligible (< 1% of 317 MB headroom)** and presents **LOW OPERATIONAL RISK**.
- However, at commercial scale (> 2,500 employers), loading the entire dataset into memory with unpaginated full-corpus queries presents genuine OOM vulnerability under concurrent loads.
- **Mandated Architecture Strategy for Scale:** Mandate database offloading (SQLite / PostgreSQL), HTTP response pagination (`limit` / `offset`), and in-memory LRU caching capped at 1,000 active profiles before expanding beyond 1,000 employers.
