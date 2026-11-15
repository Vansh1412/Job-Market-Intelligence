# M0 Model and Artifact Inventory

## Current registered models

**VERIFIED FROM SOURCE CODE and configuration:** `src/backend/models/model_registry.py` declares 10 entries: 9 required model/preprocessing objects and 1 optional India cohort. The separate JSON manifest lists 19 entries, including runtime metadata and optional research cohorts. The startup log expects 10 verified items in older terminology; actual registry `EXPECTED_HASHES` has 10 keys including the optional India cohort. Mandatory registry keys load USA salary model, USA metadata preprocessor, USA archetype scaler/PCA/KMeans; India salary model, India preprocessor, India archetype PCA/KMeans. Feature/model metadata JSON is loaded as files but not all are hash entries in the Python `EXPECTED_HASHES` dictionary; the JSON manifest contains them.

| Market | Model/role | Artifact | Model type / contract | Runtime |
|---|---|---|---|---|
| India | Salary | `models/india/final_model.pkl` | `HistGradientBoostingRegressor`; prediction applies inverse log transform in `IndiaService` | Required |
| India | Preprocessor | `models/india/final_preprocessor.pkl` | fitted `ColumnTransformer`; transforms 290 raw fields into 327 columns per feature metadata | Required |
| India | PCA/archetypes | `models/india/india_pca_v1.pkl`, `india_kmeans_v1.pkl` | centered 15-component PCA, KMeans 6 clusters | Required |
| USA | Salary | `models/phase5/best_model.pkl` | tuned XGBoost regressor; 123 model features | Required |
| USA | Preprocessor | `models/phase5/best_pipeline.pkl` | custom `MetadataTransformer`; emits categorical one-hot features plus remote and skill count | Required |
| USA | Archetypes | `models/scaler_phase4_1.pkl`, `pca_phase4_1.pkl`, `kmeans_phase4_1_k7.pkl` | mean-center scaler, 15-component PCA, KMeans 7 clusters | Required |

Exact current sizes, hashes, metadata, optional dataset entries, and legacy model assets are in `M0_ARTIFACT_INTEGRITY_MANIFEST.md`. Every digest matched. The JSON manifest’s `size_bytes` fields are not reliable at this checkout: multiple values disagree with actual bytes despite matching hashes. No serialization was loaded by the audit hash pass. Model source and training transform code were reviewed before the project’s test run, which exercises models.

## Feature/model metadata

- India: `models/india/final_feature_list.json` records `feature_count_raw: 290` and `feature_count_transformed: 327`; `final_model_metadata.json` says model type `HistGradientBoostingRegressor`, feature count 290 (ambiguous raw/model-facing wording). `IndiaService` transforms the 290-column DataFrame before `predict`; actual estimator expects transformed input. Test verifies exact metadata raw count but does not independently assert 327 live transform width.
- USA: `models/phase5/feature_metadata.json` reports `n_features: 123`, 82 technical skills, and metadata columns; live `USAService` concatenates metadata transformer output and the skill array. XGB estimator is described as tuned in the metadata and registry.
- USA artifacts additionally present outside runtime registry: `models/pca_phase4.pkl`, `kmeans_phase4_k7.pkl`, `scaler_phase4.pkl`; these are legacy/phase-4 lineage. They should not be confused with the runtime `_phase4_1` clustering assets.
- India `india_holdout_archetype_pipeline.pkl` and `india_kmeans_v1.pkl` coexist; the registry loads the latter plus PCA and `ArchetypeService` handles the pipeline/metadata relationship. Exact call path merits follow-up for lifecycle cleanup.

## Artifact loading and verification

`ModelRegistry.verify_all_artifacts()` computes SHA-256; required missing files raise; optional cohorts may be unmounted unless `JOBINTEL_STRICT_RESEARCH` is enabled. Only after verification are pickles loaded. Registry singleton initializes on startup and route access. `artifact_manifest.json` is a separate manifest; it lists more files than Python registry’s hard-coded expected-hash table, so the two sources of truth can drift. **Verified source concern.**

## Limitations

Artifact hashes prove exact bytes against checked-in constants; they do not establish provenance, safety of pickles from other sources, predictor calibration, or current deployed artifact identity. Live Render state was not inspected. Private cohorts are listed by path/size/hash only and not opened or copied here.

