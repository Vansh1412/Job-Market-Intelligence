# ASHE 2025 Revised Table 15 — Data Quality Audit

**Audit date:** 2026-11-10  
**Decision scope:** Full-time annual gross pay medians, Table 15 (4), 2025 revised  
**Result:** The documented archive and headline coverage counts reproduce. The quality pattern is too sparse and uneven for a complete Great Britain occupation salary view; source-reported observations can only be displayed with strict missingness and CV caveats.

## Executive summary

- The local ONS archive hash matches the previously documented value. The extracted four-digit set contains 44 XLSX workbooks, and the estimate/CV workbooks agree on the same 4,532 occupation-region keys.
- The 4,532 median cells contain 1,339 numeric estimates (29.55%), 2,818 `x` suppressed estimates (62.18%), and 375 blanks (8.27%). These are three distinct states; blanks are not documented as suppression and neither state means zero.
- All 412 occupation codes match the official SOC 2020 unit-group list. Across the 11 GB regions, 190 occupations have no numeric cell, 34 have numeric cells in every region, and only 91 meet the audit’s comparison-screening threshold of at least 8 of 11 regions.
- Numeric estimates have reported CVs: 134 are ≤5%, 502 are >5–10%, and 703 are >10–20%. No numeric median has a missing/non-numeric CV in the paired CV workbook.
- The source workbook exposes percentile columns, but none of the 4,532 full-time annual gross occupation-region rows has a numeric value in any P10–P90 column. This measure therefore cannot support employee salary-distribution charts at this grain.

## Dataset and grain

| Item | Verified value |
|---|---|
| Archive | `data/raw/ashe_table15_2025_revised/ashetable152025revised.zip` |
| SHA-256 | `AC1202E9C48E80BF0EE4F8C35BF869ADE6A72540F88F44E1E91C0F32564B2CF3` (matches documented hash) |
| Extracted workbook count | 44 XLSX files under ignored `data/raw/` |
| Inspected estimate workbook | `Work Region Occupation SOC20 (4) Table 15.7a Annual pay - Gross 2025.xlsx` |
| Paired CV workbook | `Work Region Occupation SOC20 (4) Table 15.7b Annual pay - Gross 2025 CV.xlsx` |
| Worksheet | `Full-Time`; row 5 header; estimate and CV keyed by description-derived region and source occupation code |
| Grain | One work-region × four-digit SOC 2020 unit-group cell, 412 codes × 11 regions = 4,532 cells |
| Measure | Source-reported median gross annual pay; GBP; annual earnings for eligible adult-rate employees in the same job over one year; tax year ending 5 April 2025 |
| Population and caveats | Employee jobs sampled from HMRC PAYE; excludes self-employed and jobs not paid in the reference period. Multiple-job holders may contribute multiple jobs. See the Phase 1.2 verification report for the complete source definition. |

The 11 work-region labels are East, East Midlands, London, North East, North West, Scotland, South East, South West, Wales, West Midlands, and Yorkshire and The Humber. This is Great Britain coverage; the workbook has no Northern Ireland or UK-total row.

## Reproduction

The read-only audit script is [ashe_coverage_audit.py](</E:/Job Market/docs/jobintel_v2/sprint2/ashe_coverage_audit.py>). From the repository root, run:

```powershell
python docs/jobintel_v2/sprint2/ashe_coverage_audit.py
```

To retain the machine-readable audit output outside the repository:

```powershell
python docs/jobintel_v2/sprint2/ashe_coverage_audit.py > "$env:TEMP\ashe_coverage_audit.json"
```

The script uses the already installed Python 3.13.9 and `openpyxl 3.1.5`; it reads the ignored source workbook and the official SOC 2020 structure workbook, writes no output files, and adds no dependency. It hashes the archive, checks ZIP integrity, counts extracted XLSX files, checks unique `(region, code)` keys, aligns estimate and CV keys, joins codes to official SOC unit groups, classifies each median cell, and reports regional, occupation, and major-group coverage. The region-comparison screening threshold (≥8 numeric regions) and region-profile threshold (≥70% numeric occupation cells) are analyst-defined screens, not ONS rules.

Exact formulas: overall state share = state cell count ÷ 4,532 × 100; regional state share = regional state count ÷ 412 × 100; occupation support = count of regions with numeric median (out of 11); major-group share = numeric cells ÷ (unit groups in group × 11) × 100. Displayed percentages are rounded to two decimals overall and one decimal by region/group.

## Quality checks and results

| Check | Result | Assessment |
|---|---:|---|
| Documented archive SHA-256 match | Yes | Integrity matches prior verification |
| Extracted XLSX count | 44 | Expected archive contents |
| Archive ZIP integrity | `ZipFile.testzip()` returned `None` | No corrupt ZIP member found |
| Estimate/CV workbook keys | 4,532 each; identical sets | CV can be joined at the source cell grain |
| Duplicate region × occupation keys | 0 | Grain is unique |
| Source occupation codes | 412 unique | Exact match to 412 official SOC 2020 unit groups |
| Region labels | 11 | GB work regions only |
| Median cell states | 1,339 numeric; 2,818 `x`; 375 blank | 29.55% numeric, 62.18% `x`, 8.27% blank |
| Numeric median amount validity | 1,339 positive finite; 0 zero/negative; 0 non-finite | No invalid numeric amount found in this selected median column |
| Other median markers (`..`, `:`, `-`) | 0 | All observed median cells fall into the three states above |
| Numeric medians with numeric matching CV | 1,339 / 1,339 | Every numeric median has a paired numeric CV |
| Numeric percentile cells P10–P90 | 0 across 4,532 rows | No full-time annual gross percentile curve is available at this grain |

