# Sprint 2 Phase 1.1–1.2 — ASHE Table 15 Verification

**Verification date:** 2026-11-10  
**Status (updated in Phase 1.2):** The initial Phase 1.1 workbook inspection was blocked by network restrictions. Phase 1.2 successfully retrieved and inspected the latest clearly released revised edition, **ASHE 2025 revised**. The 2026 provisional Table 15 release status remains unresolved because its page still carries the table-specific delay notice.  
**Recommendation:** **NO-GO for a public UK-wide salary release remains in force.** The workbook supports a limited, explicitly Great Britain regional descriptive workflow, but it has no UK/Northern Ireland total rows and high suppression for detailed annual earnings. Keep source status `REVIEW_REQUIRED`; implementation and public release still require approval.

## 1. Exact dataset and workbook identity

The selected source is the ONS dataset **“Earnings and hours worked, region by occupation by four-digit SOC: ASHE Table 15”**, dataset ID **ASHE: Table 15**. The official page describes annual estimates of paid hours and weekly, hourly and annual earnings for UK employees, by sex, full-/part-time, region and four-digit SOC.

| Edition shown by ONS | Listed archive | Listed size | Finding as of 2026-11-10 |
|---|---|---:|---|
| 2026 provisional | `ashetable152026provisional.zip` at `https://www.ons.gov.uk/file?uri=%2Femploymentandlabourmarket%2Fpeopleinwork%2Fearningsandworkinghours%2Fdatasets%2Fregionbyoccupation4digitsoc2010ashetable15%2F2026provisional%2Fashetable152026provisional.zip` | 64.3 MB | Listed on the dataset landing page, but the same page carries a 22 October 2026 notice saying publication of **this table** was delayed for processing and additional quality assurance, and would be made available within three weeks. The 2026 ASHE bulletin itself was released on 22 October. The table-specific conflict is unresolved; the page does not establish that this exact Table 15 package is ready for use. |
| 2025 revised | `ashetable152025revised.zip` at `https://www.ons.gov.uk/file?uri=%2Femploymentandlabourmarket%2Fpeopleinwork%2Fearningsandworkinghours%2Fdatasets%2Fregionbyoccupation4digitsoc2010ashetable15%2F2025revised%2Fashetable152025revised.zip` | ONS page: 64.0 MB; downloaded file: 67,137,692 bytes | **Retrieved and inspected.** This is the latest clearly released revised Table 15 edition. The 2026 bulletin identifies 2025 revised results as released 22 October 2026; the 2026 Table 15 delay notice remains on the dataset page. |

The 2025 revised ZIP contains 44 XLSX workbooks: 22 files in the companion `Table 15 (3)` set and 22 in `Table 15 (4)`, each set comprising 11 estimate workbooks and 11 matching coefficient-of-variation (CV) workbooks. The `Table 15 (4)` filenames identify `Work Region Occupation SOC20` and the four-digit unit-group set selected for this inspection. One workbook contains separate data sheets for employee groups; it is not a single CSV-shaped table.

### Retrieval, origin and integrity

- Official download URL used: `https://www.ons.gov.uk/file?uri=%2Femploymentandlabourmarket%2Fpeopleinwork%2Fearningsandworkinghours%2Fdatasets%2Fregionbyoccupation4digitsoc2010ashetable15%2F2025revised%2Fashetable152025revised.zip`.
- Download command: `Invoke-WebRequest -Uri '<official URL above>' -OutFile $zipPath -TimeoutSec 180`; result was HTTP-successful. A separate `HEAD` request returned status `200`, `Content-Type: application/zip; charset=utf-8`.
- Local archive: `E:\Job Market\data\raw\ashe_table15_2025_revised\ashetable152025revised.zip`; size `67,137,692` bytes; SHA-256 `AC1202E9C48E80BF0EE4F8C35BF869ADE6A72540F88F44E1E91C0F32564B2CF3`.
- `zipfile.is_zipfile` returned true and `ZipFile.testzip()` returned no corrupt member. The archive was extracted to the sibling `extracted/` directory (44 XLSX files) under `data/raw/`, which `.gitignore` excludes. No raw dataset file is tracked or committed. ONS did not expose a publisher checksum in the page/HTTP metadata; the checksum above is locally computed.
- The prior Phase 1.1 attempts were unable to fetch ZIP content due DNS restrictions and the web viewer's unsupported ZIP MIME type. Phase 1.2 used a network-enabled shell and resolved that access limitation.

