"""
Phase 5: Publication Figures & Diagnostic Visualizations
========================================================
INT234 Predictive Analytics — Job Market Intelligence
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

FIGURES_DIR = "reports/figures/phase5"
os.makedirs(FIGURES_DIR, exist_ok=True)

# Aesthetics
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8
plt.rcParams["grid.color"] = "#eeeeee"
plt.rcParams["grid.linestyle"] = "--"


def plot_cv_comparisons(df_cv):
    """Plots CV MAE, RMSE, and R2 across models and feature sets (Figures 01-03)."""
    # Exclude dummy for clearer scaling
    df_plot = df_cv[~df_cv["Model"].str.contains("Dummy")].copy()

    # Fig 01: CV MAE
    plt.figure(figsize=(10, 5), dpi=300)
    sns.barplot(data=df_plot, x="Model", y="CV_MAE_Mean", hue="Feature_Set", palette="viridis")
    plt.title("Figure 01: 5-Fold Cross-Validation MAE by Model and Feature Set", fontsize=12, fontweight="bold", pad=12)
    plt.ylabel("Mean Validation MAE ($ USD)", fontsize=11)
    plt.xlabel("Regression Model", fontsize=11)
    plt.legend(title="Feature Set", frameon=True)
    plt.gca().yaxis.set_major_formatter("${x:,.0f}")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "01_cv_mae_comparison.png"))
    plt.close()

    # Fig 02: CV RMSE
    plt.figure(figsize=(10, 5), dpi=300)
    sns.barplot(data=df_plot, x="Model", y="CV_RMSE_Mean", hue="Feature_Set", palette="magma")
    plt.title("Figure 02: 5-Fold Cross-Validation RMSE by Model and Feature Set", fontsize=12, fontweight="bold", pad=12)
    plt.ylabel("Mean Validation RMSE ($ USD)", fontsize=11)
    plt.xlabel("Regression Model", fontsize=11)
    plt.legend(title="Feature Set", frameon=True)
    plt.gca().yaxis.set_major_formatter("${x:,.0f}")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "02_cv_rmse_comparison.png"))
    plt.close()

    # Fig 03: CV R2
    plt.figure(figsize=(10, 5), dpi=300)
    sns.barplot(data=df_plot, x="Model", y="CV_R2_Mean", hue="Feature_Set", palette="mako")
    plt.title("Figure 03: 5-Fold Cross-Validation R² by Model and Feature Set", fontsize=12, fontweight="bold", pad=12)
    plt.ylabel("Mean Validation R²", fontsize=11)
    plt.xlabel("Regression Model", fontsize=11)
    plt.legend(title="Feature Set", frameon=True)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "03_cv_r2_comparison.png"))
    plt.close()


def plot_test_comparisons(df_test):
    """Plots Test MAE, RMSE, and R2 (Figures 04-06)."""
    plt.figure(figsize=(9, 5), dpi=300)
    bars = plt.bar(df_test["Model"], df_test["Test_MAE"], color="#2b5c8f", alpha=0.85)
    plt.title("Figure 04: Holdout Test Set MAE Across Final Models", fontsize=12, fontweight="bold", pad=12)
    plt.ylabel("Test MAE ($ USD)", fontsize=11)
    plt.gca().yaxis.set_major_formatter("${x:,.0f}")
    for b in bars:
        h = b.get_height()
        plt.text(b.get_x() + b.get_width()/2, h + 500, f"${h:,.0f}", ha="center", fontsize=9, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "04_test_mae_comparison.png"))
    plt.close()

    plt.figure(figsize=(9, 5), dpi=300)
    bars = plt.bar(df_test["Model"], df_test["Test_RMSE"], color="#1b9e77", alpha=0.85)
    plt.title("Figure 05: Holdout Test Set RMSE Across Final Models", fontsize=12, fontweight="bold", pad=12)
    plt.ylabel("Test RMSE ($ USD)", fontsize=11)
    plt.gca().yaxis.set_major_formatter("${x:,.0f}")
    for b in bars:
        h = b.get_height()
        plt.text(b.get_x() + b.get_width()/2, h + 500, f"${h:,.0f}", ha="center", fontsize=9, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "05_test_rmse_comparison.png"))
    plt.close()

    plt.figure(figsize=(9, 5), dpi=300)
    bars = plt.bar(df_test["Model"], df_test["Test_R2"], color="#d95f02", alpha=0.85)
    plt.title("Figure 06: Holdout Test Set R² Across Final Models", fontsize=12, fontweight="bold", pad=12)
    plt.ylabel("Test R²", fontsize=11)
    for b in bars:
        h = b.get_height()
        plt.text(b.get_x() + b.get_width()/2, h + 0.01, f"{h:.4f}", ha="center", fontsize=9, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "06_test_r2_comparison.png"))
    plt.close()


def plot_learning_curve(train_sizes, train_scores, val_scores, model_name="Best Model"):
    """Plots empirical learning curve (Figure 07)."""
    plt.figure(figsize=(9, 5), dpi=300)
    tr_mean = np.mean(train_scores, axis=1)
    tr_std = np.std(train_scores, axis=1)
    val_mean = np.mean(val_scores, axis=1)
    val_std = np.std(val_scores, axis=1)

    plt.plot(train_sizes, tr_mean, "o-", color="#2b5c8f", label="Training Score (R²)", lw=2)
    plt.fill_between(train_sizes, tr_mean - tr_std, tr_mean + tr_std, alpha=0.15, color="#2b5c8f")
    plt.plot(train_sizes, val_mean, "s-", color="#d95f02", label="Cross-Validation Score (R²)", lw=2)
    plt.fill_between(train_sizes, val_mean - val_std, val_mean + val_std, alpha=0.15, color="#d95f02")

    plt.title(f"Figure 07: Empirical Learning Curve — {model_name}", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Training Set Size (Job Postings)", fontsize=11)
    plt.ylabel("Coefficient of Determination (R²)", fontsize=11)
    plt.legend(loc="lower right", frameon=True)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "07_learning_curve.png"))
    plt.close()


def plot_validation_curves(param_range_ridge, ridge_scores, param_range_xgb, xgb_scores):
    """Plots validation curves for Ridge alpha and XGBoost max_depth (Figures 08-09)."""
    # Fig 08: Ridge Alpha
    plt.figure(figsize=(9, 5), dpi=300)
    plt.semilogx(param_range_ridge, np.mean(ridge_scores, axis=1), "o-", color="#2b5c8f", lw=2)
    plt.title("Figure 08: Validation Curve — Ridge Regularization Strength (Alpha)", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Ridge Alpha Parameter (log scale)", fontsize=11)
    plt.ylabel("Validation Score (Negative MAE)", fontsize=11)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "08_validation_curve_ridge.png"))
    plt.close()

    # Fig 09: XGBoost max_depth
    plt.figure(figsize=(9, 5), dpi=300)
    plt.plot(param_range_xgb, np.mean(xgb_scores, axis=1), "s-", color="#1b9e77", lw=2)
    plt.title("Figure 09: Validation Curve — XGBoost Maximum Tree Depth", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Maximum Tree Depth", fontsize=11)
    plt.ylabel("Validation Score (Negative MAE)", fontsize=11)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "09_validation_curve_xgboost.png"))
    plt.close()


def plot_residual_diagnostics(y_true, y_pred, model_name="Best Model"):
    """Plots prediction quality diagnostics: Actual vs Predicted, Residuals vs Predicted, Residual Dist (Figures 10-12)."""
    residuals = y_pred - y_true

    # Fig 10: Actual vs Predicted
    plt.figure(figsize=(8, 8), dpi=300)
    plt.scatter(y_true, y_pred, alpha=0.25, color="#2b5c8f", s=15, edgecolors="none")
    lims = [30000, 600000]
    plt.plot(lims, lims, "--", color="#d95f02", lw=2, label="Perfect Agreement (45° Line)")
    plt.xlim(lims)
    plt.ylim(lims)
    plt.title(f"Figure 10: Predicted vs. Actual Salary — {model_name} (Test Set)", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Actual Salary Midpoint ($ USD)", fontsize=11)
    plt.ylabel("Predicted Salary Midpoint ($ USD)", fontsize=11)
    plt.gca().xaxis.set_major_formatter("${x:,.0f}")
    plt.gca().yaxis.set_major_formatter("${x:,.0f}")
    plt.legend(frameon=True)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "10_predicted_vs_actual.png"))
    plt.close()

    # Fig 11: Residual vs Predicted
    plt.figure(figsize=(10, 5), dpi=300)
    plt.scatter(y_pred, residuals, alpha=0.25, color="#1b9e77", s=15, edgecolors="none")
    plt.axhline(0, color="#d95f02", linestyle="--", lw=1.5)
    plt.title(f"Figure 11: Residuals vs. Fitted Values — {model_name} (Test Set)", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Predicted Salary Midpoint ($ USD)", fontsize=11)
    plt.ylabel("Residual (Predicted - Actual) ($ USD)", fontsize=11)
    plt.gca().xaxis.set_major_formatter("${x:,.0f}")
    plt.gca().yaxis.set_major_formatter("${x:,.0f}")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "11_residual_vs_predicted.png"))
    plt.close()

    # Fig 12: Residual Distribution
    plt.figure(figsize=(9, 5), dpi=300)
    sns.histplot(residuals, kde=True, color="#7570b3", bins=50)
    plt.axvline(0, color="#d95f02", linestyle="--", lw=1.5, label=f"Mean Error = ${residuals.mean():,.0f}")
    plt.axvline(np.median(residuals), color="#1b9e77", linestyle=":", lw=1.5, label=f"Median Error = ${np.median(residuals):,.0f}")
    plt.title(f"Figure 12: Distribution of Prediction Errors (Residuals) — {model_name}", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Prediction Error ($ USD)", fontsize=11)
    plt.ylabel("Frequency", fontsize=11)
    plt.gca().xaxis.set_major_formatter("${x:,.0f}")
    plt.legend(frameon=True)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "12_residual_distribution.png"))
    plt.close()


def plot_interpretability(tree_imp_df, perm_imp_df, ridge_df):
    """Plots interpretability rankings: Gini/Gain, Permutation, and Ridge Coefficients (Figures 13-15)."""
    # Fig 13: Tree Feature Importance
    if tree_imp_df is not None:
        plt.figure(figsize=(10, 6), dpi=300)
        top15 = tree_imp_df.head(15).sort_values("Importance")
        plt.barh(top15["Feature"].str.replace("skill_", "").str.replace("role_family_", "Role: ").str.replace("seniority_", "Seniority: "), top15["Importance"], color="#2b5c8f", alpha=0.85)
        plt.title("Figure 13: Top 15 Feature Importances (Tree Gain / Split Metric)", fontsize=12, fontweight="bold", pad=12)
        plt.xlabel("Relative Importance Weight", fontsize=11)
        plt.tight_layout()
        plt.savefig(os.path.join(FIGURES_DIR, "13_feature_importance.png"))
        plt.close()

    # Fig 14: Permutation Importance
    if perm_imp_df is not None:
        plt.figure(figsize=(10, 6), dpi=300)
        top15 = perm_imp_df.head(15).sort_values("Permutation_Importance_Mean")
        plt.barh(top15["Feature"].str.replace("skill_", "").str.replace("role_family_", "Role: ").str.replace("seniority_", "Seniority: "), top15["Permutation_Importance_Mean"], color="#1b9e77", alpha=0.85)
        plt.title("Figure 14: Top 15 Permutation Importances on Holdout Test Set", fontsize=12, fontweight="bold", pad=12)
        plt.xlabel("Mean Increase in MAE when Permuted ($ USD)", fontsize=11)
        plt.gca().xaxis.set_major_formatter("${x:,.0f}")
        plt.tight_layout()
        plt.savefig(os.path.join(FIGURES_DIR, "14_permutation_importance.png"))
        plt.close()

    # Fig 15: Ridge Coefficients
    if ridge_df is not None:
        plt.figure(figsize=(10, 6), dpi=300)
        top15 = ridge_df.head(15).sort_values("Coefficient")
        colors = ["#d95f02" if x < 0 else "#2b5c8f" for x in top15["Coefficient"]]
        plt.barh(top15["Feature"].str.replace("skill_", "").str.replace("role_family_", "Role: ").str.replace("seniority_", "Seniority: "), top15["Coefficient"], color=colors, alpha=0.85)
        plt.axvline(0, color="black", lw=0.8)
        plt.title("Figure 15: Top 15 Standardized Ridge Regression Coefficients", fontsize=12, fontweight="bold", pad=12)
        plt.xlabel("Standardized Coefficient Magnitude", fontsize=11)
        plt.tight_layout()
        plt.savefig(os.path.join(FIGURES_DIR, "15_ridge_coefficients.png"))
        plt.close()


def plot_archetype_error_diagnostics(df_arch_errors, y_true, y_pred, archetype_labels):
    """Plots archetype error breakdowns: MAE, Relative MAE, and Residual Distributions (Figures 16-18)."""
    # Fig 16: MAE by Archetype
    plt.figure(figsize=(11, 5), dpi=300)
    bars = plt.bar(df_arch_errors["Archetype_Name"], df_arch_errors["MAE"], color="#2b5c8f", alpha=0.85)
    plt.title("Figure 16: Mean Absolute Error (MAE) by Discovered Job Archetype (RQ3)", fontsize=12, fontweight="bold", pad=12)
    plt.ylabel("Test MAE ($ USD)", fontsize=11)
    plt.xticks(rotation=25, ha="right", fontsize=9)
    plt.gca().yaxis.set_major_formatter("${x:,.0f}")
    for b in bars:
        h = b.get_height()
        plt.text(b.get_x() + b.get_width()/2, h + 300, f"${h:,.0f}", ha="center", fontsize=8.5, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "16_archetype_mae.png"))
    plt.close()

    # Fig 17: Relative MAE by Archetype
    plt.figure(figsize=(11, 5), dpi=300)
    bars = plt.bar(df_arch_errors["Archetype_Name"], df_arch_errors["Relative_MAE_%"], color="#d95f02", alpha=0.85)
    plt.title("Figure 17: Relative Prediction Error (MAE / Median Salary) by Archetype", fontsize=12, fontweight="bold", pad=12)
    plt.ylabel("Relative Error (%)", fontsize=11)
    plt.xticks(rotation=25, ha="right", fontsize=9)
    for b in bars:
        h = b.get_height()
        plt.text(b.get_x() + b.get_width()/2, h + 0.3, f"{h:.1f}%", ha="center", fontsize=8.5, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "17_archetype_relative_mae.png"))
    plt.close()

    # Fig 18: Boxplot of Residuals by Archetype
    residuals = y_pred - y_true
    df_box = pd.DataFrame({
        "Archetype": [df_arch_errors.loc[df_arch_errors['Archetype_ID'] == a, 'Archetype_Name'].iloc[0] for a in archetype_labels],
        "Residual": residuals,
    })
    plt.figure(figsize=(12, 6), dpi=300)
    sns.boxplot(data=df_box, x="Archetype", y="Residual", palette="Set2", showfliers=False)
    plt.axhline(0, color="red", linestyle="--", lw=1)
    plt.title("Figure 18: Prediction Error (Residual) Distribution by Archetype", fontsize=12, fontweight="bold", pad=12)
    plt.ylabel("Residual (Predicted - Actual) ($ USD)", fontsize=11)
    plt.xticks(rotation=25, ha="right", fontsize=9)
    plt.gca().yaxis.set_major_formatter("${x:,.0f}")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "18_archetype_residual_distribution.png"))
    plt.close()