### CV quality among numeric medians

| Source CV band | Numeric median cells | Share of numeric medians |
|---|---:|---:|
| ≤5% | 134 | 10.0% |
| >5–10% | 502 | 37.5% |
| >10–20% | 703 | 52.5% |
| **Total** | **1,339** | **100.0%** |

The workbook describes CV >20% estimates as unreliable for practical purposes and suppresses them as `x`. Thus every published numeric median is below that suppression threshold, but more than half of numeric medians remain in the workbook’s least precise published band (>10–20%). A numeric value should not be read as exact or as evidence that two estimates differ statistically.

## Marker and missingness treatment

| Workbook value | Treatment in this audit |
|---|---|
| Numeric | Source-published estimate; display only with its exact measure and paired CV/quality band |
| `x` | Suppressed because CV >20%; not zero and not rankable |
| `..` | Disclosure suppression; not zero and not rankable |
| `:` | Not applicable |
| `-` | Nil or negligible, per the workbook key; keep distinct from numeric zero |
| Blank | Workbook does not define all blank cells; preserve as unknown/unavailable, distinct from `x` |
| CV value | Preserve numeric CV exactly; `x` remains the source’s >20% CV state; `.` or blank remains unavailable/unknown rather than zero |

In the selected median column, only numeric, `x`, and blank occur. The observed blank pattern is not assumed to share the `x` mechanism. The audit does not impute either state, infer blank causes, or expose underlying raw values.

## Impact on use

The suppression/missingness is material and not plausibly ignorable for a catalogue or comparison feature. The observed `x` is explicitly tied to poor precision (CV >20%); numeric-only coverage therefore selects estimates with better precision and likely larger/more stable samples. Coverage also varies strongly by geography and occupation. The available cells are consequently a selected subset, not a representative panel of all occupations and regions. The data does not establish whether suppressed salaries are higher or lower, so no directional salary bias is inferred.

This audit supports an observed-cell display with source CV and missingness states. It does not support silently complete region profiles, rankings of all occupations, employee-level inference, imputation, or any result that treats missing/suppressed cells as zero. Annual percentile distribution charts are not available in the selected full-time measure because all P10–P90 estimates are non-numeric in the inspected rows.

## Scope and limitations

- This is one edition and one measure/population tab: full-time annual gross pay median, 2025 revised. It is not a multi-year trend audit or an audit of every Table 15 measure/tab.
- Annual pay refers to tax year ending 5 April 2025; the measure and eligibility conditions are not interchangeable with weekly or hourly pay.
- The source is a survey estimate. CV bands describe relative precision; the audit does not calculate new confidence intervals or significance tests.
- The denominator 4,532 is the complete source grid of 412 unit groups × 11 work regions, not a count of independent persons. Job counts are marked indicative by ONS and are not used as denominators.
- The source catalog remains `REVIEW_REQUIRED`; this report is not an approval to expose data.

## Sources

- [ONS ASHE Table 15, 2025 revised edition](https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/regionbyoccupation4digitsoc2010ashetable15)
- [ONS SOC 2020 structure and descriptions](https://www.ons.gov.uk/methodology/classificationsandstandards/standardoccupationalclassificationsoc/soc2020/soc2020volume1structureanddescriptionsofunitgroups)
- [ASHE workbook and licensing verification](</E:/Job Market/docs/jobintel_v2/sprint2/SPRINT2_ASHE_VERIFICATION.md>)

## Phase 2A implementation confirmation (2026-11-10)

The read-only Phase 1.3 findings were reproduced by the new local ingestion pipeline. It verified the documented source archive SHA-256, ZIP integrity, all 44 extracted XLSX files, 412 SOC 2020 unit groups, the 412 × 11 = 4,532 unique occupation-region cells, and the same 1,339 numeric, 2,818 `x`-suppressed, and 375 blank median statuses. No raw workbook was modified. The processed CSV contains all 4,532 source cells with original median/CV state and provenance; it does not calculate a salary summary or impute unavailable values.

The processed CSV SHA-256 is `DEC9D305603FBF2B843D250B8CDD08317896F4331668122FBF3484AD35B15A2E`. The output is local-only and ignored, `publication_eligible` is false, and source reuse remains `REVIEW_REQUIRED`. The established licensing and statistical limitations above therefore still apply; pipeline validation does not expand reuse permission. See [SPRINT2_ASHE_PIPELINE_TEST_REPORT.md](</E:/Job Market/docs/jobintel_v2/sprint2/SPRINT2_ASHE_PIPELINE_TEST_REPORT.md>) for command-level evidence and the incomplete India/USA parity test status.
