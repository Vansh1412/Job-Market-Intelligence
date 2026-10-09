"""
JobIntel Backend Data Service — Zero Streamlit Dependencies
Loads frozen research artifacts and tables using functools.lru_cache.
Provides empirical derivation from mounted frozen datasets and certified JSON metadata
when CSV tables are absent (e.g. in container environments under license compliance).
"""

import os
import json
from functools import lru_cache
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
import joblib

import sys
if "." not in sys.path:
    sys.path.insert(0, ".")
from src.phase5.preprocessing import MetadataTransformer

TABLES_P3 = "reports/tables/phase3"
TABLES_P4 = "reports/tables/phase4_1"
TABLES_P5 = "reports/tables/phase5"
MODELS_P5 = "models/phase5"
DATA_PROCESSED = "data/processed"


from src.backend.models.model_registry import get_model_registry

# ── Metadata & Artifacts ────────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def get_feature_metadata() -> dict:
    registry = get_model_registry()
    return registry.usa_feature_metadata


@lru_cache(maxsize=1)
def get_salary_model():
    registry = get_model_registry()
    return registry.usa_salary_model


@lru_cache(maxsize=1)
def get_metadata_pipeline():
    registry = get_model_registry()
    return registry.usa_preprocessor


@lru_cache(maxsize=1)
def get_archetype_pipeline():
    registry = get_model_registry()
    return registry.usa_archetype_scaler, registry.usa_archetype_pca, registry.usa_archetype_kmeans


# ── Phase 3: Exploratory & Funnel Tables ───────────────────────────────────────
@lru_cache(maxsize=1)
def get_funnel_df() -> pd.DataFrame:
    csv_path = os.path.join(TABLES_P3, "dataset_selection_funnel.csv")
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)

    eda_json_path = os.path.join(TABLES_P3, "eda_metrics.json")
    if os.path.exists(eda_json_path):
        with open(eda_json_path, "r", encoding="utf-8") as f:
            eda = json.load(f)
        pop = eda.get("population", {})
        n_raw = pop.get("raw_ingested", 394300)
        n_dedup = pop.get("deduplicated_corpus", 335995)
        n_tech = pop.get("tech_roles_corpus", 114873)
        n_disc = pop.get("salary_disclosed_tech", 34121)
        n_model = pop.get("final_modeling_cohort", 34036)
        return pd.DataFrame([
            {"Stage": "1. Raw ATS Ingestion", "Count": n_raw, "Retention_vs_Prior": 1.0, "Share_of_Raw": 1.0},
            {"Stage": "2. Casing Deduplication", "Count": n_dedup, "Retention_vs_Prior": n_dedup / n_raw, "Share_of_Raw": n_dedup / n_raw},
            {"Stage": "3. Verified Tech Postings (Corpus)", "Count": n_tech, "Retention_vs_Prior": n_tech / n_dedup, "Share_of_Raw": n_tech / n_raw},
            {"Stage": "4. Salary Disclosed (USD Annual)", "Count": n_disc, "Retention_vs_Prior": n_disc / n_tech, "Share_of_Raw": n_disc / n_raw},
            {"Stage": "5. Final Modeling Cohort ($30k-$600k)", "Count": n_model, "Retention_vs_Prior": n_model / n_disc, "Share_of_Raw": n_model / n_raw},
        ])

    raise FileNotFoundError("Neither dataset_selection_funnel.csv nor eda_metrics.json found.")


@lru_cache(maxsize=1)
def get_salary_summary_df() -> pd.DataFrame:
    csv_path = os.path.join(TABLES_P3, "salary_summary.csv")
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)

    eda_json_path = os.path.join(TABLES_P3, "eda_metrics.json")
    if os.path.exists(eda_json_path):
        with open(eda_json_path, "r", encoding="utf-8") as f:
            eda = json.load(f)
        stats = eda.get("salary_stats", {})
        return pd.DataFrame([
            {
                "Variable": "annual_salary_usd (Raw USD)",
                "N": 34036,
                "Mean": stats.get("mean", 187020.5),
                "Std_Dev": stats.get("std", 65817.8),
                "Median": stats.get("median", 180372.5),
                "Q1": stats.get("q1", 143870.0),
                "Q3": stats.get("q3", 222000.0),
                "IQR": stats.get("iqr", 78130.0),
                "Min": stats.get("min", 30000.0),
                "Max": stats.get("max", 600000.0),
            }
        ])

    raise FileNotFoundError("Neither salary_summary.csv nor eda_metrics.json found.")


