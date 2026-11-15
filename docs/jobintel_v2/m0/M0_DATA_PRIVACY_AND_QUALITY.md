# M0 Data Privacy and Quality

## Dataset inventory and classification

Inventory is based on tracked paths, ignored-file paths/metadata, repository docs, and the runtime code’s data references. Raw rows were not opened or copied. Classification reflects evidence found, not legal advice or a license determination.

| Dataset family | Examples (relative paths) | Classification | Notes |
|---|---|---|---|
| Public/third-party USA job posts | `data/raw/dataset_A/data/jobs.csv`, `.parquet`; `data/raw/dataset_B/nextgig_jobs_2026-06.parquet`; ignored `jobs-tier1-L-2026-08-01/` | B — public/third-party; redistribution terms need continuing review | Local raw files are ignored; dataset A has `LICENSE.md`, README, datasheet and checksums. The directory name indicates a license tier but does not itself prove derivative/model display rights. |
| USA processed row-level cohort | `data/processed/cleaned_jobs.parquet`, `modeling_dataset.parquet`, `job_archetype_assignments*.parquet`, `skill_matrix*.parquet` | C — private/derived row-level | Ignored by Git; optional research artifacts in registry. Row-level records remain local and should not be published through static hosting. |
| India raw source | `data/raw/india/indian-job-market-dataset-2025.xlsx` | B/C — third-party/public source; exact license/distribution conditions require review | Ignored. M0 recorded file metadata only. |
| India processed postings/cohorts | `data/processed/india/cleaned_india_jobs.parquet`, `india_job_postings.parquet`, `india_job_skills.parquet`, `india_modeling_cohort.parquet`, `india_skill_pca.parquet`, archetype assignments | C — private/derived row-level | Ignored; manifest specifically identifies India cohort as optional research data. |
| Small source reference SQL/JSON | `data/raw/india_reference/*.sql`; `india_taxonomy.json`, `india_feature_schema.json` | E/D — reference or derived metadata | Local only where under ignored data paths; schemas/taxonomies can themselves encode project-derived mappings. |
| Published aggregates | tracked `reports/tables/{phase3,phase4_1,phase5,india}/*` and `reports/tables/india/india_skill_analytics.json` | D — derived aggregate | `.gitignore` explicitly whitelists selected reports. Aggregate status does not alone establish small-cell disclosure safety or source license compliance. |
| Frozen models | `models/**` | D — derived trained artifacts | Tracked; inspect feature metadata and licensing constraints before redistribution. No private rows embedded were assessed in M0. |

## Exposure and Git checks

**VERIFIED FROM GIT:** no tracked `.parquet`, no tracked files under `data/`, and no tracked private `.env` file. Explicit aggregate exceptions are present. `.gitignore` blocks `*.parquet`, raw/processed data, source directories, and tier dataset directories. `.dockerignore` also excludes data/raw, data/processed, Parquet, and tier datasets. Root Dockerfile nevertheless copies `reports/`, which includes selected aggregates and figures. Vercel is configured to serve only the frontend output directory; the Render config uses source/runtime code, not static raw data.

A root-level ignored Parquet (`nextgig_jobs_2026-06.parquet`, about 39.8 MB) and larger ignored source/processed datasets exist in workspace. `.gitignore` protects expected paths but not arbitrary secrets or non-Parquet row-level data placed elsewhere. No row-level private records were read, included, or emitted in this audit.

Tracked path-only screening found `.env.example` only among environment-file candidates and no credential/key/certificate filename. This is **not** a full secrets scanner. No secret values were printed.

## Quality/provenance observations

- Dataset selection and methodology are documented in `reports/dataset_selection.md`, `reports/license_compliance.md`, `reports/india_dataset_audit.md`, `reports/india_preprocessing.md`, and model reports. These are repository-authored assertions, not independent source verification.
- USA report describes 34,036 supervised observations and salary range USD 30k–600k; India metadata describes a 5,859-posting cohort, salary midpoint INR, LPA display. The live APIs expose salary currency/unit but source vintage in API payloads is limited.
- Current feature schemas differ by market; occupation categories are existing custom families. No unified occupation code, mapping confidence, dataset source registry, vintage freshness contract, or harmonized coverage/missingness endpoint was found.
- Duplicate processing, salary unit validation, temporal freshness, and geography coverage are documented in legacy reports but no ingestion/validation pipeline for three new markets exists.
- M0 did not re-read row-level data or re-run all dataset QA. The privacy status of third-party sources and ability to redistribute transformed outputs require product/legal review.
