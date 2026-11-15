# Sprint 2 Phase 2A — ASHE Pipeline Test Report

**Status:** Verification completed. USA and India golden tests and the combined parity suite passed in an approved run outside the socket-restricted sandbox. A Phase 2A runner call-site defect found during verification was corrected and rechecked.  
**Run ID:** `ashe25r-ac1202e9c48e80bf-ashe-table15-2025r-v1.0.2`  
**Source reuse:** `REVIEW_REQUIRED`; no publication or API is enabled.

## Commands and results

Commands below were run from the repository root (`E:\Job Market`) on 2026-11-10. The raw archive and processed outputs are in ignored `data/` paths.

| Command | Result |
|---|---|
| `python -m src.backend.ingestion --local-preparation-only` (twice after correction) | Both passed. Each reported 4,532 rows, identical run ID and CSV hash, and `reused_existing_output=True`. |
| `python -m pytest -q --basetemp data/processed/.pytest-tmp tests/test_ashe_ingestion.py` (post-correction) | **27 passed** in 22.38s. Includes synthetic workbook unit fixtures and the local ignored-source integration test. |
| `python -m pytest -q --basetemp data/processed/.pytest-tmp tests/test_routing_contracts.py tests/test_schema_contracts.py tests/test_cloud_contracts.py tests/test_global_foundation.py` | **43 passed** in 8.11s. This is the relevant existing contract/foundation subset; not the full backend CI suite. |
| `python -m compileall -q src/backend/ingestion tests/test_ashe_ingestion.py` | Passed; no syntax errors. |
| `python docs/jobintel_v2/sprint2/ashe_coverage_audit.py` | Passed. Its source archive, workbook grid, SOC code-set and status-count findings match the ingestion manifest. The audit emits a large detailed JSON report to stdout. |
| `Get-FileHash data/raw/ashe_table15_2025_revised/ashetable152025revised.zip -Algorithm SHA256` | `AC1202E9C48E80BF0EE4F8C35BF869ADE6A72540F88F44E1E91C0F32564B2CF3`, expected hash matches. |
| `Get-FileHash data/processed/ashe_2025_revised/ashe25r-ac1202e9c48e80bf-ashe-table15-2025r-v1.0.2/ashe_2025_full_time_annual_gross_median_gb.csv -Algorithm SHA256` | `DEC9D305603FBF2B843D250B8CDD08317896F4331668122FBF3484AD35B15A2E`. |
| `git diff --check` | Passed; no whitespace errors. Git emitted only line-ending conversion warnings for existing working-copy files. |

The earlier Phase 2A test run had reported a successful CLI, but this review independently reran the actual command and found a keyword mismatch. See the runner verification section below; the fixed CLI was then run twice and the ingestion suite rerun.

### Windows test transport diagnosis

The earlier stall was not model loading or inference. With `-o faulthandler_timeout=15`, the stack showed the golden test at `tests/test_golden_predictions.py:45`, inside HTTPX → Starlette `TestClient` → AnyIO `start_blocking_portal`; the AnyIO thread was blocked in `socket.accept` while `asyncio` created its loopback `socketpair`. The direct USA prediction had advanced to the API request. Both default Windows Proactor and an explicit `WindowsSelectorEventLoopPolicy` produced the same socketpair stall inside the sandbox.

The same Python 3.13.9 environment and unchanged test passed when run outside the restricted sandbox with local socket access approved. This establishes the cause as sandbox loopback socket access, not model loading, artifact access, or prediction execution. Python 3.11.9 was also present, but did not have the project XLSX dependency; WSL was denied (`Wsl/ E_ACCESSDENIED`) and Docker had no running daemon. Neither alternative runtime was needed after the approved local-socket run.

An initial direct `pytest` launcher attempt had also failed before test execution with Windows `Illegal System DLL Relocation`. `python -m pytest` works. The repository-local ignored `--basetemp data/processed/.pytest-tmp` avoids the separate sandbox temporary-directory problem.

