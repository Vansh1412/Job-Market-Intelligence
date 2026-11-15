# ASHE 2025 Revised Table 15 — Great Britain Release Feasibility

**Assessment date:** 2026-11-10  
**Scope assessed:** Table 15 (4), full-time annual gross pay, 2025 revised, SOC 2020, GB work regions  
**Final decision:** **CONDITIONAL GO — only specified occupations, regions, and source-reported measures, subject to the restrictions below.**

## Decision

A narrowly scoped descriptive display is technically and statistically defensible **only as a display of the ONS-published full-time median gross annual pay estimate for an exact occupation-region cell where ONS provides a numeric estimate**, shown with its matching CV/quality band and complete provenance. It must make the missing cells visible and must not claim complete coverage of GB occupations or regions.

The 4,532-cell grid contains 1,339 numeric cells, 2,818 `x` quality suppressions and 375 blanks. Numeric coverage varies from 12.4% in North East to 43.2% in London. Of 412 unit groups, 190 have no numeric region cell, 91 have values in at least 8 regions, and only 34 have numeric values in all 11. This is too sparse and selected for broad occupation rankings, region scorecards, group-level salary summaries, or a claim to represent the full GB labour market.

**Permitted analytical shape if separately approved:** show a source cell’s point estimate, source-provided CV or CV band, exact source state for unavailable cells, edition, measure, population, SOC 2020 code, and work-region label. Cross-region juxtaposition can be limited to the 34 occupations with numeric medians in all 11 regions, with CV and non-significance caveats; it still describes only that selected subset. Single-region observed cells can be shown as source estimates but should not be used to imply omitted occupations have lower pay.

This is a feasibility decision, not authorization to publish or implementation approval. Public UK-wide release remains **NO-GO**. The source registry remains `REVIEW_REQUIRED`. No application or public data release was performed.

## Feasibility by proposed view

| Proposed view | Feasibility | Evidence and conditions |
|---|---|---|
| Individual occupation display | **Conditional** | 1,339 observed region/occupation medians can be displayed only as source-reported estimates with matched CV and region/edition context. 190 occupations have no numeric value in any region; never show blank or suppressed as zero or leave an omitted occupation looking like a measured low salary. |
| Regional comparison for a named occupation | **Conditional, narrow** | 34 occupations have a numeric median in all 11 work regions. Another 57 meet the audit screen of ≥8/11, but have 1–3 missing/suppressed regions. Label missing states and do not treat point-estimate differences as statistically significant. CVs range up to >10–20% for over half of numeric estimates. |
| Region-wide occupation comparison/profile | **Not defensible as complete** | No region meets the audit’s 70% numeric occupation coverage screen. Coverage ranges 12.4–43.2%; North East and Wales are particularly sparse. A region profile would omit most occupations and its omissions differ by region. |
| Occupation ranking | **No comprehensive ranking** | Suppression and blanks remove many occupation-region cells non-randomly; ranks among visible observations are rankings of a selected subset. ONS CVs also indicate substantial sampling uncertainty. Do not call any occupation “highest paid” or claim complete rank order. A clearly labelled exploratory sort of visible source values is possible only if it is not presented as a complete rank or a statistically tested difference; the recommended product omits it. |
| SOC major-group salary summaries | **Not supported by this table** | SOC structure supports classification into nine major groups, but Table 15 (4) provides unit-group medians. Averaging or weighting those medians does not produce a major-group employee median or mean. Indicative job counts are explicitly not reliable totals. Major-group coverage rates may be reported as coverage diagnostics only. |
| Salary distribution charts | **Not supported at this measure/grain** | Although the workbook has P10–P90 columns, the audit found zero numeric P10–P90 cells in all 4,532 full-time annual gross occupation-region rows. Do not create salary histograms or percentile curves from the distribution of occupation-level medians. |
| Trends or year-over-year comparisons | **Not assessed / unsupported by this slice** | The audited grid is one edition/reference period. Do not infer trends from it. Cross-edition comparisons need separately matched definitions, revisions, classifications, and the relevant time-series break checks. |

The ≥8/11 occupation screen and ≥70% region screen are transparent audit rules selected for this assessment; they are not ONS quality thresholds or guarantees of statistical significance.

## Comparison bias and uncertainty

The cell pattern is not missing completely at random: ONS defines `x` as CV >20%, so the published numeric subset is selected for estimates with better relative precision, while the suppression rate differs sharply by geography and occupation. This makes complete-case rankings, occupation profiles, and region comparisons compositionally uneven. Blank cells have no documented common cause and remain a separate state. The data does not justify claiming suppressed salaries are directionally higher or lower.

Of the 1,339 numeric medians, 134 have CV ≤5%, 502 have CV >5–10%, and 703 have CV >10–20%. The last group is over half of observed medians. CV bands are quality indicators, not confidence intervals for pairwise differences. Unless a suitable official inferential method and cell-level variance estimates are applied, show them descriptively and do not assert that an observed difference is meaningful or statistically significant.

## Data dictionary and transformation design

