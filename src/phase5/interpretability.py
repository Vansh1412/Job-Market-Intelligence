"""
Phase 5: Model Interpretability & Skill-Salary Triangulation (RQ1)
=================================================================
INT234 Predictive Analytics — Job Market Intelligence

Extracts Gini/gain feature importances, computes test permutation importances,
extracts standardized Ridge coefficients, and triangulates skill-salary drivers.
"""

import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance


def get_tree_feature_importance(model, feature_names):
    """Extracts tree-based feature importances (Gini/Gain)."""
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
        df = pd.DataFrame({
            "Feature": feature_names,
            "Importance": importances,
        }).sort_values("Importance", ascending=False).reset_index(drop=True)
        df["Rank"] = df.index + 1
        return df
    return None


def compute_test_permutation_importance(model, X_test, y_test, feature_names, n_repeats=5, random_state=42):
    """Computes permutation importance on held-out test partition."""
    perm = permutation_importance(
        model,
        X_test,
        y_test,
        n_repeats=n_repeats,
        random_state=random_state,
        scoring="neg_mean_absolute_error",
        n_jobs=-1
    )
    df = pd.DataFrame({
        "Feature": feature_names,
        "Permutation_Importance_Mean": perm.importances_mean,
        "Permutation_Importance_Std": perm.importances_std,
    }).sort_values("Permutation_Importance_Mean", ascending=False).reset_index(drop=True)
    df["Rank"] = df.index + 1
    return df


def get_ridge_coefficients(ridge_model, feature_names):
    """Extracts standardized regression coefficients from Ridge model."""
    if hasattr(ridge_model, "coef_"):
        coefs = ridge_model.coef_
        df = pd.DataFrame({
            "Feature": feature_names,
            "Coefficient": coefs,
            "Abs_Coefficient": np.abs(coefs),
        }).sort_values("Abs_Coefficient", ascending=False).reset_index(drop=True)
        df["Direction"] = np.where(df["Coefficient"] > 0, "Positive", "Negative")
        df["Rank"] = df.index + 1
        return df
    return None


def triangulate_rq1_skills(feature_importance_df, permutation_df, ridge_df, tech_skills):
    """
    Triangulates RQ1 skill associations across multiple modeling paradigms:
    1. Tree Gain / Split Importance (Non-linear supervised learning)
    2. Permutation Importance on Test Partition (Out-of-sample impact)
    3. Regularized Ridge Coefficients (Controlled linear effect)
    """
    tech_skills_clean = [s if s.startswith("skill_") else f"skill_{s}" for s in tech_skills]

    records = []
    for skill in tech_skills_clean:
        clean_name = skill.replace("skill_", "")

        # Tree importance
        tree_val = 0.0
        tree_rank = 999
        if feature_importance_df is not None:
            match = feature_importance_df[feature_importance_df["Feature"] == skill]
            if len(match) > 0:
                tree_val = float(match["Importance"].iloc[0])
                tree_rank = int(match["Rank"].iloc[0])

        # Permutation importance
        perm_val = 0.0
        perm_rank = 999
        if permutation_df is not None:
            match = permutation_df[permutation_df["Feature"] == skill]
            if len(match) > 0:
                perm_val = float(match["Permutation_Importance_Mean"].iloc[0])
                perm_rank = int(match["Rank"].iloc[0])

        # Ridge coefficient
        ridge_coef = 0.0
        ridge_dir = "Neutral"
        ridge_rank = 999
        if ridge_df is not None:
            match = ridge_df[ridge_df["Feature"] == skill]
            if len(match) > 0:
                ridge_coef = float(match["Coefficient"].iloc[0])
                ridge_dir = match["Direction"].iloc[0]
                ridge_rank = int(match["Rank"].iloc[0])

        records.append({
            "Skill": clean_name,
            "Feature_Tag": skill,
            "Tree_Importance": tree_val,
            "Tree_Rank": tree_rank,
            "Permutation_Importance": perm_val,
            "Permutation_Rank": perm_rank,
            "Ridge_Coefficient": ridge_coef,
            "Ridge_Direction": ridge_dir,
            "Ridge_Rank": ridge_rank,
        })

    df_tri = pd.DataFrame(records)
    # Composite rank: average of available ranks
    df_tri["Composite_Score"] = (
        df_tri["Tree_Importance"] / (df_tri["Tree_Importance"].max() + 1e-9)
        + df_tri["Permutation_Importance"] / (df_tri["Permutation_Importance"].max() + 1e-9)
    )
    df_tri = df_tri.sort_values("Composite_Score", ascending=False).reset_index(drop=True)
    df_tri["Composite_Rank"] = df_tri.index + 1

    return df_tri
