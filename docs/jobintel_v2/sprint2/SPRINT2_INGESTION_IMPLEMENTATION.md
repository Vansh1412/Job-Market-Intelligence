# Sprint 2 Phase 2A — ASHE Data Engineering Implementation

**Status:** Local ASHE 2025 data preparation implemented and verified. The Phase 2A review corrected a stale runner/parser keyword mismatch; CLI reproducibility and tests passed after correction.  
**Release state:** Local preparation only; source reuse remains `REVIEW_REQUIRED`; no API or public display is enabled.  
**Transformation version:** `ashe-table15-2025r-v1.0.2`

## Scope and safeguards

This implementation parses only ONS ASHE Table 15 (4), 2025 revised, `Full-Time`, Table 15.7a gross annual pay median and its paired 15.7b CV. It prepares source aggregates, not employee-level salary rows. It does not add an API, frontend view, database, scheduler, or deployment change. No India/USA prediction files, model artifacts, feature contracts, or runtime routes were changed.

The command requires `--local-preparation-only`. It also checks that the registered ASHE reuse state is still `REVIEW_REQUIRED` and its catalog validation state is still `NOT_COLLECTED`. The generated manifest marks `publication_eligible: false`. These controls allow this specifically approved local data-engineering task without changing the source registry or treating an artifact validation result as reuse approval.

Raw archive and extracted workbooks were read only. The command verifies the archive checksum, ZIP integrity, exact 44-workbook extraction inventory, selected workbook bytes against their archive members, and the official SOC 2020 reference checksum before parsing. A checksum or input-set mismatch fails closed.

## Pipeline components

| File | Responsibility |
|---|---|
| `src/backend/ingestion/contracts.py` | Typed ASHE source-cell and run-manifest contracts; reuses Sprint 1 `DataProvenance`, `DataQualityResult`, `DataQualityIssue`, and `RejectedRow` types. |
| `src/backend/ingestion/ashe2025.py` | XLSX header/sheet validation, official SOC hierarchy loading, estimate/CV pairing, marker classification, redacted row issues, source-cell record creation, and SHA-256 helpers. |
| `src/backend/ingestion/runner.py` | Input-integrity gates, source-registry review gate, complete-grid validation, stable CSV serialization, manifest/report generation, checksum checks, and idempotent versioned output. |
| `src/backend/ingestion/__main__.py` | Offline CLI; requires explicit local-preparation acknowledgement and only prints artifact paths, checksums and redacted issue summaries. |
| `tests/test_ashe_ingestion.py` | Small synthetic XLSX fixtures plus an offline integration check against local ignored source files when present. |

The default command is:

```powershell
python -m src.backend.ingestion --local-preparation-only
```

Optional `--archive`, `--extracted-root`, `--soc-reference`, and `--output-root` arguments support explicit local paths. No network access is used by the command or tests.

## Source and output identity

| Asset | Filename / identifier | SHA-256 |
|---|---|---|
| Official ONS archive | `ashetable152025revised.zip` | `AC1202E9C48E80BF0EE4F8C35BF869ADE6A72540F88F44E1E91C0F32564B2CF3` |
| Selected estimate workbook | `Work Region Occupation SOC20 (4) Table 15.7a   Annual pay - Gross 2025.xlsx` | `670924CAA882B8D2723D812F0B03B0DD4A40B145EA00F07DD3F0C9A7619250AA` |
| Paired CV workbook | `Work Region Occupation SOC20 (4) Table 15.7b   Annual pay - Gross 2025 CV.xlsx` | `A4E18B88E39C8F7E47EAA7DDECE24FE6F8373332D2315CA76B575F7CC7B2C8EC` |
| Official SOC reference | `soc2020volume1structureanddescriptionofunitgroupsexcel20260827.xlsx` | `B9E3E464B877418EF1258AB4CB9E3B0FFE43EE9FD418D872068C2749B2337DE3` |

There are 44 extracted ASHE XLSX workbooks (46 ZIP members including directory entries). The selected estimate and CV workbook files match their bytes in the checksum-verified archive. The SOC reference contains 412 official unit groups and is separately checksum-pinned.

The resulting local-only run is `ashe25r-ac1202e9c48e80bf-ashe-table15-2025r-v1.0.2`. It records UTC ingestion time `2026-11-10T08:39:36.904641Z`, the exact tax-year reference period, source/cell definitions, SOC 2020, 11 GB work regions, source archive and workbook hashes, source attribution, transformation version, and validation results. Run ID is deterministic from the source checksum and transform version. The CSV is byte-stable; manifest time is run metadata and remains unchanged on an idempotent rerun.

## Local artifacts

All artifacts are under ignored `data/processed/`:

```text
data/processed/ashe_2025_revised/
  ashe25r-ac1202e9c48e80bf-ashe-table15-2025r-v1.0.2/
    ashe_2025_full_time_annual_gross_median_gb.csv
    provenance_manifest.json
    quality_report.md
```

