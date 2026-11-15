# Sprint 2 Phase 2B — Final Corrective Security Test Report

**Execution date:** 2026-11-12
**Runtime:** Windows, Python 3.13.9

## Final completed test commands

| Exact command | Result |
|---|---|
| `python -m pytest -q --basetemp data/processed/.pytest-tmp tests/test_uk_salary_service.py` | **49 passed in 8.63s.** Includes current local manifest/artifact checks; future synthetic lifecycle acceptance; source-reference, provenance, checksum, archive, transformation, approval timestamp/use/identity/state validation. |
| `python -m pytest -q --basetemp data/processed/.pytest-tmp tests/test_uk_salary_api.py` | **31 passed in 5.40s.** Run with approved local-socket access. Exercises all five real dependencies, blocked-state matrix against all five routes, no service construction on denial, live revocation, and five successful isolated synthetic API routes. |
| `python -m pytest -q --basetemp data/processed/.pytest-tmp tests/test_golden_predictions.py tests/test_prediction_parity.py tests/test_archetype_parity.py` | **30 passed in 4.53s.** Existing India/USA golden and parity files and assertions were unchanged. |
| `python -m pytest -q --basetemp data/processed/.pytest-tmp tests/test_ashe_ingestion.py tests/test_routing_contracts.py tests/test_schema_contracts.py tests/test_cloud_contracts.py tests/test_global_foundation.py` | **70 passed in 8.76s.** ASHE ingestion and Sprint 1 routing/schema/cloud/global contracts. Run with approved local-socket access. |
| `python -m pytest -vv --basetemp data/processed/.pytest-tmp tests/test_chart_contracts.py tests/test_end_to_end_integration.py tests/test_input_validation.py tests/test_market_analytics.py tests/test_skill_integrity.py tests/test_zero_storage_deployment.py` | **74 passed in 5.88s.** Existing India/USA API, chart, input, analytics, and deployment contracts. Run with approved local-socket access. |

These five disjoint commands completed **254 tests passed**. No test was skipped in these final runs.

## Failed, skipped, and unexecuted tests

- During test development, one service run had **1 failed / 48 passed** because a test expected a different stable internal error code for a rejected source-reference flag. The assertion was corrected to the emitted precise validation code; the final service run passed 49/49.
- An intermediate API run had **1 failed / 22 passed** because the isolated fixture represented a fully approved synthetic catalog but expected `NOT_PUBLISHED`. The fixture's live catalog and manifest are both approved in that isolated test, so the correct context is `PUBLISHED`; the expectation was corrected and the final API run passed 31/31.
- No tests were skipped in the final commands. The actual ignored ASHE manifest and processed dataset were present and inspected.
- A monolithic all-tests invocation was **not rerun** for this patch. The previous Phase 2B report records that it stalled during collection at `collecting ...` for over 90 seconds. No monolithic full-suite pass is claimed.
- No tests were blocked by environment restrictions; TestClient commands used approved local-socket access.

## Publication gate evidence

The API test's default-state case uses the actual current registry and ignored manifest, not a dependency override. All five paths return 503 with `UK_DATA_NOT_PUBLISHED`; a factory that raises if called confirms the service is not loaded, and responses contain no observation fields or salary values.

An additional FastAPI `TestClient` smoke used the real `src.backend.main:app` entry point and normal lifespan with the unmodified live catalog/manifest. Startup verified 10/10 model artifacts. The five actual HTTP results were:

| Route | Result |
|---|---|
| `/api/v1/markets/UK/salary/occupations` | 503 `UK_DATA_NOT_PUBLISHED` |
| `/api/v1/markets/UK/salary/occupations/1001` | 503 `UK_DATA_NOT_PUBLISHED` |
| `/api/v1/markets/UK/salary/occupations/1001/regions` | 503 `UK_DATA_NOT_PUBLISHED` |
| `/api/v1/markets/UK/salary/regions/East/occupations` | 503 `UK_DATA_NOT_PUBLISHED` |
| `/api/v1/markets/UK/salary/metadata` | 503 `UK_DATA_NOT_PUBLISHED` |

The smoke command used this Python payload through PowerShell's stdin pipe:

```powershell
@'
from fastapi.testclient import TestClient
from src.backend.main import app
paths = [
    '/api/v1/markets/UK/salary/occupations',
    '/api/v1/markets/UK/salary/occupations/1001',
    '/api/v1/markets/UK/salary/occupations/1001/regions',
    '/api/v1/markets/UK/salary/regions/East/occupations',
    '/api/v1/markets/UK/salary/metadata',
]
with TestClient(app) as client:
    for path in paths:
        response=client.get(path)
        print(path, response.status_code, response.json().get('detail',{}).get('code'))
'@ | python -
```

The isolated failure matrix requests every one of the five routes for each blocked state: review-required/local manifest, not-collected catalog, approved catalog with local manifest, source URL mismatch, manifest/approval checksum mismatch, actual processed-file checksum mismatch, missing/incomplete approval, wrong approved use, false URL-match flag, wrong approval source ID, invalid timestamp, source ID mismatch, missing reference metadata, geography mismatch, period mismatch, missing/malformed manifest, and missing source entry. Each returns 503 without service factory calls.

The synthetic pass case calls the real `require_uk_publication` dependency with a temporary matching dataset, manifest, and approved synthetic catalog. The API success tests use the same real dependency and temporary artifacts. They do not override the dependency. A revocation test first loads the service, then changes the live catalog status and confirms the next request returns 503 without another service call. This verifies that approval status is not cached.

The service test accepts a local artifact while reporting `NOT_PUBLISHED`, accepts a coherent synthetic publication artifact for integrity while the live catalog remains unapproved and still reports `NOT_PUBLISHED`, and rejects mismatched data/catalog references, manifest/provenance references, false publication match flags, invalid checksums, and incomplete approvals.

## Model integrity and governance checks

- All 9 India/USA model artifacts in the artifact manifest matched their recorded SHA-256 values.
- All 5 model/feature metadata files checked matched their recorded SHA-256 values.
- India/USA golden, prediction parity, archetype parity, endpoint, and deployment tests passed as listed above.
- The current manifest remains `LOCAL_PREPARATION_ONLY`, `publication_eligible: false`, and `source_reuse_review_status: REVIEW_REQUIRED`; it has no publication approval object. Its SHA-256 is `C58B143BCA23849B5BCE762E42677AEE5A41FB2715A40D2054CA6059206FC95E`.
- The processed CSV remains SHA-256 `DEC9D305603FBF2B843D250B8CDD08317896F4331668122FBF3484AD35B15A2E`.
- Live source catalog remains `REVIEW_REQUIRED` / `NOT_COLLECTED`. All UK capabilities remain `NOT_IMPLEMENTED`.

The [official ONS Table 15 page](https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/regionbyoccupation4digitsoc2010ashetable15) lists the 2025 revised edition and a newer 2026 provisional edition, and links to OGL v3.0. The source catalog's alternate URL is unresolved; its UK-wide/2026 geography/period metadata also disagrees with the 2025 Great Britain artifact. ONS public access/licence information is not an approval record for this intended display. These discrepancies remain publication blockers.

No deployment, source approval, public release, or Phase 2C work was performed.
