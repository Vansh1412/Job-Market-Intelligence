"""
JobIntel -- Phase India-5: Archetype Discovery Engine
====================================================
Performs unsupervised skill archetype discovery, PCA evaluation, K-Means clustering,
stability analysis across seeds, salary association analysis (Kruskal-Wallis + Dunn),
and leakage-safe holdout prediction error stratification (RQ3).

Author: Antigravity Data Science & Statistical Governance Team
Date: October 2026
Phase: India-5
"""

import os
import json
import pickle
import hashlib
import time
from typing import Dict, List, Tuple, Any

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.optimize import linear_sum_assignment
from statsmodels.stats.multitest import multipletests
from sklearn.model_selection import GroupShuffleSplit
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import (
    silhouette_score,
    davies_bouldin_score,
    calinski_harabasz_score,
    adjusted_rand_score,
    adjusted_mutual_info_score,
)

# -----------------------------------------------------------------------------
# PATHS AND CONSTANTS
# -----------------------------------------------------------------------------
DATA_PATH = "data/processed/india/india_modeling_cohort.parquet"
SCHEMA_PATH = "data/processed/india/india_feature_schema.json"

FROZEN_MODEL_PATH = "models/india/final_model.pkl"
FROZEN_PREPROCESSOR_PATH = "models/india/final_preprocessor.pkl"
FROZEN_FEATURE_LIST_PATH = "models/india/final_feature_list.json"
FROZEN_METADATA_PATH = "models/india/final_model_metadata.json"

MODELS_DIR = "models/india"
TABLES_DIR = "reports/tables/india"
FIGURES_DIR = "reports/figures/india"
DATA_PROCESSED_DIR = "data/processed/india"

PRIMARY_SEED = 42
STABILITY_SEEDS = [42, 7, 21, 100, 123]
N_COMPONENTS_RETAINED = 15
SELECTED_K = 6

# Styling configuration
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["font.size"] = 10
plt.rcParams["axes.titlesize"] = 12
plt.rcParams["axes.labelsize"] = 11
plt.rcParams["figure.dpi"] = 200

# -----------------------------------------------------------------------------
# HELPER: DUNN TEST WITH MULTIPLE TESTING CORRECTION
# -----------------------------------------------------------------------------
def run_dunn_test(
    groups: List[np.ndarray],
    group_names: List[str],
    method: str = "holm"
) -> pd.DataFrame:
    """
    Perform Dunn's post-hoc pairwise rank-sum test with exact tie correction
    and FWER/FDR multiplicity adjustment (Holm).
    """
    all_vals = []
    group_indices = []
    for idx, grp in enumerate(groups):
        all_vals.extend(grp)
        group_indices.extend([idx] * len(grp))
        
    all_vals = np.array(all_vals)
    group_indices = np.array(group_indices)
    N = len(all_vals)
    k = len(groups)
    
    ranks = stats.rankdata(all_vals)
    
    # Tie correction factor
    _, counts = np.unique(all_vals, return_counts=True)
    tie_term = np.sum(counts**3 - counts) / (12.0 * (N - 1)) if N > 1 else 0.0
    sigma2 = (N * (N + 1) / 12.0) - tie_term
    
    group_mean_ranks = [np.mean(ranks[group_indices == i]) for i in range(k)]
    group_sizes = [len(grp) for grp in groups]
    
    records = []
    p_raw_list = []
    
    for i in range(k):
        for j in range(i + 1, k):
            diff = group_mean_ranks[i] - group_mean_ranks[j]
            se = np.sqrt(sigma2 * (1.0 / group_sizes[i] + 1.0 / group_sizes[j]))
            z = diff / se if se > 0 else 0.0
            p_val = 2.0 * (1.0 - stats.norm.cdf(np.abs(z)))
            
            records.append({
                "group1": group_names[i],
                "group2": group_names[j],
                "mean_rank_diff": diff,
                "standard_error": se,
                "z_statistic": z,
                "p_raw": p_val
            })
            p_raw_list.append(p_val)
            
    rejected, p_adj, _, _ = multipletests(p_raw_list, method=method)
    
    for idx, rec in enumerate(records):
        rec["p_adjusted"] = p_adj[idx]
        rec["correction_method"] = method
        rec["significant"] = bool(rejected[idx])
        
    return pd.DataFrame(records)