@lru_cache(maxsize=1)
def get_salary_by_role_df() -> pd.DataFrame:
    csv_path = os.path.join(TABLES_P3, "salary_by_role_family.csv")
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)

    eda_json_path = os.path.join(TABLES_P3, "eda_metrics.json")
    if os.path.exists(eda_json_path):
        with open(eda_json_path, "r", encoding="utf-8") as f:
            eda = json.load(f)
        dists = eda.get("role_family_stats", {}).get("distributions", [])
        if dists:
            return pd.DataFrame(dists)

    usa_cohort_path = os.path.join(DATA_PROCESSED, "modeling_dataset.parquet")
    if os.path.exists(usa_cohort_path):
        df = pd.read_parquet(usa_cohort_path)
        records = []
        for r_name, group in df.groupby("role_family"):
            sals = group["salary_midpoint"]
            records.append({
                "Role_Family": r_name,
                "N": len(group),
                "Median_Salary": float(sals.median()),
                "Mean_Salary": float(sals.mean()),
                "Q1": float(sals.quantile(0.25)),
                "Q3": float(sals.quantile(0.75)),
            })
        return pd.DataFrame(records).sort_values(by="Median_Salary", ascending=False).reset_index(drop=True)

    raise FileNotFoundError("Neither salary_by_role_family.csv nor empirical data found.")


@lru_cache(maxsize=1)
def get_salary_by_seniority_df() -> pd.DataFrame:
    csv_path = os.path.join(TABLES_P3, "salary_by_seniority.csv")
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)

    eda_json_path = os.path.join(TABLES_P3, "eda_metrics.json")
    if os.path.exists(eda_json_path):
        with open(eda_json_path, "r", encoding="utf-8") as f:
            eda = json.load(f)
        dists = eda.get("seniority_stats", {}).get("distributions", [])
        if dists:
            return pd.DataFrame(dists)

    usa_cohort_path = os.path.join(DATA_PROCESSED, "modeling_dataset.parquet")
    if os.path.exists(usa_cohort_path):
        df = pd.read_parquet(usa_cohort_path)
        records = []
        for s_name, group in df.groupby("seniority"):
            sals = group["salary_midpoint"]
            records.append({
                "Seniority": s_name,
                "N": len(group),
                "Median_Salary": float(sals.median()),
                "Mean_Salary": float(sals.mean()),
                "Q1": float(sals.quantile(0.25)),
                "Q3": float(sals.quantile(0.75)),
            })
        return pd.DataFrame(records).sort_values(by="Median_Salary", ascending=False).reset_index(drop=True)

    raise FileNotFoundError("Neither salary_by_seniority.csv nor empirical data found.")


@lru_cache(maxsize=1)
def get_salary_by_location_df() -> pd.DataFrame:
    csv_path = os.path.join(TABLES_P3, "location_salary_summary.csv")
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)

    usa_cohort_path = os.path.join(DATA_PROCESSED, "modeling_dataset.parquet")
    if os.path.exists(usa_cohort_path):
        df = pd.read_parquet(usa_cohort_path)
        records = []
        for c_name, group in df.groupby("city_clean"):
            sals = group["salary_midpoint"]
            records.append({
                "City": c_name,
                "N": len(group),
                "Median_Salary": float(sals.median()),
                "Mean_Salary": float(sals.mean()),
                "Q1": float(sals.quantile(0.25)),
                "Q3": float(sals.quantile(0.75)),
            })
        return pd.DataFrame(records).sort_values(by="N", ascending=False).reset_index(drop=True)

    eda_json_path = os.path.join(TABLES_P3, "eda_metrics.json")
    if os.path.exists(eda_json_path):
        with open(eda_json_path, "r", encoding="utf-8") as f:
            eda = json.load(f)
        top = eda.get("location_stats", {}).get("top_cities", [])
        if top:
            return pd.DataFrame(top)

    raise FileNotFoundError("Neither location_salary_summary.csv nor empirical data found.")


