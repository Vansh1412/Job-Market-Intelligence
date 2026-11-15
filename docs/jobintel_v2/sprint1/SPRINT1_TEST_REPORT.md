# Sprint 1 Test Report

Run on 2026-11-10 from `E:/Job Market` using Python 3.13.9, FastAPI 0.111.0, Starlette 0.37.2, httpx 0.28.1, and pytest 8.4.2.

## Test commands and results

| Exact command | Result |
|---|---|
| `python -m pytest tests/test_global_foundation.py -q` | **26 passed** in 2.04s. Includes schemas, registries, finite-positive salary validation, stable issue codes/no rejected-value echo, capability-to-route assertions, and `/api/v1` route/404 contracts. |
| `python -m pytest tests/test_routing_contracts.py tests/test_schema_contracts.py tests/test_cloud_contracts.py -v` | **17 passed** in 1.90s. Includes existing routes, India/USA schemas, 290/123 feature counts, market isolation, and artifact checks. |
| `python -m pytest tests/test_golden_predictions.py::test_usa_golden_predictions_parity -vv` | **1 passed** in 1.66s. |
| `python -m pytest tests/test_golden_predictions.py::test_india_golden_predictions_parity -vv` | **1 passed** in 3.28s. |
| `python -m pytest tests/test_golden_predictions.py tests/test_prediction_parity.py -v` | **15 passed** in 3.83s, including both golden tests and the existing India/USA API, health, metadata, parity, fallback, and isolation tests. Run with local loopback permission enabled. |
| `python -m compileall -q src/backend/schemas src/backend/markets src/backend/data_catalog src/backend/employers src/backend/routers/v1.py` | Passed; no syntax errors. |

## Application startup and HTTP verification

Started the actual application with its normal lifespan using:

```text
python -m uvicorn src.backend.main:app --host 127.0.0.1 --port 8765 --log-level info
```

Startup logged artifact synchronization **19/19 verified**, registry status **GREEN**, and model artifact verification **10/10**. The process then logged application startup complete.

Using Python `urllib.request` against `http://127.0.0.1:8765`, these real HTTP requests completed:

| Request | Status and validation |
|---|---|
| `GET /api/v1/markets` | 200; five items validated as `list[MarketConfig]`. |
| `GET /api/v1/markets/UK` | 200; validated as `MarketConfig`, market `UK`, currency `GBP`. |
| `GET /api/v1/sources` | 200; eleven items validated as `list[DataSource]`. |
| `GET /api/v1/sources/uk.ons.ashe` | 200; validated as `DataSource`, reuse `REVIEW_REQUIRED`, validation `NOT_COLLECTED`. |
| `GET /api/v1/employers` | 200; empty list validated as `list[EmployerProfile]`. |
| `GET /api/v1/employers/unknown-company` | 404; `{"detail":"Employer not found"}`. |
| `GET /api/v1/markets/XX` | 404; `{"detail":"Market not found"}`. |
| `GET /api/v1/sources/unknown.source` | 404; `{"detail":"Source not found"}`. |

All six endpoint responses serialized to JSON and validated against their Pydantic response models. The production India and USA prediction routes were also exercised over this live local server for all golden profiles; all six requests returned HTTP 200.

Representative successful response bodies (list examples show one returned item):