## Reproduced source and quality counts

The pipeline independently verified the pinned archive SHA-256, ZIP integrity, all 44 extracted XLSX files against the archive member set, selected workbook bytes, and the official SOC 2020 reference code set.

| Check | Result |
|---|---:|
| Archive members | 46, including directory entries |
| Extracted workbook files | 44 |
| SOC 2020 unit-group codes matched | 412 / 412 |
| Work regions | 11 Great Britain regions |
| Unique occupation-region source cells | 4,532 |
| Numeric median observations (`REPORTED`) | 1,339 |
| Quality-suppressed `x` values | 2,818 |
| Blank values (`BLANK_UNKNOWN`) | 375 |
| Duplicate keys / rejected rows | 0 / 0 |
| Non-data footer rows recognized | 5 |
| Numeric percentile cells selected | 0 |

Status counts sum to 4,532. Numeric salaries are finite and positive; paired numeric CVs are valid and at most 20% for reportable medians. Suppressed and blank cells remain null with distinct statuses; no imputation or aggregation was performed.

## Artifact checksums

| Asset | SHA-256 |
|---|---|
| ONS source archive | `AC1202E9C48E80BF0EE4F8C35BF869ADE6A72540F88F44E1E91C0F32564B2CF3` |
| Estimate workbook 15.7a | `670924CAA882B8D2723D812F0B03B0DD4A40B145EA00F07DD3F0C9A7619250AA` |
| CV workbook 15.7b | `A4E18B88E39C8F7E47EAA7DDECE24FE6F8373332D2315CA76B575F7CC7B2C8EC` |
| SOC 2020 reference workbook | `B9E3E464B877418EF1258AB4CB9E3B0FFE43EE9FD418D872068C2749B2337DE3` |
| Processed CSV | `DEC9D305603FBF2B843D250B8CDD08317896F4331668122FBF3484AD35B15A2E` |

Raw and processed assets remain under ignored `data/`; neither is included as a tracked deliverable.

## Row-level processed-data integrity audit

The processed CSV was read independently and compared cell-by-cell against the `Full-Time` worksheet in the paired estimate and CV workbooks under `data/raw/ashe_table15_2025_revised/extracted/Table 15 (4)/`. The check covered **all 4,532** occupation-region cells, not only totals. For every row it compared region/code keys, original source description, occupation description, original source code, median value or marker, paired CV value or marker, and classification status. It also checked source ID, exact reference period, transformation version, archive hash, and each selected workbook hash against the manifest. All comparisons matched.

| Direct source example | Median cell | CV cell | Prepared status | Result |
|---|---:|---:|---|---|
| SOC 1150, North East — Managers and directors in retail and wholesale | 31133.8 | 13.8 | `REPORTED` | Exact numeric median and CV match |
| SOC 1111, North East — Chief executives and senior officials | `x` | `x` | `SUPPRESSED_QUALITY` | Markers retained; no salary value |
| SOC 1112, North East — Elected officers and representatives | blank | blank | `BLANK_UNKNOWN` | Blank retained distinctly; no salary value |

Output metadata checks confirmed `source_id=uk.ons.ashe`, reference period `Tax year ending 5 April 2025`, transformation `ashe-table15-2025r-v1.0.2`, SOC 2020, GB work-region labels, and `geography_code` unset because Table 15 does not provide a region code. The CSV SHA-256 matched the manifest: `DEC9D305603FBF2B843D250B8CDD08317896F4331668122FBF3484AD35B15A2E`. The current provenance manifest SHA-256 is `C58B143BCA23849B5BCE762E42677AEE5A41FB2715A40D2054CA6059206FC95E`.

## USA / India regression results

Commands were run with Python 3.13.9. The three passing commands below used approved unsandboxed execution because the sandbox blocks loopback socketpair creation. No assertion, tolerance, golden value, model, artifact, or prediction service was changed.

