# M0 Artifact Integrity Manifest

Computed 2026-11-03 using local SHA-256 and filesystem byte sizes. No serialized artifact was deserialized by this hash command. Runtime registry source (`src/backend/models/model_registry.py`) verifies hashes before loading. A matching digest proves byte identity against the checked-in expected value, not model quality or trustworthiness of the original producer.

| Registry/key | Relative path | Size (bytes) | SHA-256 | Market | Artifact role | Requirement | Registry size | Hash check |
|---|---|---:|---|---|---|---|---:|---|
| `india_salary_model` | `models/india/final_model.pkl` | 549969 | `7a3490d7a36a128eea5a70e80bb3550c504da69648ac368a891f8729282a8310` | India | model_artifact | mandatory production/runtime | 662561 | MATCH |
| `india_preprocessor` | `models/india/final_preprocessor.pkl` | 10527 | `0ee1dabf3130a19c8bbc80a31ab93d8e97affa4d4a688249d59ee336f7ab4ead` | India | model_artifact | mandatory production/runtime | 2574 | MATCH |
| `india_pca` | `models/india/india_pca_v1.pkl` | 37446 | `8591e3d3f713e35b27307e0c5810b35bb80ee33fd97bc909487985624e390897` | India | model_artifact | mandatory production/runtime | 34809 | MATCH |
| `india_kmeans` | `models/india/india_kmeans_v1.pkl` | 22617 | `4465a3d8c3b7ab92e668cab2b502bdc3ba832d8458545f00cc5121d9c73da40a` | India | model_artifact | mandatory production/runtime | 2842 | MATCH |
| `usa_salary_model` | `models/phase5/best_model.pkl` | 619464 | `55c1b7fd87d2a04c9761a1941fcc4f6d3174ed80a10ce0802b0c07fc644bfadd` | USA | model_artifact | mandatory production/runtime | 2605745 | MATCH |
| `usa_preprocessor` | `models/phase5/best_pipeline.pkl` | 3317 | `815fd9a3d88f2ebae82cebce86c6438d0455835de8de1bb8d66802f12a77be19` | USA | model_artifact | mandatory production/runtime | 8393 | MATCH |
| `usa_scaler` | `models/scaler_phase4_1.pkl` | 1161 | `2d969acd5b175979ac65a9ae5bf94f73ddd1bb7e3618528ab76706f16b00577c` | USA | model_artifact | mandatory production/runtime | 1842 | MATCH |
| `usa_pca` | `models/pca_phase4_1.pkl` | 6355 | `ef4ef56bdc4b9471b1ec636fb9c689744832992b13f9733549271a19e3ce83c0` | USA | model_artifact | mandatory production/runtime | 11264 | MATCH |
| `usa_kmeans` | `models/kmeans_phase4_1_k7.pkl` | 468479 | `4d6d2509f04502fdf088604151b66d2272a8b4de106ce9fa2f745f97806c0106` | USA | model_artifact | mandatory production/runtime | 2437 | MATCH |
| `india_cohort` | `data/processed/india/india_modeling_cohort.parquet` | 654351 | `d4e32be45d84b159804e1a019f44dd5da6682346e38f39635e8edcaac3a200ec` | India | optional_research_cohort | optional private research cohort | 654351 | MATCH |
| `usa_cohort` | `data/processed/modeling_dataset.parquet` | 1669405 | `68895e3823cca91ffbfea76b8986198700b4eb8bb02905bacc9a04985156a21b` | USA | optional_research_cohort | optional private research cohort | 1669405 | MATCH |
| `skill_matrix_technical` | `data/processed/skill_matrix_technical.parquet` | 5334250 | `91abf1d836de7e50e5bcdc64aa68dfcba0850af0550ce53f907ef547f391b406` | USA/India research | optional_research_cohort | optional private research cohort | 5334250 | MATCH |
| `job_archetype_assignments` | `data/processed/job_archetype_assignments.parquet` | 2725548 | `c4f2fb9353837087d198bb936c469875aab84361ecbce69bed4d3c19b639147c` | USA/India research | optional_research_cohort | optional private research cohort | 2725548 | MATCH |
| `india_skill_analytics` | `data/processed/india/india_skill_analytics.json` | 180164 | `805e33aeca78dfa7ce0c6da2ec2b04654e91c053ccaffd9e2219ca0c9c0378c5` | India | runtime_dataset | mandatory production/runtime | 180164 | MATCH |
| `india_final_feature_list` | `models/india/final_feature_list.json` | 15748 | `710aebaca840d4300a1e5f513fbe4826310abad9aa99e0547e63c0aabbef610e` | India | metadata | mandatory production/runtime | 15748 | MATCH |
| `india_final_model_metadata` | `models/india/final_model_metadata.json` | 8995 | `3e2aed92bee6a939295ac0d07fe4701856d079ea6f279952cb71b26565af3cb3` | India | metadata | mandatory production/runtime | 8995 | MATCH |
| `india_archetype_metadata` | `models/india/india_archetype_metadata.json` | 4494 | `e49c22b85111408d4e87e4a29cb1afc5e76d9ac0d97bbe3789cca9311a2f4cff` | India | metadata | mandatory production/runtime | 4494 | MATCH |
| `usa_feature_metadata` | `models/phase5/feature_metadata.json` | 5858 | `6f436976d2004b8b97934c7866ca7b3769cb938147d6a4ef1eea3a439dea7a5b` | USA | metadata | mandatory production/runtime | 5858 | MATCH |
| `usa_model_metrics` | `models/phase5/model_metrics.json` | 3051 | `06f372ff9cfde71890f5ef2be9ecafeceea6bc50ef503f173ee13124301b52c3` | USA | metadata | mandatory production/runtime | 3051 | MATCH |
| `experiment_registry` | `models/india/experiment_registry.json` | 42377 | `42d1d28344e930e0706f7e0cf0f9721f893330bec0529badb92d5ca8116224a4` | India | experiment metadata | optional research/legacy; not in runtime registry | — | NOT IN REGISTRY |
| `final_evaluation` | `models/india/final_evaluation.json` | 679 | `04552f31c8694223a7895a10ce195acf5629ec772fa7da68628a5b0afea7658b` | India | experiment metadata | optional research/legacy; not in runtime registry | — | NOT IN REGISTRY |
| `india_holdout_archetype_pipeline` | `models/india/india_holdout_archetype_pipeline.pkl` | 55644 | `efce615d239ca0198605bdee3468b1709c281242af0b49a38df311d3e272df6b` | India | legacy/experimental model artifact | optional research/legacy; not in runtime registry | — | NOT IN REGISTRY |
| `kmeans_phase4_k7` | `models/kmeans_phase4_k7.pkl` | 1345139 | `7716419c8b26eae903464d118137726294ad55084d90f83843b6264deab4b047` | USA / legacy phase 4 | legacy/experimental model artifact | optional research/legacy; not in runtime registry | — | NOT IN REGISTRY |
| `pca_phase4` | `models/pca_phase4.pkl` | 6355 | `2995dfb11134ae9381f9e8c893ddfaea070ebfc1691287d6d883d12484f44a4a` | USA / legacy phase 4 | legacy/experimental model artifact | optional research/legacy; not in runtime registry | — | NOT IN REGISTRY |
| `scaler_phase4` | `models/scaler_phase4.pkl` | 1161 | `11067c5a83090ef2e96f2e75a279b2bf6dfee0c7b9a1f97cd7ef71005f9826ef` | USA / legacy phase 4 | legacy/experimental model artifact | optional research/legacy; not in runtime registry | — | NOT IN REGISTRY |

## Findings

- Runtime manifest entries: 19; every listed file exists and every SHA-256 matches at audit time: **True**.
- Manifest `size_bytes` values are stale for several entries even when hashes match. Current actual size is recorded above; SHA-256 is the integrity decision recorded by the registry.
- India and USA optional research cohorts, plus other ignored processed files, exist locally and are not tracked in Git. Their hashes are recorded where present because the central manifest lists them; private row-level content is not included.
- Model files outside the manifest are identified as legacy/experimental and must not be treated as runtime requirements without tracing references.
- `models/pca_phase4.pkl`, `models/kmeans_phase4_k7.pkl`, and `models/scaler_phase4.pkl` are older USA phase-4 assets. Runtime registry instead uses `_phase4_1` assets for USA archetypes.
