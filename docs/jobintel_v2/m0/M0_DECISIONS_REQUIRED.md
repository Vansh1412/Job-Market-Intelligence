# M0 Decisions Required Before M1

The following are product and governance decisions. The audit does not select values on the owner’s behalf.

1. **Product scope per market:** Should Australia, UK and Singapore launch first as sourced descriptive intelligence, or is salary prediction a launch requirement? The available official starting sources reviewed support aggregates, not equivalent row-level predictive training data.
2. **Canonical occupation grain:** What is the canonical level (broad family, unit group, detailed occupation)? Accept many-to-many crosswalks and display mapping confidence, or hide uncertain mappings? Which ISCO version is the international backbone, if any?
3. **Classification versioning:** Adopt OSCA 2024 for Australia while retaining ANZSCO history, SOC 2020 for UK, SSOC 2024 for Singapore, and define how historical revisions are versioned.
4. **Salary contract:** Which measures are eligible for comparison: basic, gross, total cash, annual base? Define population (residents/all employees, full-time/all), reference period, salary range treatment, and whether annualization from hourly/weekly/monthly data is allowed.
5. **Currency and cost context:** Keep native currencies only (current design) or permit date-specific FX conversion? Do not present converted amounts as purchasing power; PPP/cost-of-living is a separate decision.
6. **Source use and licensing:** Approve reuse, attribution, storage, display, derived aggregate, model-training, and refresh terms per source. Public access is not blanket ML or redistribution permission.
7. **Demand semantics:** Decide whether to publish postings, survey vacancies, official shortage lists, and modelled employment projections as distinct named signals; do not combine them into a single score without approved method.
8. **Evidence bar for skills/scenarios:** Decide minimum sample size, uncertainty, temporal holdout, mapping-confidence floor, claim language, and whether causal scenarios are out of scope until causal evidence exists.
9. **Freshness and support policy:** Set refresh cadence, stale-data behavior, update notification, and what happens when a source withdraws or suppresses cells.
10. **API compatibility:** Keep existing unversioned `/api` and root aliases during an announced compatibility period while adding `/api/v1`, or choose another migration policy.
11. **Operational budget:** Approve acceptable Render plan, memory/startup limits, ingestion storage, monitoring, and paid data costs if the current free architecture cannot meet targets.
12. **Launch gates and owners:** Assign sign-off owners for source/legal review, taxonomy QA, scientific validation, privacy, security, frontend accessibility, and production release.

M1 can start only after the user explicitly reviews M0 and approves the next milestone, as specified in the request. This document records decisions needed; it does not request or assume approval now.