```powershell
python -m pytest -vv -s -o faulthandler_timeout=45 --basetemp data/processed/.pytest-tmp tests/test_golden_predictions.py::test_usa_golden_predictions_parity
```

Result: **1 passed in 5.31s**; app startup logged 10/10 model artifacts verified.

```powershell
python -m pytest -vv -s --basetemp data/processed/.pytest-tmp tests/test_golden_predictions.py::test_india_golden_predictions_parity
```

Result: **1 passed in 6.56s**; app startup logged 10/10 model artifacts verified.

```powershell
python -m pytest -vv -s --basetemp data/processed/.pytest-tmp tests/test_golden_predictions.py tests/test_prediction_parity.py
```

Result: **15 passed in 5.64s**, covering both golden tests, health/meta, four USA profiles, five India profiles, zero-skill fallback, and cross-market isolation. Existing assertions and tolerances passed unchanged.

## Dependency review

- Runtime: Python 3.13.9; repository requires Python >=3.11.
- Installed `openpyxl`: **3.1.5**, with package metadata `Requires-Python >=3.8`; compatible with the repository runtime and declared `openpyxl>=3.1.0,<4.0.0` range.
- `openpyxl` declares only `et-xmlfile` as a runtime dependency; `python -m pip check` reported no openpyxl/et-xmlfile conflict.
- `python -m pip check` exited **1** for unrelated environment conflicts: `pdflatex` requires `attrs<19.0` but 26.1.0 is installed; `spyder` requires `bcrypt>=4.3.0` but 4.0.1 is installed. Neither involves openpyxl or this project’s ASHE code.
- No Python lockfile was found. `frontend/package-lock.json` is the frontend npm lockfile and does not govern Python dependencies. No lockfile change was needed for consistency with the repository’s existing unpinned-range `requirements.txt` convention.

## Runner verification defect found and corrected

The initial review rerun of `python -m src.backend.ingestion --local-preparation-only` failed with `TypeError: parse_workbook_pair() got an unexpected keyword argument 'ingested_at'`. The runner passed a parameter absent from the parser contract. Removed that stale keyword at the call site in `src/backend/ingestion/runner.py`; ingestion time continues to be recorded by the run manifest. The CLI then passed twice, each time reporting 4,532 rows, the same CSV checksum and `reused_existing_output=True`; the post-correction 27-test ingestion suite passed. No row values or output format changed.

## Scope and remaining limits

- This is a local preparation pipeline only. `publication_eligible` is false and `uk.ons.ashe` remains `REVIEW_REQUIRED` / catalog validation `NOT_COLLECTED`.
- The source catalog URL differs from the canonical ONS URL recorded in the manifest. It was preserved and flagged; reconcile before any catalog/API release.
- The 43-test run is a targeted contract/foundation subset, not a full backend CI run.
- The 43-test run is a targeted contract/foundation subset, not the full backend CI suite.
- The raw source archive, extracted source workbooks, and processed CSV are ignored local data and must not be committed.

## Phase 2A file inventory and Git review

### Created for Phase 2A

- `src/backend/ingestion/__init__.py`
- `src/backend/ingestion/__main__.py`
- `src/backend/ingestion/ashe2025.py`
- `src/backend/ingestion/contracts.py`
- `src/backend/ingestion/runner.py`
- `tests/test_ashe_ingestion.py`
- `docs/jobintel_v2/sprint2/SPRINT2_INGESTION_IMPLEMENTATION.md`
- `docs/jobintel_v2/sprint2/SPRINT2_ASHE_PIPELINE_TEST_REPORT.md`
- `docs/jobintel_v2/sprint2/SPRINT2_ASHE_PROCESSED_DATA_DICTIONARY.md`

### Modified for Phase 2A

- `requirements.txt` — declares the single XLSX parser dependency, `openpyxl>=3.1.0,<4.0.0`.
- `src/backend/ingestion/runner.py` — during this review, removed a stale unsupported keyword argument to the workbook parser; no schema or transformation behavior changed.
- `docs/jobintel_v2/sprint2/SPRINT2_ASHE_DATA_QUALITY_REPORT.md` — appends reproduction evidence.
- `docs/jobintel_v2/sprint2/SPRINT2_INGESTION_DESIGN.md` — records the implemented state and parser rationale.