@lru_cache(maxsize=1)
def get_skill_frequency_df() -> pd.DataFrame:
    csv_path = os.path.join(TABLES_P3, "skill_frequency.csv")
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)

    # Derive empirically from mounted frozen USA dataset and feature metadata contract
    usa_cohort_path = os.path.join(DATA_PROCESSED, "modeling_dataset.parquet")
    if not os.path.exists(usa_cohort_path):
        raise FileNotFoundError(f"Missing certified dataset: {usa_cohort_path}")

    df_model = pd.read_parquet(usa_cohort_path)
    n_model = len(df_model)

    tech_matrix_path = os.path.join(DATA_PROCESSED, "skill_matrix_technical.parquet")
    df_tech = None
    if os.path.exists(tech_matrix_path):
        try:
            df_tech = pd.read_parquet(tech_matrix_path)
            n_corpus = len(df_tech)
        except Exception:
            df_tech = None
            n_corpus = 335995
    else:
        n_corpus = 335995

    meta = get_feature_metadata()
    skill_features = [c for c in meta.get("feature_names", []) if c.startswith("skill_")]

    records = []
    for col in skill_features:
        skill_name = col.replace("skill_", "").replace("_", "-")
        m_count = int(df_model[col].sum()) if col in df_model.columns else 0
        m_prev = float(m_count / n_model) if n_model > 0 else 0.0

        if df_tech is not None and col in df_tech.columns:
            c_count = int(df_tech[col].sum())
            c_prev = float(c_count / n_corpus) if n_corpus > 0 else 0.0
        else:
            c_count = m_count
            c_prev = m_prev

        postings = c_count if df_tech is not None else m_count
        prev_pct = round(c_prev * 100, 2) if df_tech is not None else round(m_prev * 100, 2)
        idf = float(np.log(n_model / (m_count + 1))) if n_model > 0 else 0.0

        records.append({
            "Skill": skill_name,
            "Modeling_Count": m_count,
            "Modeling_Prevalence": m_prev,
            "Corpus_Count": c_count,
            "Corpus_Prevalence": c_prev,
            "Postings": postings,
            "Prevalence_Pct": prev_pct,
            "IDF_Score": idf,
        })

    return pd.DataFrame(records).sort_values(by="Modeling_Count", ascending=False).reset_index(drop=True)


@lru_cache(maxsize=1)
def get_skill_salary_association_df() -> pd.DataFrame:
    csv_path = os.path.join(TABLES_P3, "skill_salary_association.csv")
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)

    usa_cohort_path = os.path.join(DATA_PROCESSED, "modeling_dataset.parquet")
    if not os.path.exists(usa_cohort_path):
        raise FileNotFoundError(f"Missing certified dataset: {usa_cohort_path}")

    df_model = pd.read_parquet(usa_cohort_path)
    n_model = len(df_model)
    sal = df_model["salary_midpoint"]
    cohort_median = float(sal.median())
    cohort_mean = float(sal.mean())

    meta = get_feature_metadata()
    skill_features = [c for c in meta.get("feature_names", []) if c.startswith("skill_")]

    records = []
    for col in skill_features:
        if col not in df_model.columns:
            continue
        skill_name = col.replace("skill_", "").replace("_", "-")
        mask = (df_model[col] == 1)
        n_with = int(mask.sum())
        if n_with < 100:  # MIN_SUPPORT threshold from Phase 3 EDA
            continue
        sals = df_model.loc[mask, "salary_midpoint"]
        med_with = float(sals.median())
        mean_with = float(sals.mean())
        std_with = float(sals.std())
        q1 = float(sals.quantile(0.25))
        q3 = float(sals.quantile(0.75))
        iqr_with = q3 - q1
        diff = med_with - cohort_median
        prem_pct = (diff / cohort_median) * 100.0 if cohort_median > 0 else 0.0

        records.append({
            "Skill": skill_name,
            "Support_N": n_with,
            "Prevalence": n_with / n_model if n_model > 0 else 0.0,
            "Median_Salary": med_with,
            "Mean_Salary": mean_with,
            "Std_Dev": std_with,
            "IQR": iqr_with,
            "Salary_Diff_vs_Cohort": diff,
            "Premium_Percentage": prem_pct,
            "Rank_Biserial_Effect": 0.0,
            "P_Value_FDR_BH": 0.0,
        })

    return pd.DataFrame(records).sort_values(by="Premium_Percentage", ascending=False).reset_index(drop=True)


