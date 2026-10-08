"""
Phase 5: Archetype Error Analysis (RQ3) & Statistical Tests
===========================================================
INT234 Predictive Analytics — Job Market Intelligence

Computes per-archetype prediction error metrics (MAE, RMSE, Median AE, Mean Error / Bias,
Relative Error) and performs Kruskal-Wallis statistical significance testing.
"""

import numpy as np
import pandas as pd
from scipy.stats import kruskal, f_oneway
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score


def analyze_archetype_errors(y_true, y_pred, archetype_labels, archetype_names_map=None):
    """
    Computes per-archetype error metrics to rigorously answer RQ3:
    Does salary-prediction error differ systematically across skill-based job archetypes?
    """
    if archetype_names_map is None:
        archetype_names_map = {
            0: "FOUND_TECH (Foundational & Broad)",
            1: "DEVOPS_PLAT (DevOps & Cloud)",
            2: "WEB_FRONT (Frontend & Web)",
            3: "CLOUD_ARCH (Multi-Cloud)",
            4: "DATA_BI (Data & Analytics)",
            5: "AI_ML (AI / Machine Learning)",
            6: "SYS_ENG (Systems & Backend)",
        }

    abs_errors = np.abs(y_true - y_pred)
    raw_errors = y_pred - y_true  # Positive = overpredicted, Negative = underpredicted

    records = []
    error_groups = []

    unique_archetypes = sorted(np.unique(archetype_labels))

    for arch_id in unique_archetypes:
        mask = (archetype_labels == arch_id)
        n_arch = int(mask.sum())
        y_t_sub = y_true[mask]
        y_p_sub = y_pred[mask]
        abs_err_sub = abs_errors[mask]
        raw_err_sub = raw_errors[mask]

        mae = float(mean_absolute_error(y_t_sub, y_p_sub))
        rmse = float(root_mean_squared_error(y_t_sub, y_p_sub))
        med_ae = float(np.median(abs_err_sub))
        mean_err = float(np.mean(raw_err_sub))
        median_salary = float(np.median(y_t_sub))
        rel_mae = float(mae / median_salary * 100.0) if median_salary > 0 else 0.0

        r2 = float(r2_score(y_t_sub, y_p_sub)) if len(y_t_sub) > 1 else np.nan

        error_groups.append(abs_err_sub)

        arch_title = archetype_names_map.get(arch_id, f"Cluster_{arch_id}")

        records.append({
            "Archetype_ID": arch_id,
            "Archetype_Name": arch_title,
            "N": n_arch,
            "Median_Salary": median_salary,
            "MAE": mae,
            "RMSE": rmse,
            "Median_AE": med_ae,
            "Mean_Bias": mean_err,
            "Relative_MAE_%": rel_mae,
            "R2": r2,
        })

    df_errors = pd.DataFrame(records)

    # Statistical significance test: Kruskal-Wallis non-parametric ANOVA on absolute errors
    kw_stat, kw_pval = kruskal(*error_groups)

    stats_summary = {
        "kruskal_wallis_stat": float(kw_stat),
        "kruskal_wallis_pval": float(kw_pval),
        "is_significant_005": bool(kw_pval < 0.05),
        "highest_mae_archetype": df_errors.loc[df_errors["MAE"].idxmax(), "Archetype_Name"],
        "lowest_mae_archetype": df_errors.loc[df_errors["MAE"].idxmin(), "Archetype_Name"],
        "highest_rel_error_archetype": df_errors.loc[df_errors["Relative_MAE_%"].idxmax(), "Archetype_Name"],
        "lowest_rel_error_archetype": df_errors.loc[df_errors["Relative_MAE_%"].idxmin(), "Archetype_Name"],
    }

    return df_errors, stats_summary
