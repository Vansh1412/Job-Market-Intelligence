# JOBINTEL 2.0 — M0 Executive Summary

Audit snapshot: 2026-11-03 (workspace time Asia/Calcutta). Scope: working tree at `master`, HEAD `198b79d`. Evidence labels are used throughout: **VERIFIED FROM SOURCE CODE**, **VERIFIED FROM CONFIGURATION**, **VERIFIED BY EXECUTED TEST**, **VERIFIED FROM OFFICIAL SOURCE**, **INFERRED**, **NOT VERIFIED**, **REQUIRES USER DECISION**.

## Conclusion

The repository is a two-market product with India and USA salary prediction, market statistics, skill exploration, archetypes, and a cross-market summary. This is **VERIFIED FROM SOURCE CODE** in `frontend/src/App.tsx`, the 11 FastAPI routers, market services, and the model registry. Australia, UK, and Singapore are not registered in the app or backend; five-market support is **NOT IMPLEMENTED**.

The tree was clean at audit start: branch `master`, HEAD `198b79d`, tracking `origin/master`, no staged, unstaged, or untracked changes. **VERIFIED FROM GIT**. The M0 documents created in this directory are the only intentional workspace additions.

All model/artifact SHA-256 values listed in the registry and JSON manifest match local files. **VERIFIED BY EXECUTED HASH CHECK**. Multiple `size_bytes` values in the JSON manifest do not match current file sizes, including required model artifacts. No hash mismatch was found. The manifest records optional private cohorts as optional; those ignored files are locally present. No row-level data was copied into these documents.

The 290 India and 123 USA claims are supported, with a key distinction: India has 290 raw features and 327 transformed features; USA has 123 model inputs (41 metadata outputs + 82 binary skills). The two contracts are market-specific and not interchangeable. **VERIFIED FROM SOURCE CODE and model metadata**.

Backend CI’s code-only subset passed (17/17). Frontend build and lint completed successfully; lint emitted warnings. Vitest failed before executing tests because fork workers timed out. Full pytest did not complete collection within the audit window; the CI subset did. Details are in `M0_TEST_BASELINE.md`.

## Current posture and M0 limits

- Production services are configured for Render and Vercel. Live deployment health and deployed environment values were not checked: **NOT VERIFIED**.
- Source datasets are ignored locally; Git has no tracked Parquet files or `data/` files. **VERIFIED FROM GIT**. Workspace contains private/raw files, including row-level datasets; no private rows or contents were included here.
- Data-source feasibility for the three new markets is research-backed but does not establish redistribution permission or predictive-ML suitability.
- No product code, artifacts, dependencies, manifests, lockfiles, CI/deployment files, or environment configuration were changed. No commit, push, or deployment was made.

## Immediate decisions before M1

Approve the product role of predictions versus descriptive statistics; canonical occupation identity and mapping confidence; earnings definitions and annualization; data licensing/provenance policy; country launch gates; and whether cross-market analytics remain native-currency only or gain explicitly sourced FX conversion.

## Documents

See the remaining M0 reports in this directory. The audit is a readiness blueprint only. **M1 has not started.**

## M0 completion checklist

- [x] Git state inspected; start tree clean; no prior changes to overwrite.
- [x] Frontend routes inventoried; visual/mobile/accessibility behavior explicitly marked unverified where not rendered.
- [x] Backend route families and dual prefixes inventoried; request fields and known errors documented.
- [x] Model artifacts, metadata and hashes inventoried.
- [x] India/USA feature contracts and preprocessing relationship verified from source/metadata.
- [x] Data privacy, ignore patterns and tracked-file exposure checked.
- [x] Deployment configuration documented; live status marked not verified.
- [x] Test/build/lint baseline recorded with execution limitations.
- [x] Official starting-source feasibility reviewed for Australia, UK and Singapore.
- [x] Current and target architecture, risks, decisions and M1–M9 roadmap documented.
- [x] No production code, artifacts, dependencies, deployment settings, or Git history were modified.
- [x] No private row-level data or secret values were exposed in audit documentation.
- [ ] M1 approval — intentionally not granted or started.

## Deliverables

All 18 requested M0 documents are in this folder. These documents are new and are the only intentional tracked-workspace changes. Validation created ignored frontend build/cache output. No existing file was modified.