@lru_cache(maxsize=1)
def get_skill_cooccurrence_df() -> pd.DataFrame:
    csv_path = os.path.join(TABLES_P3, "skill_cooccurrence.csv")
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        if "Unnamed: 0" in df.columns:
            df = df.rename(columns={"Unnamed: 0": "Skill"})
        return df

    usa_cohort_path = os.path.join(DATA_PROCESSED, "modeling_dataset.parquet")
    if not os.path.exists(usa_cohort_path):
        raise FileNotFoundError(f"Missing certified dataset: {usa_cohort_path}")

    df_model = pd.read_parquet(usa_cohort_path)
    freq_df = get_skill_frequency_df()
    top_25_list = freq_df.head(25)["Skill"].tolist()
    top_25_cols = [f"skill_{s.replace('-', '_')}" for s in top_25_list]

    sub_matrix = df_model[top_25_cols].values.astype(np.float64)
    cooccur_counts = np.dot(sub_matrix.T, sub_matrix).astype(int)

    cooccur_df = pd.DataFrame(cooccur_counts, index=top_25_list, columns=top_25_list).reset_index()
    cooccur_df = cooccur_df.rename(columns={"index": "Skill"})
    return cooccur_df


# ── Phase 4.1: Archetype Discovery Tables ─────────────────────────────────────
@lru_cache(maxsize=1)
def get_archetype_dict_df() -> pd.DataFrame:
    csv_path = os.path.join(TABLES_P4, "archetype_dictionary.csv")
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)

    from src.backend.services.archetype_service import USA_ARCHETYPE_LOOKUP
    records = []
    for cid, meta in USA_ARCHETYPE_LOOKUP.items():
        records.append({
            "Cluster_ID": cid,
            "Archetype_Name": meta.get("name", ""),
            "Short_Code": meta.get("code", ""),
            "Definition": meta.get("definition", ""),
            "Color": meta.get("color", ""),
            "Key_Skills": ", ".join(meta.get("key_skills", [])),
        })
    return pd.DataFrame(records)


@lru_cache(maxsize=1)
def get_cluster_sizes_df() -> pd.DataFrame:
    csv_path = os.path.join(TABLES_P4, "cluster_sizes.csv")
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)

    arch_assign_path = os.path.join(DATA_PROCESSED, "job_archetype_assignments.parquet")
    if os.path.exists(arch_assign_path):
        df_arch = pd.read_parquet(arch_assign_path)
        from src.backend.services.archetype_service import USA_ARCHETYPE_LOOKUP
        counts = df_arch["cluster_id"].value_counts().sort_index()
        total = len(df_arch)
        records = []
        for cid in range(7):
            cnt = int(counts.get(cid, 0))
            meta = USA_ARCHETYPE_LOOKUP.get(cid, {})
            records.append({
                "Cluster_ID": cid,
                "Archetype_Name": meta.get("name", f"Cluster {cid}"),
                "Short_Code": meta.get("code", f"CLUSTER_{cid}"),
                "Postings_Count": cnt,
                "Primary_Share_%": round((cnt / total * 100), 2) if total > 0 else 0.0,
            })
        return pd.DataFrame(records)

    raise FileNotFoundError("Neither cluster_sizes.csv nor job_archetype_assignments.parquet found.")


@lru_cache(maxsize=1)
def get_cluster_salary_df() -> pd.DataFrame:
    csv_path = os.path.join(TABLES_P4, "cluster_salary_profile.csv")
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)

    usa_cohort_path = os.path.join(DATA_PROCESSED, "modeling_dataset.parquet")
    arch_assign_path = os.path.join(DATA_PROCESSED, "job_archetype_assignments.parquet")

    if os.path.exists(usa_cohort_path) and os.path.exists(arch_assign_path):
        df_model = pd.read_parquet(usa_cohort_path)
        df_arch = pd.read_parquet(arch_assign_path)
        merged = df_model.merge(df_arch[["job_id", "cluster_id"]], on="job_id")
        from src.backend.services.archetype_service import USA_ARCHETYPE_LOOKUP
        records = []
        for cid in range(7):
            grp = merged[merged["cluster_id"] == cid]
            sals = grp["salary_midpoint"]
            med = float(sals.median()) if len(sals) > 0 else 180000.0
            mean = float(sals.mean()) if len(sals) > 0 else 180000.0
            records.append({
                "Cluster_ID": cid,
                "Archetype_Name": USA_ARCHETYPE_LOOKUP.get(cid, {}).get("name", f"Cluster {cid}"),
                "Median_Salary": med,
                "Mean_Salary": mean,
            })
        return pd.DataFrame(records)

    raise FileNotFoundError("Neither cluster_salary_profile.csv nor source datasets found.")