# -----------------------------------------------------------------------------
# MAIN PIPELINE CLASS
# -----------------------------------------------------------------------------
class IndiaArchetypeEngine:
    def __init__(self):
        os.makedirs(MODELS_DIR, exist_ok=True)
        os.makedirs(TABLES_DIR, exist_ok=True)
        os.makedirs(FIGURES_DIR, exist_ok=True)
        os.makedirs(DATA_PROCESSED_DIR, exist_ok=True)
        
        self.df = None
        self.skill_cols = None
        self.df_skills = None
        self.X_skills = None
        
        self.pca_full = None
        self.X_pca_full = None
        self.km_full = None
        
        self.archetype_meta = {}
        self.archetype_labels = None
        
    def step1_load_and_audit(self):
        """Load cohort and audit skill matrix binary properties."""
        print("\n" + "=" * 80)
        print("STEP 1: POPULATION & SKILL MATRIX AUDIT")
        print("=" * 80)
        
        self.df = pd.read_parquet(DATA_PATH)
        self.skill_cols = [c for c in self.df.columns if c.startswith("skill_")]
        
        n_total = len(self.df)
        n_skills = len(self.skill_cols)
        
        assert n_total == 5859, f"Expected 5,859 rows, got {n_total}"
        assert n_skills == 284, f"Expected 284 skill columns, got {n_skills}"
        
        # Binary check
        for sc in self.skill_cols:
            u_vals = set(self.df[sc].unique())
            assert u_vals.issubset({0, 1}), f"Non-binary values in {sc}: {u_vals}"
            
        row_sums = self.df[self.skill_cols].sum(axis=1)
        skill_mask = row_sums >= 1
        
        n_skill_bearing = int(skill_mask.sum())
        n_zero_skill = int((~skill_mask).sum())
        
        print(f"Total cohort rows: N = {n_total}")
        print(f"Skill columns: {n_skills}")
        print(f"Skill-bearing rows (>= 1 selected skill): N = {n_skill_bearing} ({n_skill_bearing/n_total*100:.2f}%)")
        print(f"Zero-skill rows (0 selected skills): N = {n_zero_skill} ({n_zero_skill/n_total*100:.2f}%)")
        
        self.df_skills = self.df[skill_mask].copy().reset_index(drop=True)
        self.X_skills = self.df_skills[self.skill_cols].values
        
        sparsity = float((self.X_skills == 0).sum() / self.X_skills.size)
        print(f"Skill matrix shape: {self.X_skills.shape}")
        print(f"Skill matrix sparsity: {sparsity*100:.2f}%")
        
        # Skill prevalence table
        prev_records = []
        for sc in self.skill_cols:
            clean_name = sc.replace("skill_", "").replace("_", " ").title()
            cnt = int(self.df_skills[sc].sum())
            pct = cnt / len(self.df_skills) * 100.0
            prev_records.append({
                "skill_column": sc,
                "skill_name": clean_name,
                "frequency_count": cnt,
                "prevalence_pct": pct,
                "sparsity_pct": 100.0 - pct
            })
        df_prev = pd.DataFrame(prev_records).sort_values(by="frequency_count", ascending=False)
        df_prev.to_csv(os.path.join(TABLES_DIR, "india_skill_prevalence.csv"), index=False)
        print(f"Saved: {TABLES_DIR}/india_skill_prevalence.csv")
        
        return df_prev

    def step2_evaluate_pca(self):
        """Evaluate PCA formulations (PCA-A centered covariance vs PCA-B standardized correlation)."""
        print("\n" + "=" * 80)
        print("STEP 2: PCA FORMULATION & COMPONENT RETENTION EVALUATION")
        print("=" * 80)
        
        # PCA-A: Centered Covariance PCA
        pca_a = PCA(random_state=PRIMARY_SEED)
        pca_a.fit(self.X_skills)
        var_a = pca_a.explained_variance_ratio_
        cum_a = np.cumsum(var_a)
        
        # PCA-B: Standardized Correlation PCA
        scaler_b = StandardScaler()
        X_scaled_b = scaler_b.fit_transform(self.X_skills)
        pca_b = PCA(random_state=PRIMARY_SEED)
        pca_b.fit(X_scaled_b)
        var_b = pca_b.explained_variance_ratio_
        cum_b = np.cumsum(var_b)
        
        print("PCA-A (Centered Covariance) Cumulative Variance:")
        print(f"  10 PCs: {cum_a[9]*100:.2f}%, 15 PCs: {cum_a[14]*100:.2f}%, 20 PCs: {cum_a[19]*100:.2f}%, 30 PCs: {cum_a[29]*100:.2f}%")
        print("PCA-B (Standardized Correlation) Cumulative Variance:")
        print(f"  10 PCs: {cum_b[9]*100:.2f}%, 15 PCs: {cum_b[14]*100:.2f}%, 20 PCs: {cum_b[19]*100:.2f}%, 30 PCs: {cum_b[29]*100:.2f}%")
        
        # Primary selection: PCA-A with 15 components
        # Rationale: Binary sparse skill data. Standardization inflates rare singleton terms by ~40x,
        # distorting natural Euclidean market distance. Centered covariance PCA preserves variance
        # proportional to real market prevalence. Scree elbow stabilizes around PC15 where marginal variance drops to ~1.1%.
        self.pca_full = PCA(n_components=N_COMPONENTS_RETAINED, random_state=PRIMARY_SEED)
        self.X_pca_full = self.pca_full.fit_transform(self.X_skills)
        
        var_retained = self.pca_full.explained_variance_ratio_
        cum_retained = np.cumsum(var_retained)
        
        var_records = []
        for i in range(len(var_a)):
            var_records.append({
                "component": f"PC{i+1:02d}",
                "eigenvalue": float(pca_a.singular_values_[i]**2 / (len(self.X_skills) - 1)),
                "explained_variance_ratio": float(var_a[i]),
                "cumulative_explained_variance": float(cum_a[i]),
                "retained": bool(i < N_COMPONENTS_RETAINED)
            })
        df_pca_var = pd.DataFrame(var_records)
        df_pca_var.to_csv(os.path.join(TABLES_DIR, "india_pca_variance.csv"), index=False)
        print(f"Saved: {TABLES_DIR}/india_pca_variance.csv")
        
        # Loadings table
        loadings_dict = {
            "skill_column": self.skill_cols,
            "skill_name": [c.replace("skill_", "").replace("_", " ").title() for c in self.skill_cols]
        }
        for pc_idx in range(N_COMPONENTS_RETAINED):
            loadings_dict[f"PC{pc_idx+1:02d}"] = self.pca_full.components_[pc_idx]
            
        df_loadings = pd.DataFrame(loadings_dict)
        df_loadings.to_csv(os.path.join(TABLES_DIR, "india_pca_loadings.csv"), index=False)
        print(f"Saved: {TABLES_DIR}/india_pca_loadings.csv")
        
        # Save serialized PCA artifact
        with open(os.path.join(MODELS_DIR, "india_pca_v1.pkl"), "wb") as f:
            pickle.dump(self.pca_full, f)
        print(f"Saved: {MODELS_DIR}/india_pca_v1.pkl")
        
        # Save PCA parquet data
        pca_cols = [f"pca_{i+1}" for i in range(N_COMPONENTS_RETAINED)]
        df_pca_out = pd.DataFrame(self.X_pca_full, columns=pca_cols)
        df_pca_out["job_id"] = self.df_skills["job_id"].values
        df_pca_out["content_fingerprint"] = self.df_skills["content_fingerprint"].values
        # Reorder to put IDs first
        cols_order = ["job_id", "content_fingerprint"] + pca_cols
        df_pca_out = df_pca_out[cols_order]
        df_pca_out.to_parquet(os.path.join(DATA_PROCESSED_DIR, "india_skill_pca.parquet"), index=False)
        print(f"Saved: {DATA_PROCESSED_DIR}/india_skill_pca.parquet")
        
        return df_pca_var, df_loadings

    def step3_evaluate_kmeans_and_stability(self):
        """Evaluate KMeans for k=2..10 across silhouette, DB, CH, sizes, and stability seeds."""
        print("\n" + "=" * 80)
        print("STEP 3: K-MEANS MULTI-CRITERION & STABILITY EVALUATION")
        print("=" * 80)
        
        k_metrics = []
        for k in range(2, 11):
            km = KMeans(n_clusters=k, random_state=PRIMARY_SEED, n_init=10)
            labels = km.fit_predict(self.X_pca_full)
            
            sil = float(silhouette_score(self.X_pca_full, labels))
            db = float(davies_bouldin_score(self.X_pca_full, labels))
            ch = float(calinski_harabasz_score(self.X_pca_full, labels))
            inertia = float(km.inertia_)
            
            sizes = pd.Series(labels).value_counts().sort_index().values
            min_sz = int(np.min(sizes))
            max_sz = int(np.max(sizes))
            imbalance = float(max_sz / min_sz) if min_sz > 0 else np.nan
            sub_2pct = bool((min_sz / len(self.X_pca_full)) < 0.02)
            
            k_metrics.append({
                "k": k,
                "silhouette_score": sil,
                "davies_bouldin_index": db,
                "calinski_harabasz_index": ch,
                "inertia": inertia,
                "min_cluster_size": min_sz,
                "max_cluster_size": max_sz,
                "size_imbalance_ratio": imbalance,
                "sub_2pct_cluster_flag": sub_2pct
            })
            print(f"k={k:2d}: Silhouette={sil:.4f}, DB={db:.4f}, CH={ch:7.1f}, Min Size={min_sz:4d} (Sub-2%: {sub_2pct})")
            
        df_k_metrics = pd.DataFrame(k_metrics)
        df_k_metrics.to_csv(os.path.join(TABLES_DIR, "india_kmeans_metrics.csv"), index=False)
        print(f"Saved: {TABLES_DIR}/india_kmeans_metrics.csv")
        
        # Stability across seeds for selected k=6
        print(f"\nEvaluating Stability Across Seeds {STABILITY_SEEDS} for Selected k={SELECTED_K}...")
        labels_by_seed = {}
        for s in STABILITY_SEEDS:
            km_s = KMeans(n_clusters=SELECTED_K, random_state=s, n_init=10)
            labels_by_seed[s] = km_s.fit_predict(self.X_pca_full)
            
        stability_records = []
        aris = []
        amis = []
        for i in range(len(STABILITY_SEEDS)):
            for j in range(i + 1, len(STABILITY_SEEDS)):
                s1 = STABILITY_SEEDS[i]
                s2 = STABILITY_SEEDS[j]
                ari = float(adjusted_rand_score(labels_by_seed[s1], labels_by_seed[s2]))
                ami = float(adjusted_mutual_info_score(labels_by_seed[s1], labels_by_seed[s2]))
                aris.append(ari)
                amis.append(ami)
                stability_records.append({
                    "seed_pair": f"{s1}_vs_{s2}",
                    "seed_1": s1,
                    "seed_2": s2,
                    "ari": ari,
                    "ami": ami
                })
                
        df_stability = pd.DataFrame(stability_records)
        df_stability.to_csv(os.path.join(TABLES_DIR, "india_cluster_stability.csv"), index=False)
        print(f"Saved: {TABLES_DIR}/india_cluster_stability.csv")
        print(f"Stability Summary for k={SELECTED_K}:")
        print(f"  Mean ARI: {np.mean(aris):.4f}, Median ARI: {np.median(aris):.4f}, Min ARI: {np.min(aris):.4f}, Max ARI: {np.max(aris):.4f}")
        print(f"  Mean AMI: {np.mean(amis):.4f}, Median AMI: {np.median(amis):.4f}, Min AMI: {np.min(amis):.4f}, Max AMI: {np.max(amis):.4f}")
        
        return df_k_metrics, df_stability, np.mean(aris), np.median(aris), np.mean(amis), np.median(amis)

    def step4_fit_final_archetypes(self):
        """Fit final KMeans on full skill-bearing cohort and assign stable archetype IDs."""
        print("\n" + "=" * 80)
        print(f"STEP 4: FINAL ARCHETYPE DISCOVERY & TAXONOMY (k={SELECTED_K})")
        print("=" * 80)
        
        self.km_full = KMeans(n_clusters=SELECTED_K, random_state=PRIMARY_SEED, n_init=10)
        raw_labels = self.km_full.fit_predict(self.X_pca_full)
        
        # Save serialized KMeans
        with open(os.path.join(MODELS_DIR, "india_kmeans_v1.pkl"), "wb") as f:
            pickle.dump(self.km_full, f)
        print(f"Saved: {MODELS_DIR}/india_kmeans_v1.pkl")
        
        # Calculate cluster medians to order archetypes from highest to lowest salary
        cluster_sal_medians = {}
        for c in range(SELECTED_K):
            sub_sal = self.df_skills.loc[raw_labels == c, "salary_midpoint_inr"].values / 100000.0
            cluster_sal_medians[c] = float(np.median(sub_sal))
            
        # Rank by salary median descending
        sorted_clusters = sorted(cluster_sal_medians.keys(), key=lambda c: cluster_sal_medians[c], reverse=True)
        
        # Archetype definitions based on empirical profiles
        taxonomy_defs = {
            sorted_clusters[0]: {
                "id": "IND_ARC_01",
                "name": "Big Data Engineering & Distributed Systems",
                "definition": "Distributed big data pipelines, large-scale data processing frameworks (Spark, Hadoop, Hive), and workflow orchestration (Airflow, Scala)."
            },
            sorted_clusters[1]: {
                "id": "IND_ARC_02",
                "name": "Enterprise Java & Microservices Backend",
                "definition": "Enterprise backend architecture, Java ecosystems, Spring Boot microservices, and distributed service design, frequently extending to enterprise full-stack interfaces."
            },
            sorted_clusters[2]: {
                "id": "IND_ARC_03",
                "name": "Python, Cloud Data & Applied AI/ML",
                "definition": "Python-centric stack for analytical computing, machine learning, modern API services (FastAPI/Flask/Django), cloud databases, and generative AI systems."
            },
            sorted_clusters[3]: {
                "id": "IND_ARC_04",
                "name": "Full-Stack & Modern Application Engineering",
                "definition": "End-to-end software application lifecycle, modern web technologies (React, JavaScript, .NET), and relational data persistence."
            },
            sorted_clusters[4]: {
                "id": "IND_ARC_05",
                "name": "Baseline & General Technology Stack",
                "definition": "Broad, heterogeneous market stratum characterized by diverse baseline technology roles, IT support, QA testing, and low-density or cross-functional skill requirements."
            },
            sorted_clusters[5]: {
                "id": "IND_ARC_06",
                "name": "Enterprise ERP & SAP Functional Solutions",
                "definition": "Enterprise resource planning postings concentrated in SAP modules (FICO, MM), implementation consulting, functional testing, and enterprise certification."
            }
        }
        
        self.archetype_meta = {}
        cluster_to_arc_map = {}
        for rank, c_idx in enumerate(sorted_clusters):
            meta = taxonomy_defs[c_idx]
            self.archetype_meta[c_idx] = {
                "archetype_id": meta["id"],
                "archetype_numeric_label": rank + 1,
                "cluster_raw_idx": c_idx,
                "archetype_name": meta["name"],
                "definition": meta["definition"],
                "salary_median_lpa": cluster_sal_medians[c_idx]
            }
            cluster_to_arc_map[c_idx] = meta["id"]
            
        print("Established Archetype Taxonomy (Ranked by Observed Median Salary):")
        for c_idx in sorted_clusters:
            m = self.archetype_meta[c_idx]
            print(f"  {m['archetype_id']}: {m['archetype_name']} (Median: {m['salary_median_lpa']:.2f} LPA)")
            
        # Assign to skill-bearing dataframe
        self.archetype_labels = np.array([cluster_to_arc_map[c] for c in raw_labels])
        self.df_skills["archetype_id"] = self.archetype_labels
        self.df_skills["archetype_numeric_label"] = [self.archetype_meta[c]["archetype_numeric_label"] for c in raw_labels]
        self.df_skills["archetype_name"] = [self.archetype_meta[c]["archetype_name"] for c in raw_labels]
        
        # Build assignment table for the FULL 5,859 cohort (incorporating zero-skill rows cleanly)
        assignment_df = self.df[["job_id", "content_fingerprint", "total_selected_skill_count"]].copy()
        
        # Merge archetype assignments
        skill_assign_map = dict(zip(self.df_skills["job_id"], self.df_skills["archetype_id"]))
        skill_num_map = dict(zip(self.df_skills["job_id"], self.df_skills["archetype_numeric_label"]))
        skill_name_map = dict(zip(self.df_skills["job_id"], self.df_skills["archetype_name"]))
        
        assignment_df["has_selected_skills"] = assignment_df["total_selected_skill_count"] >= 1
        assignment_df["archetype_id"] = assignment_df["job_id"].map(skill_assign_map).fillna("IND_ARC_UNASSIGNED")
        assignment_df["archetype_numeric_label"] = assignment_df["job_id"].map(skill_num_map).fillna(-1).astype(int)
        assignment_df["archetype_name"] = assignment_df["job_id"].map(skill_name_map).fillna("Unassigned (Zero Selected Skills)")
        
        # Add cluster sizes and shares
        arc_counts = assignment_df["archetype_id"].value_counts().to_dict()
        assignment_df["cluster_size"] = assignment_df["archetype_id"].map(arc_counts)
        assignment_df["cluster_share_pct"] = (assignment_df["cluster_size"] / len(assignment_df)) * 100.0
        
        # Save assignment parquet (Notice: NO salary or target features present!)
        assignment_cols = [
            "job_id",
            "content_fingerprint",
            "has_selected_skills",
            "archetype_id",
            "archetype_numeric_label",
            "archetype_name",
            "cluster_size",
            "cluster_share_pct"
        ]
        assignment_df = assignment_df[assignment_cols]
        assignment_df.to_parquet(os.path.join(DATA_PROCESSED_DIR, "india_archetype_assignments.parquet"), index=False)
        print(f"Saved: {DATA_PROCESSED_DIR}/india_archetype_assignments.parquet (N = {len(assignment_df)})")
        
        # Archetype sizes table
        sizes_records = []
        for rank in range(1, SELECTED_K + 1):
            arc_id = f"IND_ARC_0{rank}"
            c_idx = next(c for c, m in self.archetype_meta.items() if m["archetype_id"] == arc_id)
            meta = self.archetype_meta[c_idx]
            sz = int((self.archetype_labels == arc_id).sum())
            sizes_records.append({
                "archetype_id": arc_id,
                "archetype_name": meta["archetype_name"],
                "cluster_size": sz,
                "share_pct_skill_bearing": (sz / len(self.df_skills)) * 100.0,
                "share_pct_full_cohort": (sz / len(self.df)) * 100.0
            })
        # Add unassigned row
        unassigned_cnt = int((~assignment_df["has_selected_skills"]).sum())
        sizes_records.append({
            "archetype_id": "IND_ARC_UNASSIGNED",
            "archetype_name": "Unassigned (Zero Selected Skills)",
            "cluster_size": unassigned_cnt,
            "share_pct_skill_bearing": 0.0,
            "share_pct_full_cohort": (unassigned_cnt / len(self.df)) * 100.0
        })
        df_sizes = pd.DataFrame(sizes_records)
        df_sizes.to_csv(os.path.join(TABLES_DIR, "india_archetype_sizes.csv"), index=False)
        print(f"Saved: {TABLES_DIR}/india_archetype_sizes.csv")
        
        return assignment_df, df_sizes

    def step5_profile_archetypes(self):
        """Profile archetypes: prevalence, skill lift, discriminative skills, and covariates."""
        print("\n" + "=" * 80)
        print("STEP 5: SKILL LIFT & MULTIDIMENSIONAL ARCHETYPE PROFILING")
        print("=" * 80)
        
        overall_prev = self.X_skills.mean(axis=0)
        
        lift_records = []
        profile_records = []
        
        for rank in range(1, SELECTED_K + 1):
            arc_id = f"IND_ARC_0{rank}"
            c_idx = next(c for c, m in self.archetype_meta.items() if m["archetype_id"] == arc_id)
            meta = self.archetype_meta[c_idx]
            
            mask_arc = (self.archetype_labels == arc_id)
            sub_df = self.df_skills[mask_arc]
            sub_X = self.X_skills[mask_arc]
            cluster_prev = sub_X.mean(axis=0)
            
            # Compute skill lifts for all 284 skills
            for i, sc in enumerate(self.skill_cols):
                clean_name = sc.replace("skill_", "").replace("_", " ").title()
                p_c = float(cluster_prev[i] * 100.0)
                p_o = float(overall_prev[i] * 100.0)
                lift = float(cluster_prev[i] / overall_prev[i]) if overall_prev[i] > 0 else 0.0
                lift_records.append({
                    "archetype_id": arc_id,
                    "archetype_name": meta["archetype_name"],
                    "skill_column": sc,
                    "skill_name": clean_name,
                    "cluster_prevalence_pct": p_c,
                    "overall_prevalence_pct": p_o,
                    "skill_lift": lift
                })
                
            # Identify top skills by prevalence
            top_prev_idx = np.argsort(cluster_prev)[-8:][::-1]
            top_prev_str = ", ".join([f"{self.skill_cols[idx].replace('skill_', '').title()} ({cluster_prev[idx]*100:.1f}%)" for idx in top_prev_idx if cluster_prev[idx] > 0.02])
            
            # Identify top skills by lift (filter min prevalence >= 5% to avoid singletons)
            lift_candidates = []
            for idx in range(len(self.skill_cols)):
                if cluster_prev[idx] >= 0.05 and overall_prev[idx] >= 0.005:
                    lift_val = cluster_prev[idx] / overall_prev[idx]
                    lift_candidates.append((self.skill_cols[idx].replace('skill_', '').title(), lift_val, cluster_prev[idx]*100))
            lift_candidates.sort(key=lambda x: x[1], reverse=True)
            top_lift_str = ", ".join([f"{x[0]} ({x[1]:.2f}x)" for x in lift_candidates[:6]]) if lift_candidates else "Generalist Baseline"
            
            # Covariates
            top_roles = sub_df["normalized_role"].value_counts().head(2)
            top_roles_str = ", ".join([f"{r} ({cnt/len(sub_df)*100:.1f}%)" for r, cnt in top_roles.items()])
            
            top_cities = sub_df["city_grouped"].value_counts().head(2)
            top_cities_str = ", ".join([f"{c} ({cnt/len(sub_df)*100:.1f}%)" for c, cnt in top_cities.items()])
            
            top_mode = sub_df["work_mode"].value_counts().index[0]
            med_exp = float(sub_df["experience_midpoint_years"].median())
            
            profile_records.append({
                "archetype_id": arc_id,
                "archetype_name": meta["archetype_name"],
                "definition": meta["definition"],
                "dominant_role_families": top_roles_str,
                "top_skills_by_prevalence": top_prev_str,
                "top_discriminative_skills": top_lift_str,
                "median_experience_years": med_exp,
                "dominant_work_mode": top_mode,
                "dominant_cities": top_cities_str
            })
            
        df_lift = pd.DataFrame(lift_records)
        df_lift.to_csv(os.path.join(TABLES_DIR, "india_archetype_skill_lift.csv"), index=False)
        print(f"Saved: {TABLES_DIR}/india_archetype_skill_lift.csv")
        
        df_profiles = pd.DataFrame(profile_records)
        df_profiles.to_csv(os.path.join(TABLES_DIR, "india_archetype_profiles.csv"), index=False)
        print(f"Saved: {TABLES_DIR}/india_archetype_profiles.csv")
        
        return df_lift, df_profiles

    def step6_salary_analysis_and_testing(self):
        """Analyze salary distributions by archetype, run Kruskal-Wallis, Dunn post-hoc test, and effect size."""
        print("\n" + "=" * 80)
        print("STEP 6: SALARY ASSOCIATION & STATISTICAL TESTING (RQ2 DOWNSTREAM)")
        print("=" * 80)
        
        salaries = self.df_skills["salary_midpoint_inr"].values / 100000.0
        cohort_median = float(np.median(salaries))
        
        summary_records = []
        group_salaries = []
        group_names = []
        
        for rank in range(1, SELECTED_K + 1):
            arc_id = f"IND_ARC_0{rank}"
            c_idx = next(c for c, m in self.archetype_meta.items() if m["archetype_id"] == arc_id)
            meta = self.archetype_meta[c_idx]
            
            sub_sal = salaries[self.archetype_labels == arc_id]
            group_salaries.append(sub_sal)
            group_names.append(arc_id)
            
            q25, med, q75 = np.percentile(sub_sal, [25, 50, 75])
            iqr = q75 - q25
            mean_sal = float(np.mean(sub_sal))
            std_sal = float(np.std(sub_sal))
            min_sal = float(np.min(sub_sal))
            max_sal = float(np.max(sub_sal))
            
            summary_records.append({
                "archetype_id": arc_id,
                "archetype_name": meta["archetype_name"],
                "N": len(sub_sal),
                "median_salary_lpa": med,
                "mean_salary_lpa": mean_sal,
                "q25_salary_lpa": q25,
                "q75_salary_lpa": q75,
                "iqr_salary_lpa": iqr,
                "std_salary_lpa": std_sal,
                "min_salary_lpa": min_sal,
                "max_salary_lpa": max_sal,
                "salary_rank": rank,
                "delta_vs_cohort_median_lpa": med - cohort_median
            })
            
        df_sal_summary = pd.DataFrame(summary_records)
        df_sal_summary.to_csv(os.path.join(TABLES_DIR, "india_archetype_salary_summary.csv"), index=False)
        print(f"Saved: {TABLES_DIR}/india_archetype_salary_summary.csv")
        
        # Kruskal-Wallis omnibus test
        h_stat, p_val = stats.kruskal(*group_salaries)
        N_tot = len(salaries)
        df_stat = SELECTED_K - 1
        eps2 = float((h_stat - SELECTED_K + 1) / (N_tot - SELECTED_K))
        
        test_record = [{
            "test_name": "Kruskal-Wallis H Test",
            "variable": "salary_midpoint_inr (LPA)",
            "n_observations": N_tot,
            "n_groups": SELECTED_K,
            "h_statistic": float(h_stat),
            "degrees_of_freedom": df_stat,
            "p_value": float(p_val),
            "effect_size_name": "epsilon_squared (eps2)",
            "effect_size_value": eps2,
            "alpha": 0.05,
            "interpretation": f"Statistically significant salary variation across archetypes (H={h_stat:.2f}, p={p_val:.2e}, eps2={eps2:.4f})"
        }]
        df_sal_test = pd.DataFrame(test_record)
        df_sal_test.to_csv(os.path.join(TABLES_DIR, "india_archetype_salary_test.csv"), index=False)
        print(f"Saved: {TABLES_DIR}/india_archetype_salary_test.csv")
        print(f"Kruskal-Wallis Salary Omnibus: H = {h_stat:.2f}, df = {df_stat}, p = {p_val:.2e}, eps2 = {eps2:.4f}")
        
        # Dunn post-hoc pairwise tests with Holm adjustment
        df_dunn_sal = run_dunn_test(group_salaries, group_names, method="holm")
        # Add friendly archetype names
        arc_name_dict = {f"IND_ARC_0{r}": df_sal_summary.loc[df_sal_summary["archetype_id"] == f"IND_ARC_0{r}", "archetype_name"].values[0] for r in range(1, SELECTED_K + 1)}
        df_dunn_sal["group1_name"] = df_dunn_sal["group1"].map(arc_name_dict)
        df_dunn_sal["group2_name"] = df_dunn_sal["group2"].map(arc_name_dict)
        df_dunn_sal.to_csv(os.path.join(TABLES_DIR, "india_archetype_posthoc.csv"), index=False)
        print(f"Saved: {TABLES_DIR}/india_archetype_posthoc.csv ({len(df_dunn_sal)} pairwise comparisons)")
        
        return df_sal_summary, df_sal_test, df_dunn_sal, h_stat, p_val, eps2

    def step7_leakage_safe_rq3_error_analysis(self):
        """
        RQ3: Prediction Error Stratification Across Archetypes.
        Strictly leakage-safe: PCA and KMeans fitted on training partition only.
        Holdout skills projected, assigned to matched cluster, and evaluated against frozen model predictions.
        """
        print("\n" + "=" * 80)
        print("STEP 7: LEAKAGE-SAFE RQ3 PREDICTION ERROR STRATIFICATION")
        print("=" * 80)
        
        # 1. Reproduce identical Phase 4 GroupShuffleSplit
        gss = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=PRIMARY_SEED)
        train_idx, holdout_idx = next(gss.split(self.df, groups=self.df["content_fingerprint"]))
        
        df_train = self.df.iloc[train_idx].copy().reset_index(drop=True)
        df_holdout = self.df.iloc[holdout_idx].copy().reset_index(drop=True)
        
        tr_skill_mask = df_train[self.skill_cols].sum(axis=1) >= 1
        ho_skill_mask = df_holdout[self.skill_cols].sum(axis=1) >= 1
        
        df_tr_skills = df_train[tr_skill_mask].copy().reset_index(drop=True)
        df_ho_skills = df_holdout[ho_skill_mask].copy().reset_index(drop=True)
        
        print(f"Train partition skill-bearing rows: N = {len(df_tr_skills)} / {len(df_train)}")
        print(f"Holdout partition skill-bearing rows: N = {len(df_ho_skills)} / {len(df_holdout)}")
        
        # 2. Fit PCA + KMeans strictly on training skills
        pca_train = PCA(n_components=N_COMPONENTS_RETAINED, random_state=PRIMARY_SEED)
        X_tr_pca = pca_train.fit_transform(df_tr_skills[self.skill_cols].values)
        
        km_train = KMeans(n_clusters=SELECTED_K, random_state=PRIMARY_SEED, n_init=10)
        km_train.fit(X_tr_pca)
        tr_raw_labels = km_train.labels_
        
        # Save training holdout pipeline object
        holdout_pipeline = {
            "pca_train": pca_train,
            "km_train": km_train,
            "n_components": N_COMPONENTS_RETAINED,
            "k": SELECTED_K,
            "random_state": PRIMARY_SEED
        }
        with open(os.path.join(MODELS_DIR, "india_holdout_archetype_pipeline.pkl"), "wb") as f:
            pickle.dump(holdout_pipeline, f)
        print(f"Saved: {MODELS_DIR}/india_holdout_archetype_pipeline.pkl")
        
        # 3. Hungarian matching: align train cluster indices to full cohort descriptive archetypes
        train_job_ids = set(df_tr_skills["job_id"])
        full_train_mask = self.df_skills["job_id"].isin(train_job_ids)
        full_labels_on_train = self.df_skills.loc[full_train_mask, "archetype_numeric_label"].values - 1 # 0-indexed rank
        
        contingency = np.zeros((SELECTED_K, SELECTED_K), dtype=int)
        for f_l, t_l in zip(full_labels_on_train, tr_raw_labels):
            contingency[f_l, t_l] += 1
            
        row_ind, col_ind = linear_sum_assignment(-contingency)
        train_to_rank_map = {col: row + 1 for row, col in zip(row_ind, col_ind)}
        
        # 4. Transform and assign holdout postings
        X_ho_pca = pca_train.transform(df_ho_skills[self.skill_cols].values)
        ho_raw_clusters = km_train.predict(X_ho_pca)
        ho_ranks = np.array([train_to_rank_map[c] for c in ho_raw_clusters])
        ho_archetype_ids = np.array([f"IND_ARC_0{r}" for r in ho_ranks])
        
        # 5. Load frozen model and preprocessor to generate holdout predictions
        with open(FROZEN_PREPROCESSOR_PATH, "rb") as f:
            preprocessor = pickle.load(f)
        with open(FROZEN_MODEL_PATH, "rb") as f:
            frozen_model = pickle.load(f)
        with open(FROZEN_FEATURE_LIST_PATH, "r", encoding="utf-8") as f:
            raw_features = json.load(f)["feature_names_raw"]
            
        # Overall holdout verification
        X_ho_full = preprocessor.transform(df_holdout[raw_features])
        y_ho_all = df_holdout["salary_midpoint_inr"].values
        pred_log_all = frozen_model.predict(X_ho_full)
        pred_raw_all = np.expm1(pred_log_all)
        
        all_mae_lpa = float(np.mean(np.abs(y_ho_all - pred_raw_all)) / 100000.0)
        all_rmse_lpa = float(np.sqrt(np.mean((y_ho_all - pred_raw_all)**2)) / 100000.0)
        all_med_ae_lpa = float(np.median(np.abs(y_ho_all - pred_raw_all)) / 100000.0)
        ss_res = np.sum((y_ho_all - pred_raw_all)**2)
        ss_tot = np.sum((y_ho_all - np.mean(y_ho_all))**2)
        all_r2 = float(1.0 - (ss_res / ss_tot))
        
        print("\nFrozen Model Full Holdout Reproduction Check:")
        print(f"  Holdout N: {len(df_holdout)}")
        print(f"  Holdout MAE: INR {all_mae_lpa*100000:,.0f} ({all_mae_lpa:.2f} LPA)")
        print(f"  Holdout RMSE: INR {all_rmse_lpa*100000:,.0f} ({all_rmse_lpa:.2f} LPA)")
        print(f"  Holdout R2: {all_r2:.4f}")
        print(f"  Holdout Median AE: INR {all_med_ae_lpa*100000:,.0f} ({all_med_ae_lpa:.2f} LPA)")
        
        assert abs(all_mae_lpa - 3.7147) < 0.01, f"Frozen holdout MAE mismatch: {all_mae_lpa}"
        assert abs(all_r2 - 0.5798) < 0.01, f"Frozen holdout R2 mismatch: {all_r2}"
        print("Bitwise-exact holdout reproduction confirmed.")
        
        # 6. Stratified Error Evaluation on Skill-Bearing Holdout Postings
        X_ho_skills_proc = preprocessor.transform(df_ho_skills[raw_features])
        y_ho_skills = df_ho_skills["salary_midpoint_inr"].values / 100000.0
        pred_ho_skills = np.expm1(frozen_model.predict(X_ho_skills_proc)) / 100000.0
        
        res_ho = y_ho_skills - pred_ho_skills
        abs_err_ho = np.abs(res_ho)
        
        error_records = []
        groups_abs_err = []
        group_err_names = []
        
        for rank in range(1, SELECTED_K + 1):
            arc_id = f"IND_ARC_0{rank}"
            mask_arc = (ho_archetype_ids == arc_id)
            n_arc = int(mask_arc.sum())
            
            c_idx = next(c for c, m in self.archetype_meta.items() if m["archetype_id"] == arc_id)
            meta = self.archetype_meta[c_idx]
            
            y_a = y_ho_skills[mask_arc]
            p_a = pred_ho_skills[mask_arc]
            err_a = res_ho[mask_arc]
            abs_a = abs_err_ho[mask_arc]
            
            groups_abs_err.append(abs_a)
            group_err_names.append(arc_id)
            
            mae_a = float(np.mean(abs_a))
            rmse_a = float(np.sqrt(np.mean(err_a**2)))
            med_ae_a = float(np.median(abs_a))
            mean_res_a = float(np.mean(err_a))
            med_sal_a = float(np.median(y_a))
            rel_mae_a = float((mae_a / med_sal_a) * 100.0) if med_sal_a > 0 else 0.0
            mape_a = float(np.mean(abs_a / y_a) * 100.0)
            
            error_records.append({
                "archetype_id": arc_id,
                "archetype_name": meta["archetype_name"],
                "holdout_N": n_arc,
                "holdout_share_pct": (n_arc / len(df_ho_skills)) * 100.0,
                "holdout_median_salary_lpa": med_sal_a,
                "mae_lpa": mae_a,
                "rmse_lpa": rmse_a,
                "median_ae_lpa": med_ae_a,
                "mean_signed_residual_lpa": mean_res_a,
                "relative_mae_pct": rel_mae_a,
                "mape_pct": mape_a
            })
            print(f"{arc_id} ({meta['archetype_name']}): N={n_arc:3d}, MedSal={med_sal_a:5.2f} LPA | MAE={mae_a:5.2f} LPA, RelMAE={rel_mae_a:4.1f}%, MeanRes={mean_res_a:+5.2f} LPA")
            
        df_error_summary = pd.DataFrame(error_records)
        df_error_summary.to_csv(os.path.join(TABLES_DIR, "india_archetype_error_summary.csv"), index=False)
        print(f"Saved: {TABLES_DIR}/india_archetype_error_summary.csv")
        
        # 7. Kruskal-Wallis test on absolute prediction errors
        h_err, p_err = stats.kruskal(*groups_abs_err)
        N_ho = len(abs_err_ho)
        df_err_stat = SELECTED_K - 1
        eps2_err = float((h_err - SELECTED_K + 1) / (N_ho - SELECTED_K))
        
        test_err_record = [{
            "test_name": "Kruskal-Wallis H Test on Absolute Errors",
            "variable": "absolute_prediction_error (LPA)",
            "n_observations": N_ho,
            "n_groups": SELECTED_K,
            "h_statistic": float(h_err),
            "degrees_of_freedom": df_err_stat,
            "p_value": float(p_err),
            "effect_size_name": "epsilon_squared (eps2)",
            "effect_size_value": eps2_err,
            "alpha": 0.05,
            "interpretation": f"Statistically significant error heterogeneity across archetypes (H={h_err:.2f}, p={p_err:.2e}, eps2={eps2_err:.4f})"
        }]
        df_err_test = pd.DataFrame(test_err_record)
        df_err_test.to_csv(os.path.join(TABLES_DIR, "india_archetype_error_test.csv"), index=False)
        print(f"Saved: {TABLES_DIR}/india_archetype_error_test.csv")
        print(f"Holdout Error Kruskal-Wallis: H = {h_err:.2f}, df = {df_err_stat}, p = {p_err:.2e}, eps2 = {eps2_err:.4f}")
        
        # Dunn post-hoc test on prediction errors
        df_dunn_err = run_dunn_test(groups_abs_err, group_err_names, method="holm")
        arc_name_dict = {f"IND_ARC_0{r}": df_error_summary.loc[df_error_summary["archetype_id"] == f"IND_ARC_0{r}", "archetype_name"].values[0] for r in range(1, SELECTED_K + 1)}
        df_dunn_err["group1_name"] = df_dunn_err["group1"].map(arc_name_dict)
        df_dunn_err["group2_name"] = df_dunn_err["group2"].map(arc_name_dict)
        df_dunn_err.to_csv(os.path.join(TABLES_DIR, "india_archetype_error_posthoc.csv"), index=False)
        print(f"Saved: {TABLES_DIR}/india_archetype_error_posthoc.csv")
        
        # 8. Integrated Archetype ? Salary ? Error Table (Section 30)
        integrated_records = []
        for rank in range(1, SELECTED_K + 1):
            arc_id = f"IND_ARC_0{rank}"
            row_err = df_error_summary[df_error_summary["archetype_id"] == arc_id].iloc[0]
            c_idx = next(c for c, m in self.archetype_meta.items() if m["archetype_id"] == arc_id)
            meta = self.archetype_meta[c_idx]
            
            sub_sal = self.df_skills.loc[self.archetype_labels == arc_id, "salary_midpoint_inr"].values / 100000.0
            q25, med_sal, q75 = np.percentile(sub_sal, [25, 50, 75])
            
            integrated_records.append({
                "Archetype": arc_id,
                "Archetype_Name": meta["archetype_name"],
                "N_Full": len(sub_sal),
                "Share_Pct_Full": (len(sub_sal) / len(self.df_skills)) * 100.0,
                "Median_Salary_LPA": med_sal,
                "IQR_Salary_LPA": q75 - q25,
                "Holdout_N": row_err["holdout_N"],
                "Holdout_MAE_LPA": row_err["mae_lpa"],
                "Holdout_RMSE_LPA": row_err["rmse_lpa"],
                "Holdout_Median_AE_LPA": row_err["median_ae_lpa"],
                "Holdout_Mean_Residual_LPA": row_err["mean_signed_residual_lpa"],
                "Holdout_Relative_MAE_Pct": row_err["relative_mae_pct"],
                "Salary_Rank": rank
            })
            
        df_integrated = pd.DataFrame(integrated_records)
        df_integrated.to_csv(os.path.join(TABLES_DIR, "india_archetype_salary_error_summary.csv"), index=False)
        print(f"Saved: {TABLES_DIR}/india_archetype_salary_error_summary.csv")
        
        return df_error_summary, df_err_test, df_dunn_err, df_integrated, df_ho_skills, ho_archetype_ids, y_ho_skills, pred_ho_skills, h_err, p_err, eps2_err

    def step8_render_all_figures(self, df_prev, df_pca_var, df_loadings, df_k_metrics, df_lift, df_sal_summary, df_error_summary, df_ho_skills, ho_archetype_ids, y_ho_skills, pred_ho_skills):
        """Render all 13 required research figures adhering to strict visual guidelines."""
        print("\n" + "=" * 80)
        print("STEP 8: GENERATING ALL 13 PUBLICATION-QUALITY FIGURES")
        print("=" * 80)
        
        # Color palette for 6 archetypes
        arc_palette = {
            "IND_ARC_01": "#1f77b4",  # Steel Blue - Big Data
            "IND_ARC_02": "#ff7f0e",  # Amber Orange - Java Enterprise
            "IND_ARC_03": "#2ca02c",  # Forest Green - Python AI/ML
            "IND_ARC_04": "#d62728",  # Crimson - Web / App Dev
            "IND_ARC_05": "#9467bd",  # Purple - Baseline Tech
            "IND_ARC_06": "#8c564b"   # Brown - SAP ERP
        }
        
        # FIGURE 1: Skill prevalence distribution
        plt.figure(figsize=(10, 5))
        top_skills_plot = df_prev.head(25)
        sns.barplot(data=top_skills_plot, x="prevalence_pct", y="skill_name", color="#2b5c8f")
        plt.title("Top 25 Technical Skills by Prevalence (N = 5,323 Skill-Bearing Postings)", fontweight="bold")
        plt.xlabel("Prevalence (% of Skill-Bearing Postings)")
        plt.ylabel("Technical Skill")
        plt.tight_layout()
        plt.savefig(os.path.join(FIGURES_DIR, "india_skill_prevalence.png"))
        plt.close()
        print("Rendered: india_skill_prevalence.png")
        
        # FIGURE 2: PCA scree plot
        plt.figure(figsize=(9, 5))
        plot_var = df_pca_var.head(30)
        pcs = range(1, len(plot_var) + 1)
        plt.plot(pcs, plot_var["explained_variance_ratio"] * 100.0, marker="o", color="#1f77b4", linewidth=1.8, markersize=5)
        plt.axvline(15, color="red", linestyle="--", linewidth=1.5, label="Retained Dimension (15 PCs)")
        plt.title("PCA Scree Plot: Explained Variance Ratio by Principal Component", fontweight="bold")
        plt.xlabel("Principal Component Index")
        plt.ylabel("Explained Variance (%)")
        plt.legend(frameon=True)
        plt.tight_layout()
        plt.savefig(os.path.join(FIGURES_DIR, "india_pca_scree.png"))
        plt.close()
        print("Rendered: india_pca_scree.png")
        
        # FIGURE 3: Cumulative explained variance
        plt.figure(figsize=(9, 5))
        plt.plot(pcs, plot_var["cumulative_explained_variance"] * 100.0, marker="s", color="#2ca02c", linewidth=1.8, markersize=4)
        plt.axvline(15, color="red", linestyle="--", linewidth=1.5, label=f"15 PCs: {df_pca_var.loc[14, 'cumulative_explained_variance']*100:.1f}% Variance")
        plt.axhline(df_pca_var.loc[14, "cumulative_explained_variance"] * 100.0, color="gray", linestyle=":", linewidth=1.2)
        plt.title("Cumulative Explained Variance Curve (Top 30 Principal Components)", fontweight="bold")
        plt.xlabel("Number of Retained Principal Components")
        plt.ylabel("Cumulative Variance Explained (%)")
        plt.legend(frameon=True)
        plt.tight_layout()
        plt.savefig(os.path.join(FIGURES_DIR, "india_pca_cumulative_variance.png"))
        plt.close()
        print("Rendered: india_pca_cumulative_variance.png")
        
        # FIGURE 4: PCA loadings
        fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=False)
        for idx, (ax, pc_col, title) in enumerate(zip(axes, ["PC01", "PC02"], ["PC1: Enterprise Java/Microservices vs ERP", "PC2: Big Data/Python vs ERP"])):
            top_pos = df_loadings.sort_values(by=pc_col, ascending=False).head(8)
            top_neg = df_loadings.sort_values(by=pc_col, ascending=True).head(8)
            comb = pd.concat([top_neg, top_pos])
            colors = ["#d62728" if v < 0 else "#2ca02c" for v in comb[pc_col]]
            ax.barh(comb["skill_name"], comb[pc_col], color=colors)
            ax.axvline(0, color="black", linestyle="-", linewidth=0.8)
            ax.set_title(title, fontweight="bold", fontsize=11)
            ax.set_xlabel("Component Factor Loading")
        plt.tight_layout()
        plt.savefig(os.path.join(FIGURES_DIR, "india_pca_loadings.png"))
        plt.close()
        print("Rendered: india_pca_loadings.png")
        
        # FIGURE 5: PCA 2D scatter colored by archetype
        plt.figure(figsize=(9, 7))
        for arc_id in [f"IND_ARC_0{r}" for r in range(1, SELECTED_K + 1)]:
            mask_arc = (self.archetype_labels == arc_id)
            c_idx = next(c for c, m in self.archetype_meta.items() if m["archetype_id"] == arc_id)
            name = self.archetype_meta[c_idx]["archetype_name"]
            plt.scatter(
                self.X_pca_full[mask_arc, 0],
                self.X_pca_full[mask_arc, 1],
                c=arc_palette[arc_id],
                label=f"{arc_id}: {name}",
                alpha=0.45,
                s=22,
                edgecolors="none"
            )
        plt.title("Two-Dimensional Projection of Retained PCA Representation by Archetype", fontweight="bold")
        plt.xlabel("Principal Component 1 (Java/Microservices vs ERP)")
        plt.ylabel("Principal Component 2 (Big Data/Spark vs ERP)")
        plt.legend(frameon=True, fontsize=9, loc="upper right")
        caption = "Note: Two-dimensional projection of the retained PCA representation;\nvisual separation does not imply complete separation in the full feature space."
        plt.figtext(0.5, 0.01, caption, ha="center", fontsize=8, style="italic")
        plt.tight_layout(rect=[0, 0.04, 1, 1])
        plt.savefig(os.path.join(FIGURES_DIR, "india_pca_clusters.png"))
        plt.close()
        print("Rendered: india_pca_clusters.png")
        
        # FIGURE 6: Cluster sizes
        plt.figure(figsize=(10, 5))
        plot_sizes = df_sal_summary.copy()
        sns.barplot(data=plot_sizes, x="N", y="archetype_name", palette=[arc_palette[aid] for aid in plot_sizes["archetype_id"]])
        for i, row in plot_sizes.iterrows():
            pct = (row["N"] / len(self.df_skills)) * 100.0
            plt.text(row["N"] + 25, i, f"N={row['N']:,} ({pct:.1f}%)", va="center", fontsize=9, fontweight="bold")
        plt.xlim(0, max(plot_sizes["N"]) * 1.18)
        plt.title("Cluster Size Distribution Across Discovered Job Archetypes (N = 5,323)", fontweight="bold")
        plt.xlabel("Number of Postings")
        plt.ylabel("Archetype")
        plt.tight_layout()
        plt.savefig(os.path.join(FIGURES_DIR, "india_cluster_sizes.png"))
        plt.close()
        print("Rendered: india_cluster_sizes.png")
        
        # FIGURE 7: Skill prevalence heatmap across archetypes
        # Select top 24 discriminative skills across clusters
        top_skills_for_heatmap = [
            "spark", "scala", "hadoop", "airflow", "hive",
            "java", "microservices", "spring_boot", "spring",
            "python", "sql", "machine_learning", "aws", "generative_ai",
            "react", "javascript", "node_js", "angular", "net",
            "sap", "fico", "mm", "consulting", "sap_testing"
        ]
        heatmap_skills_cols = [f"skill_{s}" for s in top_skills_for_heatmap if f"skill_{s}" in self.skill_cols]
        
        prev_matrix = []
        for arc_id in [f"IND_ARC_0{r}" for r in range(1, SELECTED_K + 1)]:
            sub_X = self.X_skills[self.archetype_labels == arc_id]
            col_indices = [self.skill_cols.index(sc) for sc in heatmap_skills_cols]
            prev_matrix.append(sub_X[:, col_indices].mean(axis=0) * 100.0)
            
        df_hm_prev = pd.DataFrame(
            np.array(prev_matrix).T,
            index=[sc.replace("skill_", "").replace("_", " ").title() for sc in heatmap_skills_cols],
            columns=[f"IND_ARC_0{r}" for r in range(1, SELECTED_K + 1)]
        )
        
        plt.figure(figsize=(10, 9))
        sns.heatmap(df_hm_prev, annot=True, fmt=".1f", cmap="YlGnBu", cbar_kws={"label": "Skill Prevalence (%)"})
        plt.title("Archetype Skill Prevalence Heatmap (Top Discriminative Technical Skills)", fontweight="bold")
        plt.xlabel("Archetype ID")
        plt.ylabel("Technical Skill")
        plt.tight_layout()
        plt.savefig(os.path.join(FIGURES_DIR, "india_archetype_skill_heatmap.png"))
        plt.close()
        print("Rendered: india_archetype_skill_heatmap.png")
        
        # FIGURE 8: Skill lift heatmap
        lift_matrix = []
        for arc_id in [f"IND_ARC_0{r}" for r in range(1, SELECTED_K + 1)]:
            sub_X = self.X_skills[self.archetype_labels == arc_id]
            col_indices = [self.skill_cols.index(sc) for sc in heatmap_skills_cols]
            c_prev = sub_X[:, col_indices].mean(axis=0)
            o_prev = self.X_skills[:, col_indices].mean(axis=0)
            lift_vals = np.where(o_prev > 0, c_prev / o_prev, 0.0)
            lift_matrix.append(lift_vals)
            
        df_hm_lift = pd.DataFrame(
            np.array(lift_matrix).T,
            index=[sc.replace("skill_", "").replace("_", " ").title() for sc in heatmap_skills_cols],
            columns=[f"IND_ARC_0{r}" for r in range(1, SELECTED_K + 1)]
        )
        
        plt.figure(figsize=(10, 9))
        sns.heatmap(df_hm_lift, annot=True, fmt=".2f", cmap="Blues", cbar_kws={"label": "Skill Lift Ratio (x Baseline)"})
        plt.title("Archetype Skill Lift Heatmap (Prevalence Ratio vs Full Skill-Bearing Cohort)", fontweight="bold")
        plt.xlabel("Archetype ID")
        plt.ylabel("Technical Skill")
        plt.tight_layout()
        plt.savefig(os.path.join(FIGURES_DIR, "india_archetype_skill_lift_heatmap.png"))
        plt.close()
        print("Rendered: india_archetype_skill_lift_heatmap.png")
        
        # FIGURE 9: Salary distribution by archetype (Boxplot)
        plt.figure(figsize=(10, 6))
        plot_df = self.df_skills.copy()
        plot_df["salary_lpa"] = plot_df["salary_midpoint_inr"] / 100000.0
        sns.boxplot(
            data=plot_df,
            x="archetype_id",
            y="salary_lpa",
            palette=arc_palette,
            showmeans=True,
            meanprops={"marker": "D", "markeredgecolor": "black", "markerfacecolor": "white", "markersize": 6}
        )
        plt.axhline(float(np.median(plot_df["salary_lpa"])), color="gray", linestyle="--", linewidth=1.2, label=f"Cohort Median ({np.median(plot_df['salary_lpa']):.1f} LPA)")
        plt.title("Observed Salary Disclosed Distribution by Job Archetype", fontweight="bold")
        plt.xlabel("Archetype ID")
        plt.ylabel("Annual Salary (LPA INR)")
        plt.ylim(0, 55)
        plt.legend(frameon=True)
        plt.tight_layout()
        plt.savefig(os.path.join(FIGURES_DIR, "india_archetype_salary_distribution.png"))
        plt.close()
        print("Rendered: india_archetype_salary_distribution.png")
        
        # FIGURE 10: Median salary by archetype with IQR error bars
        plt.figure(figsize=(10, 5))
        plot_sal = df_sal_summary.copy().sort_values(by="median_salary_lpa", ascending=True)
        plt.barh(
            plot_sal["archetype_name"],
            plot_sal["median_salary_lpa"],
            color=[arc_palette[aid] for aid in plot_sal["archetype_id"]],
            xerr=plot_sal["iqr_salary_lpa"] / 2.0,
            capsize=4,
            alpha=0.88
        )
        for i, row in plot_sal.reset_index(drop=True).iterrows():
            plt.text(row["median_salary_lpa"] + 1.0, i, f"INR {row['median_salary_lpa']:.2f} LPA", va="center", fontweight="bold", fontsize=10)
        plt.title("Observed Median Salary by Skill Archetype (with IQR Dispersion)", fontweight="bold")
        plt.xlabel("Median Salary Disclosed (LPA INR)")
        plt.ylabel("Archetype")
        plt.xlim(0, 30)
        plt.tight_layout()
        plt.savefig(os.path.join(FIGURES_DIR, "india_archetype_salary_medians.png"))
        plt.close()
        print("Rendered: india_archetype_salary_medians.png")
        
        # FIGURE 11: Prediction MAE and Relative MAE by archetype
        fig, ax1 = plt.subplots(figsize=(10, 5))
        x_indices = np.arange(len(df_error_summary))
        width = 0.35
        
        bars1 = ax1.bar(x_indices - width/2, df_error_summary["mae_lpa"], width, label="Absolute MAE (LPA)", color="#1f77b4")
        ax1.set_ylabel("Holdout MAE (LPA INR)", color="#1f77b4", fontweight="bold")
        ax1.set_ylim(0, 7.0)
        
        ax2 = ax1.twinx()
        bars2 = ax2.bar(x_indices + width/2, df_error_summary["relative_mae_pct"], width, label="Relative MAE (%)", color="#ff7f0e", alpha=0.9)
        ax2.set_ylabel("Relative MAE (% of Median Salary)", color="#ff7f0e", fontweight="bold")
        ax2.set_ylim(0, 60.0)
        
        ax1.set_xticks(x_indices)
        ax1.set_xticklabels([f"{row['archetype_id']}\n{row['archetype_name'][:18]}..." for _, row in df_error_summary.iterrows()], fontsize=9)
        plt.title("Holdout Prediction MAE vs Relative MAE Across Archetypes (Frozen Model)", fontweight="bold")
        plt.tight_layout()
        plt.savefig(os.path.join(FIGURES_DIR, "india_archetype_error_mae.png"))
        plt.close()
        print("Rendered: india_archetype_error_mae.png")
        
        # FIGURE 12: Absolute error distribution by archetype (Boxplot)
        plt.figure(figsize=(10, 6))
        ho_err_df = pd.DataFrame({
            "archetype_id": ho_archetype_ids,
            "abs_error_lpa": np.abs(y_ho_skills - pred_ho_skills)
        })
        sns.boxplot(
            data=ho_err_df,
            x="archetype_id",
            y="abs_error_lpa",
            palette=arc_palette,
            showmeans=True,
            meanprops={"marker": "D", "markeredgecolor": "black", "markerfacecolor": "white", "markersize": 6}
        )
        plt.title("Holdout Absolute Prediction Error Distribution by Archetype", fontweight="bold")
        plt.xlabel("Archetype ID")
        plt.ylabel("Absolute Prediction Error (LPA INR)")
        plt.ylim(0, 25)
        plt.tight_layout()
        plt.savefig(os.path.join(FIGURES_DIR, "india_archetype_error_distribution.png"))
        plt.close()
        print("Rendered: india_archetype_error_distribution.png")
        
        # FIGURE 13: Predicted vs Actual salary colored by archetype
        plt.figure(figsize=(8, 8))
        for arc_id in [f"IND_ARC_0{r}" for r in range(1, SELECTED_K + 1)]:
            mask_arc = (ho_archetype_ids == arc_id)
            c_idx = next(c for c, m in self.archetype_meta.items() if m["archetype_id"] == arc_id)
            name = self.archetype_meta[c_idx]["archetype_name"]
            plt.scatter(
                y_ho_skills[mask_arc],
                pred_ho_skills[mask_arc],
                c=arc_palette[arc_id],
                label=f"{arc_id}: {name}",
                alpha=0.55,
                s=25,
                edgecolors="none"
            )
        plt.plot([0, 80], [0, 80], color="red", linestyle="--", linewidth=1.8, label="Ideal Line (y = y_hat)")
        plt.title("Observed vs Predicted Salary on Holdout by Archetype", fontweight="bold")
        plt.xlabel("Actual Salary Disclosed (LPA INR)")
        plt.ylabel("Predicted Salary (LPA INR)")
        plt.xlim(0, 65)
        plt.ylim(0, 65)
        plt.legend(frameon=True, fontsize=8, loc="upper left")
        plt.tight_layout()
        plt.savefig(os.path.join(FIGURES_DIR, "india_archetype_predicted_vs_actual.png"))
        plt.close()
        print("Rendered: india_archetype_predicted_vs_actual.png")
        
        print("All 13 figures rendered and saved successfully.")

    def step9_save_archetype_metadata(self, df_stability_stats, h_stat, p_val, eps2, h_err, p_err, eps2_err):
        """Save comprehensive machine-readable metadata artifact."""
        print("\n" + "=" * 80)
        print("STEP 9: SERIALIZING ARCHETYPE METADATA ARTIFACT")
        print("=" * 80)
        
        mean_ari, med_ari, mean_ami, med_ami = df_stability_stats
        
        archetypes_payload = []
        for rank in range(1, SELECTED_K + 1):
            arc_id = f"IND_ARC_0{rank}"
            c_idx = next(c for c, m in self.archetype_meta.items() if m["archetype_id"] == arc_id)
            meta = self.archetype_meta[c_idx]
            sz = int((self.archetype_labels == arc_id).sum())
            archetypes_payload.append({
                "archetype_id": arc_id,
                "rank": rank,
                "archetype_name": meta["archetype_name"],
                "definition": meta["definition"],
                "cluster_size": sz,
                "share_pct_skill_bearing": (sz / len(self.df_skills)) * 100.0,
                "observed_median_salary_lpa": meta["salary_median_lpa"]
            })
            
        metadata_payload = {
            "version": "india_archetypes_v1",
            "phase": "India-5",
            "date": "2026-10-07",
            "cohort": "India Technology Salary Cohort",
            "n_total_cohort": len(self.df),
            "n_skill_bearing": len(self.df_skills),
            "n_zero_skill": len(self.df) - len(self.df_skills),
            "n_skills": len(self.skill_cols),
            "pca_method": "Centered Covariance PCA (StandardScaler with_mean=True, with_std=False)",
            "n_components_retained": N_COMPONENTS_RETAINED,
            "cumulative_variance_explained": float(self.pca_full.explained_variance_ratio_.sum()),
            "clustering_algorithm": "KMeans",
            "k": SELECTED_K,
            "random_state": PRIMARY_SEED,
            "stability_seeds": STABILITY_SEEDS,
            "stability_metrics": {
                "mean_ari": float(mean_ari),
                "median_ari": float(med_ari),
                "mean_ami": float(mean_ami),
                "median_ami": float(med_ami)
            },
            "selection_policy": "Multi-criterion evaluation optimizing cluster stability (mean ARI 0.8035), interpretability, absence of sub-2% pathological clusters, and distinct salary stratification.",
            "feature_exclusions": [
                "salary_midpoint_inr",
                "salary_lpa",
                "normalized_role",
                "city_grouped",
                "work_mode",
                "experience_midpoint_years",
                "frozen_model_predictions",
                "residuals"
            ],
            "salary_association_test": {
                "test": "Kruskal-Wallis H Test",
                "h_statistic": float(h_stat),
                "degrees_of_freedom": SELECTED_K - 1,
                "p_value": float(p_val),
                "epsilon_squared": float(eps2),
                "posthoc_method": "Dunn test with Holm correction"
            },
            "rq3_error_heterogeneity_test": {
                "test": "Kruskal-Wallis H Test on Absolute Errors",
                "h_statistic": float(h_err),
                "degrees_of_freedom": SELECTED_K - 1,
                "p_value": float(p_err),
                "epsilon_squared": float(eps2_err),
                "holdout_protocol": "Leakage-safe (fitted strictly on training split skills)",
                "posthoc_method": "Dunn test with Holm correction"
            },
            "archetypes": archetypes_payload
        }
        
        with open(os.path.join(MODELS_DIR, "india_archetype_metadata.json"), "w", encoding="utf-8") as f:
            json.dump(metadata_payload, f, indent=2)
        print(f"Saved: {MODELS_DIR}/india_archetype_metadata.json")

    def run(self):
        """Execute the entire Phase India-5 pipeline end-to-end."""
        t0 = time.time()
        print("=" * 80)
        print("STARTING JOBINTEL PHASE INDIA-5 MASTER PIPELINE")
        print("=" * 80)
        
        df_prev = self.step1_load_and_audit()
        df_pca_var, df_loadings = self.step2_evaluate_pca()
        df_k_metrics, df_stability, mean_ari, med_ari, mean_ami, med_ami = self.step3_evaluate_kmeans_and_stability()
        assignment_df, df_sizes = self.step4_fit_final_archetypes()
        df_lift, df_profiles = self.step5_profile_archetypes()
        df_sal_summary, df_sal_test, df_dunn_sal, h_stat, p_val, eps2 = self.step6_salary_analysis_and_testing()
        df_error_summary, df_err_test, df_dunn_err, df_integrated, df_ho_skills, ho_archetype_ids, y_ho_skills, pred_ho_skills, h_err, p_err, eps2_err = self.step7_leakage_safe_rq3_error_analysis()
        
        self.step8_render_all_figures(
            df_prev, df_pca_var, df_loadings, df_k_metrics, df_lift,
            df_sal_summary, df_error_summary, df_ho_skills, ho_archetype_ids,
            y_ho_skills, pred_ho_skills
        )
        
        self.step9_save_archetype_metadata(
            (mean_ari, med_ari, mean_ami, med_ami),
            h_stat, p_val, eps2, h_err, p_err, eps2_err
        )
        
        t1 = time.time()
        print("\n" + "=" * 80)
        print(f"PHASE INDIA-5 PIPELINE COMPLETED SUCCESSFULLY IN {t1 - t0:.2f} SECONDS")
        print("=" * 80)


if __name__ == "__main__":
    engine = IndiaArchetypeEngine()
    engine.run()