```text
GET /api/v1/markets -> 200
{"market_id":"IN","display_name":"India","iso_country_code":"IN","primary_currency":"INR","capabilities":{"salary_prediction":"AVAILABLE","salary_analytics":"AVAILABLE","skills_analytics":"AVAILABLE","demand_analytics":"PARTIAL","occupation_mapping":"NOT_IMPLEMENTED","employer_intelligence":"NOT_IMPLEMENTED"},"data_availability":"AVAILABLE","source_ids":["in.jobintel.market-data"],"last_successful_update":null}

GET /api/v1/markets/UK -> 200
{"market_id":"UK","display_name":"United Kingdom","iso_country_code":"GB","primary_currency":"GBP","capabilities":{"salary_prediction":"NOT_IMPLEMENTED","salary_analytics":"NOT_IMPLEMENTED","skills_analytics":"NOT_IMPLEMENTED","demand_analytics":"NOT_IMPLEMENTED","occupation_mapping":"NOT_IMPLEMENTED","employer_intelligence":"NOT_IMPLEMENTED"},"data_availability":"NOT_IMPLEMENTED","source_ids":["uk.ons.ashe","uk.ons.labour-demand","uk.ons.soc2020"],"last_successful_update":null}

GET /api/v1/sources -> 200
{"source_id":"in.jobintel.market-data","source_name":"JobIntel India market data","source_organization":"JobIntel","source_reference":"https://github.com/Vansh1412/Job-Market-Intelligence","source_category":"EXISTING_PROJECT_DATA","reuse_review_status":"UNKNOWN","geographic_coverage":["India"],"collected_at":null,"validation_status":"NOT_COLLECTED"}

GET /api/v1/sources/uk.ons.ashe -> 200
{"source_id":"uk.ons.ashe","source_name":"Annual Survey of Hours and Earnings","source_organization":"Office for National Statistics","reuse_review_status":"REVIEW_REQUIRED","update_frequency":"Annual","reference_period":"2026","collected_at":null,"validation_status":"NOT_COLLECTED"}

GET /api/v1/employers -> 200
[]

GET /api/v1/employers/unknown-company -> 404
{"detail":"Employer not found"}
```

## Prediction parity

Golden comparisons below use the existing test tolerances, direct frozen-model predictions, expected manifest values, and archetype assertions. No golden value, assertion, or artifact was changed.

| Profile | Market | HTTP prediction | Direct-model difference | Manifest difference | Result |
|---|---|---:|---:|---:|---|
| `USA_GOLDEN_01_ML_AI` | USA | $256,960.28 | $0.001250 | $0.000000 | Pass; direct tolerance `< $0.10`, manifest tolerance `< $0.50`. |
| `USA_GOLDEN_02_BACKEND` | USA | $161,140.12 | $0.005000 | $0.000000 | Pass. |
| `USA_GOLDEN_03_CLOUD_DATA` | USA | $206,508.61 | $0.000625 | $0.000000 | Pass. |
| `IND_GOLDEN_01_PYTHON_AI` | India | 16.6200 LPA | 0.003080 LPA | 0.000000 LPA | Pass; both tolerances `< 0.05 LPA`. |
| `IND_GOLDEN_02_JAVA_MICROSERVICES` | India | 9.3500 LPA | 0.004119 LPA | 0.000000 LPA | Pass. |
| `IND_GOLDEN_03_DATA_ENGINEERING` | India | 17.2100 LPA | 0.002504 LPA | 0.000000 LPA | Pass. |

## Capability verification

Direct calls to existing services/handlers succeeded for India/USA salary prediction, market-summary analytics, and skills analytics (**6/6**). Responses were checked by result shape without printing market datasets or analytics payloads. Salary predictions loaded through the model registry, which verified all 10 registered artifacts.

## Environment diagnosis

Without local-loopback permission, `TestClient` stalled at the API request. A faulthandler run of the USA golden test located it at `client.post("/api/usa/predict")` in `tests/test_golden_predictions.py:45`; the model load and direct prediction precede that line. The independently run India test showed the same stall at `client.post("/api/india/predict")` in line 86 after model loading and direct prediction. Both stacks blocked inside AnyIO’s Windows asyncio backend while Python attempted `_fallback_socketpair()` for the Proactor event loop. A minimal FastAPI app exhibited the same issue. The same Python runtime with local loopback permission enabled completed the TestClient suites and the actual Uvicorn/HTTP checks. This was a sandbox network restriction; no application or test workaround was added.

## Artifact and Git audit

- Parsed `docs/jobintel_v2/m0/M0_ARTIFACT_INTEGRITY_MANIFEST.md` and recalculated SHA-256 for all **20 model-directory files** listed there: all 20 matched the audited digest.
- `git diff --quiet -- models` and `git diff --cached --quiet -- models` both passed; no staged or unstaged model changes.
- Runtime startup independently verified 19/19 synchronized artifacts and 10/10 model registry artifacts.
- `git diff --check` passed. A text-file scan found no trailing whitespace in Sprint 1 Python/Markdown files.
- No dependency, deployment, frontend, credential, private dataset, or generated model file was added or changed. All newly untracked Sprint 1 files are source, tests, or Markdown documentation.
- Git contains one modified tracked file and 21 new Sprint 1 files. The 18 pre-existing untracked M0 audit files remain untouched.

No acceptance verification remains blocked. No frontend build was run because frontend files were not modified.