Therefore, the latest edition listed is 2026 provisional, but the latest clearly released **revised** Table 15 edition and the latest edition verified as usable for this analysis is **2025 revised**. The 2026 provisional package remains unresolved until ONS clarifies the table-specific delay notice and its contents are independently inspected.

## 2. Official source references

- [ONS ASHE Table 15 dataset page](https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/regionbyoccupation4digitsoc2010ashetable15) — dataset identity, listed editions/archives, correction and delay notices, and OGL v3.0 footer.
- [Employee earnings in the UK: 2026 bulletin](https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/bulletins/annualsurveyofhoursandearnings/2026) — provisional status, reference date, population/method, definitions and occupational coding change.
- [ASHE methodology and guidance](https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/methodologies/annualsurveyofhoursandearningsashemethodologyandguidance) — ASHE variable family and population scope.
- [Guide to interpreting ASHE estimates](https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/methodologies/guidetointerpretingannualsurveyofhoursandearningsasheestimates) — gross pay, sample coverage and pay-component definitions. This page is last revised 26 October 2017, so newer bulletin/table notes take precedence where applicable.
- [ONS terms and conditions](https://www.ons.gov.uk/help/terms-conditions) and [ONS licensing page](https://www.ons.gov.uk/methodology/geography/licences/) — general ONS reuse terms and attribution/third-party caveats.
- [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/) — permission scope, attribution conditions and exclusions.
- [SOC 2020 overview](https://www.ons.gov.uk/methodology/classificationsandstandards/standardoccupationalclassificationsoc/soc2020) — current UK SOC and official volumes.
- [ONS relationship between SOC 2010 and SOC 2020](https://www.ons.gov.uk/methodology/classificationsandstandards/standardoccupationalclassificationsoc/soc2020/therelationshipbetweenstandardoccupationalclassification2010andstandardoccupationalclassification2020) — official dual-coded relationship analysis and downloadable correspondence tables.

## 3. Workbook structure, headers and classification

| Question | Verification result |
|---|---|
| Internal workbook filename / file format | Verified from extracted archive; each selected file is XLSX. For example: `Work Region Occupation SOC20 (4) Table 15.7a Annual pay - Gross 2025.xlsx` and matching `.7b ... CV.xlsx`. |
| Worksheets and sheet dimensions | Estimate workbook: `Notes` `A1:Z68`; data tabs `All`, `Male`, `Female`, `Full-Time`, `Part-Time`, `Male Full-Time`, `Male Part-Time`, `Female Full-Time`, `Female Part-Time`, each `A1:Y4542` or `A1:Y4543` depending on measure. CV workbook has `CV notes` (`A1:Z21`) and the same nine data tabs/dimensions. |
| Headers and workbook metadata | Annual gross sheet header row: `Description`, `Code`, number of jobs (thousand), median, annual percentage change, mean, annual percentage change, and percentiles 10, 20, 25, 30, 40, 60, 70, 75, 80 and 90. Row 1 identifies Table 15, the measure, employee group, currency marker and reference year. Workbook Notes tab contains definitions, coverage, quality thresholds and suppression conventions. |
| Geographic / occupation fields | `Description` combines work-region label and occupation title; `Code` stores the SOC occupation code as text (leading apostrophe in Excel). There is no separate region-code field in the inspected table. |
| Exact codes / classification version | The selected `(4)` estimate workbook is explicitly named `SOC20`; its `Code` column contains 412 distinct four-digit unit-group codes. The complete set exactly matches the 412 unit groups in the official ONS SOC 2020 structure workbook downloaded for comparison. No source code was relabelled. |
| Landing-page taxonomy clue | The page slug contains `4digitsoc2010`; it is stale/misleading for the 2025 revised workbook. The workbook itself uses SOC 2020, independently verified against the official SOC 2020 structure. |
| Official bulletin evidence | ONS says SOC 2020 has been used in ASHE from the **2021 revised estimates** and warns that the SOC 2010→SOC 2020 change creates a time-series break; those bases are not directly comparable. This agrees with the workbook's own `SOC20` identifier and exact code-set match. |

**Classification conclusion:** the selected 2025 revised four-digit files represent **SOC 2020**. The code comparison used ONS’s official workbook `soc2020volume1structureanddescriptionofunitgroupsexcel20260827.xlsx` (289,135 bytes; SHA-256 `B9E3E464B877418EF1258AB4CB9E3B0FFE43EE9FD418D872068C2749B2337DE3`), extracted from the official SOC 2020 Volume 1 page. ASHE unique four-digit codes: 412; official SOC 2020 unit-group codes: 412; ASHE codes absent from official list: 0; official codes absent from ASHE set: 0; exact set match: true. This validates code membership, not any mapping to a different taxonomy. The separate `Table 15 (3)` workbook family is not used in the four-digit comparison.

### SOC 2010↔SOC 2020 correspondence

An official ONS relationship guide and July 2021 XLSX correspondence tables exist at major, sub-major, minor and unit-group levels. They are based on dual-coded Labour Force Survey data from 2014–2016 and an economically active 1% sample of the 2011 Census for England and Wales. ONS states these relationships indicate likely correspondence, are limited by coding methodology/source error, and are a guide to relationships users may find in their own data. The guide says a perfect correspondence exists only when 100% of cases go to a single destination; its example also demonstrates a SOC 2010 occupation splitting across SOC 2020 groups.

This is **not a universally valid deterministic one-to-one crosswalk for every occupation code or an ASHE-specific reclassification**. It is potentially useful as documented, directional, empirical correspondence evidence, with one-to-many ambiguity and coverage limitations. Do not remap a Table 15 salary cell to SOC 2020 unless the exact source code, direction, evidence, and policy are represented. Safer initial treatment: serve the selected edition in its source classification; if dual-series comparison is needed, retain source SOC and surface correspondence as uncertain evidence rather than silently relabeling it.

## 4. Measures, population and reference period

### What official documentation establishes

Workbook inspection confirms the measure inventory and statistic fields shown below. The general ASHE methodology's variable list matches the 11 individual Table 15 estimate files in this archive.

The 2026 bulletin reports 2026 estimates as provisional, based on the pay period including **22 April 2026**; 2025 revised estimates relate to the pay period including **30 April 2025**. The reference date moves within April according to the survey calendar. Do not substitute download/publication date for pay reference period.

ASHE measures employer-reported actual payments and paid hours for employee jobs. The workbook Notes specify a 1% sample of jobs selected from HMRC PAYE records; multiple-job holders may be represented more than once. It excludes self-employed people and employees not paid in the reference period. Hourly/weekly estimates cover adult-rate employees whose pay was unaffected by absence; annual estimates are for adult-rate employees in the same job for more than one year.

ASHE earnings are gross before income tax, National Insurance and other deductions, and exclude payments in kind. Weekly/hourly estimates generally refer to the survey pay period (not annualized) and exclude arrears relating to another period. Annual pay is a separate measure: the 2026 bulletin says annual pay covers employees in the job for at least a year and includes pay affected by absence, so annual and weekly/hourly figures are not directly comparable. Full-time means more than 30 paid hours/week (25 or more for teaching); part-time is at/below the corresponding thresholds.

The selected workbook is work-region by occupation, as shown in its filenames and data descriptions. Its 4-digit region dimension is the 11 labels listed above. It does not provide a region identifier code separate from the descriptive label. Pay amounts are denominated in GBP (the workbook titles show £); no currency conversion is required or performed.

### Exact Table 15 measure inventory

The 4-digit ZIP contains estimate (`a`) and CV (`b`) workbooks for each of these source-labelled measures:

| Table | Workbook measure | Period / meaning from workbook label and Notes |
|---|---|---|
| 15.1 | Weekly pay — Gross | Gross pay for April reference pay period |
| 15.2 | Weekly pay — Excluding overtime | Weekly gross-pay basis excluding overtime |
| 15.3 | Basic pay — Including other pay | Basic pay including other pay, per ASHE component definition |
| 15.4 | Overtime pay | Overtime pay component |
| 15.5 | Hourly pay — Gross | Gross hourly pay for April reference pay period |
| 15.6 | Hourly pay — Excluding overtime | Hourly pay excluding overtime |
| 15.7 | Annual pay — Gross | Gross annual earnings for the tax year ending 5 April 2025; same job for over one year |
| 15.8 | Annual pay — Incentive | Annual incentive-pay component |
| 15.9 | Paid hours worked — Total | Total paid hours |
| 15.10 | Paid hours worked — Basic | Basic paid hours |
| 15.11 | Paid hours worked — Overtime | Paid overtime hours |

The annual gross sample header confirms the statistic fields: median, annual percentage change for median, mean, annual percentage change for mean, then percentiles 10, 20, 25, 30, 40, 60, 70, 75, 80 and 90. Sex and work-pattern filters are separate tabs; no automatic conversion combines these measures. Workbook Notes says job counts (in thousands) are indicative only and should not be treated as reliable estimates.

## 5. Provisional, suppression and missing-value evidence

- 2026 ASHE estimates are provisional; the bulletin says final 2026 data is expected in October 2027 under the annual revision policy. Any release using it must label the edition provisional and support replacement/revision provenance.
- The Table 15 page has a 22 October 2026 table-specific publication-delay/extra-QA notice for the 2026 provisional edition. The 2025 revised workbook itself was downloadable and passed ZIP integrity checking; its inspection resolves the workbook blocker for the revised 2025 edition, not the status of 2026 provisional.
- The landing-page 19 December 2025 correction notice concerns the 2025 **provisional** edition and says certain SOC occupations/areas were suppressed pending review for the revised 2025 release. The revised workbook was inspected. It does not include that notice as a cell-level annotation; maintain the correction notice as provenance and check the revised values for affected groups before public display.
- Workbook Notes/CV Notes define the cell markers as follows: `x` = estimate is suppressed because its CV is above 20%; `..` = estimate is suppressed for disclosure reasons; `:` = not applicable; `-` = nil or negligible; and `.` in CV sheets = unavailable. Blank cells occur but are not defined by the workbook legend, so they remain a distinct unknown/unavailable state.
- CV quality bands are: CV ≤5% (precise), >5–10% (reasonably precise), >10–20% (acceptable), and >20% (unreliable for practical purposes). Estimates can also be suppressed to avoid disclosure. CVs for annual percentage changes are unavailable.
- Inspection count for `Table 15.7a Annual pay - Gross`, `Full-Time`, `Median`: 4,532 region/unit-group cells (412 unit groups × 11 work regions); 1,339 numeric, 2,818 `x`, and 375 blank. Among the 1,339 reported numeric cells, their matching CVs fall into 134 at ≤5%, 502 at >5–10%, and 703 at >10–20%. This is a representative completeness/quality check; it does not authorize filling suppressed or blank cells.
- Numeric-value checks across the `All` sheets for gross weekly pay (15.1a), overtime pay (15.4a), gross annual pay (15.7a), and annual incentive pay (15.8a) found no zero, negative, or non-finite values in the gross weekly or gross annual measures. Overtime had 934 zero values among 1,022 numeric cells; annual incentive had 624 zero values among 708 numeric cells. Those component zeros are valid nil component observations, not zero salary estimates. No rejected/source contents or individual-level records were copied into this report.
- Never parse an unavailable/suppressed marker or an undefined blank as zero. Preserve source status explicitly. No imputation is defensible.
- ASHE 2020–2021 estimates carry additional uncertainty due to pandemic collection impacts; a 2021 occupational coding change is a time-series break. There are also bulletin-noted methodology changes affecting comparability of 2023 onward with 2022 and earlier. Any multi-year chart must account for those breaks and must not combine occupational classifications silently.

## 6. Licensing assessment by intended activity

### Evidence

The exact Table 15 landing page footer says its content is available under **Open Government Licence v3.0 except where otherwise stated**. ONS terms say most website content is under OGL and some content is exempt; ONS specifically warns that third-party material is not covered. The OGL v3.0 grants worldwide, royalty-free, perpetual, non-exclusive permission to copy, publish, distribute, transmit, adapt, and use commercially/non-commercially, subject to the licence conditions. It excludes personal data, material not made available through publication/disclosure, logos/crests/Royal Arms (subject to the stated document-integral exception), and rights the provider is not authorized to license. Users must provide the specified attribution (or the default attribution) and, where possible, link the licence; users may not imply endorsement or misrepresent the information.

### Activity-by-activity assessment

| Intended activity | OGL evidence-based assessment | Conditions / remaining caveat |
|---|---|---|
| Temporary local download/storage for inspection | **PERMITTED CONDITIONALLY** for the published ONS information covered by the page’s OGL notice; OGL expressly permits copying. | Downloaded only into ignored `data/raw/`; archive and extracted workbooks remain local and untracked. Confirm no contrary workbook notice/third-party content before later redistribution. |
| Local storage for reproducible transformation | **PERMITTED CONDITIONALLY**; copying/adaptation are in the granted rights. | Keep raw asset protected and ignored; record exact edition/checksum; source status remains `REVIEW_REQUIRED` until project-level review/approval. |
| Transformation / normalization / derived statistics | **PERMITTED CONDITIONALLY**; OGL expressly allows adapting and combining information. | Keep source meaning, definition and provisional status; no unsupported inference or misrepresentation. Do not present aggregate sample statistics as individual-level observations. |
| Public dashboard display of source-derived aggregates | **PERMITTED CONDITIONALLY**; OGL permits publishing/distributing and using information in a product/application. | Display ONS source attribution and links to source/OGL; label edition and GB work-region coverage; preserve suppression, quality and population caveats; do not imply ONS endorsement. |
| Academic/research publication | **PERMITTED CONDITIONALLY** under OGL copy/adapt/publish permissions. | Attribute ONS and cite edition/reference period; follow publication requirements; no implied endorsement; distinguish direct statistics from derived analysis. |
| Republishing the raw workbook or substantial source tables | **PERMITTED CONDITIONALLY under OGL** based on the exact dataset page statement and inspected Notes tabs. | Still review every file-specific exception/third-party component before broad redistribution; preserve attribution and license link. The application does not need to expose raw workbooks. |

**Licensing decision:** the published Table 15 dataset page explicitly applies OGL v3.0 except where otherwise stated, and the retrieved archive’s Notes/CV Notes contained no different licence or third-party copyright notice. OGL supports local copying, transformation, derived statistics, dashboard publication and academic publication with required attribution and caveats, subject to personal-data, third-party-rights, logos and other OGL exclusions. ASHE table data inspected is aggregate, not person-level records. This evidence supports those uses conditionally; it does not itself approve JobIntel implementation, and the project source-catalog status remains `REVIEW_REQUIRED`. This is a technical licensing assessment, not legal advice.

Suggested attribution, subject to any more specific workbook statement: “Source: Office for National Statistics, Annual Survey of Hours and Earnings, ASHE Table 15, [edition/reference period], licensed under the Open Government Licence v3.0.” Link to the source dataset and [OGL v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).

## 7. Technical and analytical suitability

The workbook is suitable for **limited descriptive analysis of published aggregate observations**, not prediction or individual salary inference. It has the needed median/mean/percentile and quality measures, with exact SOC 2020 unit groups. A defensible narrowly scoped candidate is 2025 revised full-time median gross annual pay by four-digit SOC 2020 and work region, showing only published numeric values and carrying CV/suppression and coverage states.

The coverage is too incomplete for a product presented as complete UK-wide occupation pay: the four-digit work-region table has 11 named areas (England, Scotland and Wales), no Northern Ireland row and no UK-total row; only 1,339 of 4,532 full-time annual gross median region/occupation cells are published numeric values, while 2,818 are marked unreliable/suppressed and 375 are blank. This sparsity can still support a constrained GB-only explorer if gaps are visible and no totals are inferred, but it does not support an unqualified national UK salary overview. Annual and weekly/hourly measures must remain separate. Never fabricate missing cells, infer quantiles from means, convert periods without an explicit method, mix SOC 2010/2020, or treat ASHE aggregates as training rows. Label provisional data and preserve edition/reference period.

## 8. Unresolved items and required next evidence

1. **2026 provisional edition status remains unresolved:** ONS still lists the 2026 provisional archive while retaining the 22 October 2026 table-specific delay notice. Confirm with a refreshed page or the Earnings team before relying on that edition. The 2025 revised workbook is the latest clearly released revised edition and was inspected.
2. **Blank-cell interpretation:** the Notes key defines `x`, `..`, `:`, `-`, and CV-sheet `.`, but not every blank in the data sheets. Preserve blanks distinctly and do not convert them to zero.
3. **2025 correction cells:** the page correction notice says affected 2025 provisional SOC 3312/331/33 estimates were to be reviewed for revised release. The revised workbook does not repeat that notice as cell annotations; inspect these code/region cells against ONS correction material before exposing them.
4. **Geographic scope:** the selected four-digit “Work Region” data contains 11 regions and no Northern Ireland or UK-total row. A GB-only product label and scope would be required; a UK-total calculation is unsupported.
5. **Data coverage:** only 1,339/4,532 full-time annual gross median cells are numeric; 2,818 are x and 375 are blank. This materially limits occupation-region coverage and must be reflected in product decisions.
6. **Licensing review status:** ONS page and OGL evidence supports the intended activities conditionally, but project source status remains `REVIEW_REQUIRED` until owner review records the exact asset and intended public use. No source registry status was changed.
7. **Operational exposure:** raw archive and extracted workbooks remain local under ignored `data/raw/`. Do not bundle, publish, or expose them via an API before separate approval.

## 9. Final recommendation

### **NO-GO for public UK-wide salary release; verification of the 2025 revised workbook is complete.**

The 2025 revised four-digit workbook is an official aggregate salary source with SOC 2020 codes that exactly match the current official 412-unit-group structure. Its source-reported measures and CV tabs support careful descriptive analysis. OGL v3.0 evidence covers conditional local storage, transformation, derived statistics, dashboard display and academic publication with attribution, subject to its exclusions. The SOC 2010↔SOC 2020 correspondence materials remain empirical guidance, not a deterministic relabeling rule.

The inspection blocker for 2025 revised is resolved, but the Phase 1 NO-GO remains: the file does not provide complete UK geography and suppresses or omits most detailed full-time annual median cells. A future **GB-only, observed-cells-only** descriptive product may be technically defensible if it preserves definitions/CVs/missingness and receives explicit source/use approval. Do not present it as UK-wide, infer national totals, relabel codes, expose raw workbooks, or change source status to `APPROVED` based on this report alone. No application code, frontend, models, dependencies, or deployment configuration were modified; no data was committed.