### Pre-existing working-tree files preserved

At task start, `src/backend/main.py` was already modified and the following groups were already untracked; they were preserved and not part of Phase 2A changes:

- `docs/jobintel_v2/m0/`: `M0_API_INVENTORY.md`, `M0_ARTIFACT_INTEGRITY_MANIFEST.md`, `M0_BACKEND_AUDIT.md`, `M0_CURRENT_ARCHITECTURE.md`, `M0_DATA_PRIVACY_AND_QUALITY.md`, `M0_DECISIONS_REQUIRED.md`, `M0_DEPLOYMENT_AUDIT.md`, `M0_EXECUTIVE_SUMMARY.md`, `M0_FEATURE_CONTRACT_AUDIT.md`, `M0_FRONTEND_AUDIT.md`, `M0_GAP_ANALYSIS.md`, `M0_IMPLEMENTATION_ROADMAP.md`, `M0_MARKET_DATA_FEASIBILITY.md`, `M0_MODEL_ARTIFACT_INVENTORY.md`, `M0_REPOSITORY_STATE.md`, `M0_RISK_REGISTER.md`, `M0_TARGET_ARCHITECTURE.md`, `M0_TEST_BASELINE.md`.
- `docs/jobintel_v2/sprint1/`: `SPRINT1_API_CONTRACTS.md`, `SPRINT1_ARCHITECTURE_DESIGN.md`, `SPRINT1_COMPLETION_REPORT.md`, `SPRINT1_DATA_DICTIONARY.md`, `SPRINT1_IMPLEMENTATION_PLAN.md`, `SPRINT1_REPOSITORY_AUDIT.md`, `SPRINT1_TEST_REPORT.md`.
- Pre-existing Sprint 2 files: `SPRINT2_API_CONTRACTS.md`, `SPRINT2_ARCHITECTURE_DESIGN.md`, `SPRINT2_ASHE_COVERAGE_REPORT.md`, `SPRINT2_ASHE_RELEASE_FEASIBILITY.md`, `SPRINT2_ASHE_VERIFICATION.md`, `SPRINT2_BASELINE_AUDIT.md`, `SPRINT2_COMPLETION_REPORT.md`, `SPRINT2_DATA_DICTIONARY.md`, `SPRINT2_DATA_QUALITY_REPORT.md`, `SPRINT2_EMPLOYER_INTELLIGENCE_DESIGN.md`, `SPRINT2_IMPLEMENTATION_PLAN.md`, `SPRINT2_SOURCE_FEASIBILITY.md`, `SPRINT2_TEST_REPORT.md`, and `ashe_coverage_audit.py`. The two modified Sprint 2 documents are listed in the previous section.
- Pre-existing Sprint 1 implementation files: `src/backend/data_catalog/{__init__.py,registry.py,validation.py}`, `src/backend/employers/{__init__.py,registry.py}`, `src/backend/markets/{__init__.py,registry.py}`, `src/backend/routers/v1.py`, `src/backend/schemas/{__init__.py,data.py,employer.py,market.py,salary.py}`, and `tests/test_global_foundation.py`.

Final `git status --short --untracked-files=all` returned **2 modified tracked paths and 64 untracked paths**. The tracked diff summary includes `requirements.txt` (3 added lines) and the pre-existing `src/backend/main.py` change (3 added lines). Git's normal diff/stat does not include untracked files; the complete Phase 2A deliverables and preserved baseline inventory are listed above. `git diff --check` passed. Both raw and processed data paths matched `.gitignore` and were confirmed ignored with `git check-ignore`; `git ls-files data` returned no paths. No model artifacts, feature contracts, frontend files, deployment settings, raw data, or processed data are in the Phase 2A source changes.