| Field | Definition / handling |
|---|---|
| Source edition | ASHE 2025 revised; archive SHA-256 `AC1202E9C48E80BF0EE4F8C35BF869ADE6A72540F88F44E1E91C0F32564B2CF3` |
| Source measure | Table 15.7a — Annual pay, Gross; statistic `Median`; full-time employee jobs; gross earnings before income tax, National Insurance and other deductions, excluding payments in kind |
| Amount / currency | GBP per year; retain the workbook’s numeric amount exactly, without annualizing or currency conversion |
| Pay period | Annual earnings for the tax year ending 5 April 2025; distinct from weekly/hourly reference-period pay |
| Population | Adult-rate employee jobs held for more than one year; annual pay can reflect absence effects. ASHE sample drawn from HMRC PAYE records; not self-employed people or employees not paid in the reference period; multiple-job holders may contribute multiple jobs |
| Occupation | Source four-digit SOC 2020 unit-group code and title; retain the original code and title; do not map or relabel to SOC 2010 |
| Geography | Source work-region label; eleven GB work regions, no Northern Ireland or UK total; preserve original description and derive region only as a traceable parsed field |
| Estimate value | Preserve the source cell verbatim/type; do not synthesize an estimate from any other statistic |
| CV and quality | Join the paired 15.7b CV workbook on exact region and SOC code; preserve numeric source CV, `x` (>20% CV), `.` (unavailable), and blank (undefined) states; preserve stated bands and do not replace them with a calculated uncertainty measure |
| Estimate state | `numeric`, `x` (CV >20% unreliable suppression), `..` (disclosure suppression), `:` (not applicable), `-` (nil/negligible), or `blank_unknown` (empty source cell, cause undefined). In the audited median column only `numeric`, `x`, and blank occur. |
| CV state | Preserve numeric CV versus source `.`/blank/unavailable; never treat unavailable CV as zero |
| Reference period | Fixed 2025 revised edition; store as edition/reference-period metadata, not download date |
| Provenance / attribution | Identify Office for National Statistics, ASHE Table 15, 2025 revised edition, measure, population, source URL, retrieval date/checksum, and Open Government Licence v3.0 link |

For a later approved transformation, retain raw workbook cells in the ignored local source area, keep a normalized row as an additional derived representation, and record every transformation. Do not overwrite or discard source strings, numeric precision, estimate markers, CVs, or original description. Do not annualize, convert currency, impute, fabricate suppressed values, calculate a new employee-level average/percentile from cell medians, or turn an indicative job count into weights.

## Licensing review by activity

The Table 15 landing page states its content is available under Open Government Licence v3.0 except where otherwise stated. OGL v3 permits copying, publishing, distributing, transmitting, adapting, and commercial/non-commercial use, subject to attribution and exclusions. ONS terms warn that some materials are exempt and third-party content may have separate rights. The inspected aggregate workbooks’ Notes/CV Notes showed no contrary licence notice in the prior workbook inspection. The source is aggregate statistical output, not person-level microdata.

| Activity | Assessment | Conditions |
|---|---|---|
| Local storage | **Permitted conditionally** | Published ONS content covered by the OGL notice may be copied. Keep raw archive local/ignored; retain edition, URL, checksum, and licence evidence; recheck any file-level exception before redistribution. |
| Transformation | **Permitted conditionally** | OGL allows adaptation. Preserve source values, population, reference period, SOC version, marker states, and CV meaning; do not imply ONS endorsement or misrepresent statistics. |
| Internal analysis | **Permitted conditionally** | Use published aggregate information with attribution and caveats; maintain provenance. Do not treat job counts as reliable weights. |
| Public dashboard display | **Permitted conditionally under OGL; not approved for this project yet** | Include ONS/source attribution and licence link; label 2025 revised / full-time annual gross median / SOC 2020 / GB work-region scope; show CV and unavailable states; avoid claims of completeness, significance, or endorsement; verify no third-party exception. |
| Derived statistics | **Permitted conditionally under OGL** | OGL allows adapting/combining, but derivations must be mathematically and statistically supported. Coverage percentages are defensible diagnostics; an average of occupation medians is not an employee-level group mean/median. |
| Academic publication | **Permitted conditionally** | Attribute the ONS source and exact edition/reference period; link OGL; preserve caveats and distinguish source estimates from analysis; comply with third-party rights and publication rules. |

Suggested attribution: “Source: Office for National Statistics, Annual Survey of Hours and Earnings, ASHE Table 15, 2025 revised, full-time annual gross pay, licensed under the Open Government Licence v3.0.” Link the dataset page and [OGL v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/). OGL evidence supports conditional reuse but does not itself update JobIntel’s source registry; that status remains `REVIEW_REQUIRED` pending owner review of the exact intended release and operational safeguards.

## Reproducibility and source references

Run the read-only calculation from the repository root:

```powershell
python docs/jobintel_v2/sprint2/ashe_coverage_audit.py
```

The script reproduces the archive hash, ZIP and extraction checks, SOC 2020 code comparison, source-cell state counts, CV bands, percentile availability, and region/occupation/major-group coverage. See the [data quality report](</E:/Job Market/docs/jobintel_v2/sprint2/SPRINT2_ASHE_DATA_QUALITY_REPORT.md>) and [coverage report](</E:/Job Market/docs/jobintel_v2/sprint2/SPRINT2_ASHE_COVERAGE_REPORT.md>) for the detailed results.

- [ONS ASHE Table 15](https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/regionbyoccupation4digitsoc2010ashetable15)
- [ONS ASHE 2026 bulletin](https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/bulletins/annualsurveyofhoursandearnings/2026)
- [ONS SOC 2020 unit-group structure](https://www.ons.gov.uk/methodology/classificationsandstandards/standardoccupationalclassificationsoc/soc2020/soc2020volume1structureanddescriptionsofunitgroups)
- [ONS terms and conditions](https://www.ons.gov.uk/help/terms-conditions)
- [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)