Processed CSV SHA-256: `DEC9D305603FBF2B843D250B8CDD08317896F4331668122FBF3484AD35B15A2E`.

The CSV contains 4,532 source-cell rows: 1,339 numeric medians, 2,818 source `x` states, and 375 source blanks. It retains source median cells, paired CV cells, source descriptions and codes, official titles in a separate field, source measure/population/reference period, classification, geography, source IDs, and provenance. No missing value is imputed. No currency or period conversion, average of medians, percentile reconstruction, or region/major-group salary aggregation is performed.

The manifest uses the existing `DataProvenance` contract with `reference_period: "2025"` (the Sprint 1 contract accepts a year token); it separately records the exact source period `Tax year ending 5 April 2025`. `DataProvenance.validation_status: VALIDATED` describes these file/row checks only. The global source catalog remains `NOT_COLLECTED` and `REVIEW_REQUIRED` and is not mutated.

## Validation and failure behavior

- Required source files, SHA-256, ZIP integrity, archive member set, all extracted workbook paths, selected workbook byte identity, sheet, and exact headers are checked before output.
- The four-digit source code set must equal the official SOC 2020 unit-group set; the complete grid must contain the expected 412 codes × 11 regions with unique keys.
- Numeric estimates must be finite and >0. Reported values require a valid matching CV at or below 20%; quality-suppressed `x` values require a matching `x` or numeric CV above 20%. CVs must be finite and nonnegative when numeric.
- `x`, `..`, `:`, `-`, blank, and CV markers remain distinct. For the audited median column, only numeric, `x`, and blank occur. Five workbook footnote/footer rows are classified as non-data, not silently dropped; unexpected partial rows receive stable row-level issue codes.
- Any rejected data row, duplicate key, unexpected count/status, checksum mismatch, or missing region/code blocks artifact generation. Structured issues carry row index, stable code, field and generic message, never source-cell values or rejected descriptions.
- Output is written to a temporary sibling directory, checksum-checked, then renamed to the deterministic versioned directory. An identical rerun reuses existing files. A conflict is not overwritten.

## Dependency rationale

`openpyxl>=3.1.0,<4.0.0` is the only new dependency. The official source is XLSX, no XLSX parser was explicitly declared before this phase, and the previously installed environment copy was not a reproducible project dependency. `openpyxl` is needed to read the workbook sheets/cells, stream the large source safely, and generate fixture workbooks in offline tests. It introduces no paid service or infrastructure. No other dependency was added.

## Known source-catalog discrepancy

The canonical verified source reference used in the output is the official [ONS Table 15 page](https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/regionbyoccupation4digitsoc2010ashetable15). The pre-existing Sprint 1 `uk.ons.ashe` catalog entry contains a different URL (`...regionbyoccupation4digitsocashetable15`). The manifest records both references and `source_reference_matches_catalog: false`; the registry was deliberately not edited in this data-engineering phase. Reconcile that catalog metadata before a later API/source-catalog release. The source remains `REVIEW_REQUIRED`.

## Test evidence

See [SPRINT2_ASHE_PIPELINE_TEST_REPORT.md](</E:/Job Market/docs/jobintel_v2/sprint2/SPRINT2_ASHE_PIPELINE_TEST_REPORT.md>) for exact test commands and results. The test suite includes local synthetic fixtures and, when the ignored source assets are available, an offline integration test that verifies the archive hash, 44 extracted files, 4,532-row grid, SOC code match, and status counts.

## Phase 2A review verification

The review compared every one of the 4,532 processed CSV rows to the corresponding source median and CV cells, occupation code/description, and region in the selected estimate and CV workbooks. All row-level comparisons and metadata checks matched; the processed CSV SHA-256 matches the provenance manifest. The pipeline CLI was rerun twice after the review correction and reused the same versioned output and checksum each time.

The first review rerun exposed a stale `ingested_at` keyword passed from `runner.py` to `parse_workbook_pair`, whose contract does not accept it. The unsupported argument was removed; ingestion time remains recorded in the run manifest. The post-correction CLI and 27-test ingestion suite passed. This is limited to the ASHE ingestion runner and does not change prediction behavior.

The USA golden test passed independently (1 passed), the India golden test passed independently (1 passed), and the combined golden plus parity suite passed (15 passed). The prior stall was traced with faulthandler to `TestClient`/AnyIO loopback socketpair creation under the sandbox. The exact same tests completed outside the socket-restricted sandbox. No prediction service, golden value, tolerance, model artifact, or feature contract was changed.

`openpyxl` 3.1.5 is installed and supports Python >=3.8, consistent with the repository Python >=3.11 requirement and the declared `openpyxl>=3.1.0,<4.0.0` range. There is no Python dependency lockfile; the existing frontend npm lockfile is unrelated. `pip check` found no openpyxl conflict; two unrelated environment conflicts are documented in the test report.
