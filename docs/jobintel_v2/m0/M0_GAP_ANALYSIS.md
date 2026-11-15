# M0 Gap Analysis

Status key: IMPLEMENTED AND VERIFIED; PARTIALLY IMPLEMENTED; EXISTS BUT NOT VERIFIED; NOT IMPLEMENTED; BLOCKED BY DATA OR ARCHITECTURE; REQUIRES RESEARCH.

| Capability | Status | Evidence / reason |
|---|---|---|
| India and USA market prediction | PARTIALLY IMPLEMENTED | Separate inference services/artifacts and routes exist; test baseline is incomplete; live production not verified. |
| Five-market registry/adapters | NOT IMPLEMENTED | Market union and APIs only India/USA. |
| Canonical occupation identity and mapping confidence | NOT IMPLEMENTED | Current market-specific role families and small cross-market hand mapping; no versioned canonical registry. |
| ANZSCO/OSCA/SOC/SSOC/ISCO correspondences | REQUIRES RESEARCH | Official mapping assets exist for new country classifications but no ingestion/mapping implementation. |
| Source registry/provenance/freshness | NOT IMPLEMENTED | Config/data docs are narrative and market-specific; no common source/vintage quality contract found. |
| Multi-market ingestion and validation | NOT IMPLEMENTED | Current training scripts/notebooks target existing cohorts; no new-market data adapters. |
| Salary normalization | PARTIALLY IMPLEMENTED | India LPA and USA annual USD output; cross-market comparison keeps native currencies; new-market gross/basic/annualization rules absent. |
| Salary percentile distributions | PARTIALLY IMPLEMENTED | Existing market aggregates and hard-coded prediction context; actual quantile APIs for India/USA; no five-market service. |
| Cross-market comparison | PARTIALLY IMPLEMENTED | Existing USA/India cross-market summary; group mapping and native currency, not canonical occupations. |
| Scenario intelligence | NOT IMPLEMENTED | No career-path transition or scenario engine. |
| Skill intelligence | PARTIALLY IMPLEMENTED | USA/India descriptive skill prevalence/associations; no sourced multi-market skill taxonomy or causal basis. |
| Demand intelligence | PARTIALLY IMPLEMENTED | Existing posting-derived skill/role statistics and research; no multi-market source-backed time series. |
| Product market selector | PARTIALLY IMPLEMENTED | Current India/USA switcher. |
| Market explorer/salary/skill transparency | PARTIALLY IMPLEMENTED | Current pages exist, but source/vintage/definition transparency is incomplete and browser verification not performed. |
| Monitoring, evaluation, drift | EXISTS BUT NOT VERIFIED | Historical docs/tests and artifact hashes exist; no live monitoring or current deployed evaluation checked. |
| Versioned API | NOT IMPLEMENTED | `/api` prefix exists but no explicit version namespace such as `/v1`. |

No planned feature has been described as existing. Data-source findings and readiness limits are detailed in `M0_MARKET_DATA_FEASIBILITY.md`.