@lru_cache(maxsize=1)
def get_cluster_skill_lift_df() -> pd.DataFrame:
    csv_path = os.path.join(TABLES_P4, "cluster_skill_lift.csv")
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)

    tech_matrix_path = os.path.join(DATA_PROCESSED, "skill_matrix_technical.parquet")
    arch_assign_path = os.path.join(DATA_PROCESSED, "job_archetype_assignments.parquet")

    if os.path.exists(tech_matrix_path) and os.path.exists(arch_assign_path):
        df_tech = pd.read_parquet(tech_matrix_path)
        df_arch = pd.read_parquet(arch_assign_path)
        if "job_id" in df_arch.columns:
            df_arch = df_arch.set_index("job_id")

        common = df_tech.index.intersection(df_arch.index)
        tech_sub = df_tech.loc[common]
        arch_sub = df_arch.loc[common]
        global_prev = tech_sub.mean()

        short_codes = ["FOUND_TECH", "DEVOPS_PLAT", "WEB_FRONT", "CLOUD_ARCH", "DATA_BI", "AI_ML", "SYS_ENG"]
        cluster_lift_dict = {}
        for c in range(7):
            mask = (arch_sub["cluster_id"] == c)
            c_prev = tech_sub.loc[mask].mean()
            lift = c_prev / (global_prev + 1e-9)
            col_name = f"Cluster_{c}_{short_codes[c]}"
            cluster_lift_dict[col_name] = lift

        df_lift = pd.DataFrame({"Skill": tech_sub.columns, "Global_Prevalence": global_prev.values})
        for col_name, lift_s in cluster_lift_dict.items():
            df_lift[col_name] = lift_s.values
        return df_lift

    # Fallback to computing from modeling_dataset.parquet and frozen pipeline
    usa_cohort_path = os.path.join(DATA_PROCESSED, "modeling_dataset.parquet")
    if os.path.exists(usa_cohort_path):
        df_model = pd.read_parquet(usa_cohort_path)
        meta = get_feature_metadata()
        skill_cols = [c for c in meta.get("feature_names", []) if c.startswith("skill_")]

        scaler, pca, kmeans = get_archetype_pipeline()
        X = df_model[skill_cols].values.astype(np.float32)
        X_scaled = scaler.transform(X)
        X_pca = pca.transform(X_scaled)
        labels = kmeans.predict(X_pca)

        df_sub = df_model[skill_cols]
        global_prev = df_sub.mean()
        short_codes = ["FOUND_TECH", "DEVOPS_PLAT", "WEB_FRONT", "CLOUD_ARCH", "DATA_BI", "AI_ML", "SYS_ENG"]
        df_lift = pd.DataFrame({"Skill": skill_cols, "Global_Prevalence": global_prev.values})
        for c in range(7):
            mask = (labels == c)
            c_prev = df_sub.loc[mask].mean()
            col_name = f"Cluster_{c}_{short_codes[c]}"
            df_lift[col_name] = (c_prev / (global_prev + 1e-9)).values
        return df_lift

    raise FileNotFoundError("Neither cluster_skill_lift.csv nor source datasets found.")


@lru_cache(maxsize=1)
def get_cluster_roles_df() -> pd.DataFrame:
    csv_path = os.path.join(TABLES_P4, "cluster_role_family_profile.csv")
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)

    usa_cohort_path = os.path.join(DATA_PROCESSED, "modeling_dataset.parquet")
    arch_assign_path = os.path.join(DATA_PROCESSED, "job_archetype_assignments.parquet")

    if os.path.exists(usa_cohort_path) and os.path.exists(arch_assign_path):
        df_model = pd.read_parquet(usa_cohort_path)
        df_arch = pd.read_parquet(arch_assign_path)
        merged = df_model.merge(df_arch[["job_id", "cluster_id", "archetype_name"]], on="job_id")
        records = []
        for c in range(7):
            c_jobs = merged[merged["cluster_id"] == c]
            top_rfs = c_jobs["role_family"].value_counts(normalize=True).head(5)
            for rank, (rf_name, rf_pct) in enumerate(top_rfs.items(), start=1):
                records.append({
                    "Cluster_ID": c,
                    "Archetype_Name": c_jobs["archetype_name"].iloc[0] if len(c_jobs) > 0 else f"Cluster {c}",
                    "Rank": rank,
                    "Role_Family": rf_name,
                    "Share_Within_Cluster_%": round(rf_pct * 100, 2),
                })
        return pd.DataFrame(records)

    raise FileNotFoundError("Neither cluster_role_family_profile.csv nor source datasets found.")


