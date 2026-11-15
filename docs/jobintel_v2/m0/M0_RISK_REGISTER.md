# M0 Risk Register

Likelihood/severity are qualitative audit judgments. Validation tests are proposed future work, not tests run in M0.

| Risk | Severity / likelihood | Evidence and impact | Mitigation | Validation test |
|---|---|---|---|---|
| Breaking existing India/USA inference | Critical / Medium | Independent schemas, feature pipelines, separate model artifacts. Could break current production. | Additive adapters; preserve old routes and golden outputs; canary rollout. | Golden prediction parity on frozen profiles, contract tests. |
| Feature contract drift | High / Medium | India raw 290 vs transformed 327 distinction; metadata count semantics ambiguous; registry and manifests duplicated. | Version input/transform schemas, generate manifest from one source, assert model input names/shapes. | Exact raw/order/output checks in CI and artifact load test. |
| Occupation mapping errors | High / High | ANZSCO/OSCA/SOC/SSOC version changes; current role labels are custom. | Versioned many-to-many crosswalk + confidence and review queue; preserve originals. | Gold-coded job-title benchmark, inter-rater audit, low-confidence rejection. |
| Salary definition mismatch | Critical / High | India LPA midpoint; USA annual base; new official sources include weekly total cash / annual gross / monthly basic+gross. | Store native definitions, population, period; annualize only with explicit observed hours; label gross/basic. | Definition/unit property tests and independent sample cases. |
| FX conversion errors | High / Medium | Current cross-market intentionally native currency; future comparisons need rates and dates. | Keep local currency as primary; explicit timestamped FX source, rate type and conversion date if enabled. | Known-date FX fixtures and round-trip tolerances. |
| Leakage / non-generalizing predictions | Critical / Medium | Existing reports describe leakage controls, not independently reproduced for all markets. New aggregate data unlikely to support row-level ML. | Market-specific evaluation, temporal/group splits, feature governance; do not imply causation. | Leakage audit and held-out temporal evaluation. |
| Sparse/suppressed official estimates | High / High | Region × occupation cells may have low precision or suppression. | Retain quality flags and sample counts; suppress unreliable comparisons rather than impute silently. | Suppression/precision threshold tests. |
| Unsupported skill/demand claims | High / Medium | Existing skill associations are observational; JSA IVI covers only selected boards; SG vacancy reports vary in granularity. | Separate associations from effects; document channel/source coverage and timeframe. | Claim-to-source checks and cohort support floors. |
| Private data exposure | Critical / Medium | Large ignored row-level data exist locally; Docker copies reports; static tracked aggregates exist. | Keep raw data outside frontend and Git; allowlist deploy artifacts; scan release tar/image. | CI tracked-file and built-image path audit. |
| Artifact integrity registry drift | High / Medium | All hashes match, but manifest size fields stale and Python registry differs from JSON manifest. | Single generated manifest; fail CI on hash AND size/schema mismatch; provenance/signing. | Integrity test over every required/optional artifact. |
| Render memory/cold-start limits | High / Medium | Free-service config one worker; historical docs cite 512MB and ~310MB, not current measurement. | Measure current image/startup peak; lazy-load optional artifacts; define supported plan. | Render-like memory/startup test and cold-start SLO. |
| Vercel/API config drift | Medium / Medium | Two Vercel configs, runtime env unknown, origin route depends on build-time base URL. | Document root directory and env by environment; one source of truth. | Preview/prod smoke test for direct route and API origin. |
| Bundle/accessibility regressions | Medium / Medium | Build bundles include Recharts; no live mobile/a11y pass. | Set bundle budgets, lazy load heavy pages, WCAG review. | Bundle-size CI and automated + manual keyboard/screen-reader audits. |
| Classification/version drift | High / Medium | OSCA 2024 replaces Australian ANZSCO; UK SOC versions and SG SSOC 2024. | Store classification version and correspondence lineage. | Historical mapping regression fixtures. |
| Secrets exposure | Critical / Low-Medium | No tracked secret path found; path scan is not comprehensive. | CI secret scanner; never emit values in logs/docs. | Push-protection + secret scan of tracked and built files. |

## M1 approval gates

Approve (a) markets as descriptive-first versus prediction parity, (b) canonical occupation grain and mapping-confidence behavior, (c) salary definition/payout annualization rules, (d) licensing/redistribution and source-attribution policy, (e) native-currency comparison versus explicit FX conversion, and (f) launch quality thresholds and ownership.