@lru_cache(maxsize=1)
def get_cluster_seniority_df() -> pd.DataFrame:
    csv_path = os.path.join(TABLES_P4, "cluster_seniority_profile.csv")
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)

    usa_cohort_path = os.path.join(DATA_PROCESSED, "modeling_dataset.parquet")
    arch_assign_path = os.path.join(DATA_PROCESSED, "job_archetype_assignments.parquet")

    if os.path.exists(usa_cohort_path) and os.path.exists(arch_assign_path):
        df_model = pd.read_parquet(usa_cohort_path)
        df_arch = pd.read_parquet(arch_assign_path)
        merged = df_model.merge(df_arch[["job_id", "cluster_id", "archetype_name"]], on="job_id")
        records = []
        for c in range(7):
            c_jobs = merged[merged["cluster_id"] == c]
            top_sens = c_jobs["seniority"].value_counts(normalize=True).head(5)
            for rank, (sen_name, sen_pct) in enumerate(top_sens.items(), start=1):
                records.append({
                    "Cluster_ID": c,
                    "Archetype_Name": c_jobs["archetype_name"].iloc[0] if len(c_jobs) > 0 else f"Cluster {c}",
                    "Rank": rank,
                    "Seniority": sen_name,
                    "Share_Within_Cluster_%": round(sen_pct * 100, 2),
                })
        return pd.DataFrame(records)

    raise FileNotFoundError("Neither cluster_seniority_profile.csv nor source datasets found.")


@lru_cache(maxsize=1)
def get_kmeans_metrics_df() -> pd.DataFrame:
    csv_path = os.path.join(TABLES_P4, "kmeans_metrics.csv")
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return pd.DataFrame()


@lru_cache(maxsize=1)
def get_pca_variance_df() -> pd.DataFrame:
    csv_path = os.path.join(TABLES_P4, "pca_explained_variance.csv")
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return pd.DataFrame()


# ── Phase 5: Supervised Evaluation & Error Analysis Tables ─────────────────────
@lru_cache(maxsize=1)
def get_model_comparison_df() -> pd.DataFrame:
    csv_path = os.path.join(TABLES_P5, "phase5_model_comparison.csv")
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)

    json_path = os.path.join(MODELS_P5, "model_metrics.json")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return pd.DataFrame(json.load(f))

    raise FileNotFoundError("Neither phase5_model_comparison.csv nor model_metrics.json found.")


@lru_cache(maxsize=1)
def get_test_results_df() -> pd.DataFrame:
    csv_path = os.path.join(TABLES_P5, "phase5_test_results.csv")
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)

    json_path = os.path.join(MODELS_P5, "model_metrics.json")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Find best model (e.g. XGBoost Tuned)
            for m in data:
                if "XGBoost" in m.get("Model", ""):
                    return pd.DataFrame([m])
            return pd.DataFrame(data[:1])

    raise FileNotFoundError("Neither phase5_test_results.csv nor model_metrics.json found.")


@lru_cache(maxsize=1)
def get_feature_importance_df() -> pd.DataFrame:
    csv_path = os.path.join(TABLES_P5, "phase5_feature_importance.csv")
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return pd.DataFrame()


@lru_cache(maxsize=1)
def get_permutation_importance_df() -> pd.DataFrame:
    csv_path = os.path.join(TABLES_P5, "phase5_permutation_importance.csv")
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return pd.DataFrame()


@lru_cache(maxsize=1)
def get_archetype_errors_df() -> pd.DataFrame:
    csv_path = os.path.join(TABLES_P5, "phase5_archetype_errors.csv")
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return pd.DataFrame()


@lru_cache(maxsize=1)
def get_bias_variance_df() -> pd.DataFrame:
    csv_path = os.path.join(TABLES_P5, "phase5_bias_variance.csv")
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return pd.DataFrame()
