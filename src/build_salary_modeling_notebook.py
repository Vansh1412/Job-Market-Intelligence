"""
Build and execute notebooks/05_salary_modeling.ipynb
Programmatically generates the Phase 5 salary modeling notebook covering all 24 required sections:
1. Environment & Reproducibility
2. Load Data
3. Data Audit
4. Target Analysis
5. Train/Test Split
6. Leakage Audit
7. Feature Set A
8. Feature Set B
9. Feature Set C
10. Baseline Model
11. Model Training
12. Cross-Validation
13. Hyperparameter Tuning
14. Model Comparison
15. Final Test Evaluation
16. Bias-Variance Analysis
17. Learning Curves
18. Validation Curves
19. Residual Analysis
20. Feature Importance
21. Archetype Error Analysis
22. RQ1 — Skill/Salaries Triangulation
23. RQ3 — Archetype Error Differences
24. Conclusions & Next Steps
"""

import os
import sys
import nbformat as nbf
from nbconvert.preprocessors import ExecutePreprocessor

sys.stdout.reconfigure(encoding="utf-8")
if sys.platform == "win32":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

base_dir = r"e:\Job Market"

nb = nbf.v4.new_notebook()
nb.metadata = {
    "language_info": {
        "name": "python",
        "version": "3.13",
    },
    "kernelspec": {
        "name": "python3",
        "display_name": "Python 3",
    },
}

cells = []

# Title & Metadata
cells.append(nbf.v4.new_markdown_cell("""# INT234 Predictive Analytics — Job Market Intelligence
## Phase 5: Salary Prediction & Comparative Machine Learning
**Research Pipeline:** Supervised Salary Modeling, Fold-Safe Cluster Value Testing & Error Disaggregation  
**Supervised Salary Modeling Population:** Verified Compensation Cohort ($N = 34,036$ postings, $80\\%$ Train / $20\\%$ Test)  
**Primary Target Variable:** `salary_midpoint` (USD, Range: $\\$30,000$ to $\\$600,000$)  
**Core Hypotheses Addressed:**  
1. **RQ1:** Which skills and skill combinations are most associated with higher salaries?  
2. **RQ3:** Does salary-prediction error differ systematically across skill-based job archetypes?  
3. **Archetype Value Proposition:** Does incorporating skill-based archetype representations improve salary prediction over explicit skills?  
**Author:** Lead ML Research Engineer & Data Scientist  
**Date:** October 2026  
"""))

# Section 1: Environment & Reproducibility
cells.append(nbf.v4.new_markdown_cell("## 1. Environment & Reproducibility"))
cells.append(nbf.v4.new_code_cell("""import os
import sys
import time
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor

# Add repository root to path
sys.path.insert(0, "..")
from src.phase5.data import load_raw_modeling_data, audit_dataset, get_train_test_split
from src.phase5.evaluation import compute_metrics
from src.phase5.feature_sets import FeatureSetBuilder
from src.phase5.models import get_default_models

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8

DATA_DIR = "../data/processed"
MODELS_DIR = "../models/phase5"
TABLES_DIR = "../reports/tables/phase5"
FIGURES_DIR = "../reports/figures/phase5"

print("Environment initialized successfully. Random state locked at 42.")
print(f"Python: {sys.version.split()[0]} | Pandas: {pd.__version__} | NumPy: {np.__version__}")
"""))

# Section 2: Load Data
cells.append(nbf.v4.new_markdown_cell("## 2. Load Data"))
cells.append(nbf.v4.new_code_cell("""data_path = os.path.join(DATA_DIR, "modeling_dataset.parquet")
df_raw = pd.read_parquet(data_path)
tech_skills = sorted([c for c in df_raw.columns if c.startswith("skill_") and c not in ["skill_count", "skills"]])

print(f"Loaded modeling dataset from: {data_path}")
print(f"Dataset Dimensions: {df_raw.shape[0]:,} rows x {df_raw.shape[1]} columns")
print(f"Technical Skill Predictors Identified: {len(tech_skills)} binary indicators")
df_raw.head(3)
"""))

# Section 3: Data Audit
cells.append(nbf.v4.new_markdown_cell("## 3. Data Audit"))
cells.append(nbf.v4.new_code_cell("""audit_df = pd.read_csv(os.path.join(TABLES_DIR, "phase5_data_audit.csv"))
display(audit_df)

n_null_target = df_raw["salary_midpoint"].isnull().sum()
n_duplicates = df_raw.duplicated(subset=["title", "company_name", "city_clean", "salary_midpoint"]).sum()

print(f"Integrity Check: Missing Target Values = {n_null_target}")
print(f"Integrity Check: Duplicate Job-Salary Tuples = {n_duplicates}")
assert n_null_target == 0, "Null target values detected!"
"""))

# Section 4: Target Analysis
cells.append(nbf.v4.new_markdown_cell("## 4. Target Analysis (Raw vs. Log-Transformed Salary)"))
cells.append(nbf.v4.new_code_cell("""y_raw = df_raw["salary_midpoint"]
y_log = np.log1p(y_raw)

target_stats = pd.DataFrame({
    "Metric": ["Count", "Mean", "Std", "Min", "Q25", "Median", "Q75", "Max", "IQR", "Skewness", "Kurtosis"],
    "Raw Salary ($)": [
        f"{len(y_raw):,}", f"${y_raw.mean():,.2f}", f"${y_raw.std():,.2f}", f"${y_raw.min():,.2f}",
        f"${y_raw.quantile(0.25):,.2f}", f"${y_raw.median():,.2f}", f"${y_raw.quantile(0.75):,.2f}",
        f"${y_raw.max():,.2f}", f"${y_raw.quantile(0.75) - y_raw.quantile(0.25):,.2f}",
        f"{y_raw.skew():.4f}", f"{y_raw.kurtosis():.4f}"
    ],
    "Log1p Salary": [
        f"{len(y_log):,}", f"{y_log.mean():.4f}", f"{y_log.std():.4f}", f"{y_log.min():.4f}",
        f"{y_log.quantile(0.25):.4f}", f"{y_log.median():.4f}", f"{y_log.quantile(0.75):.4f}",
        f"{y_log.max():.4f}", f"{y_log.quantile(0.75) - y_log.quantile(0.25):.4f}",
        f"{y_log.skew():.4f}", f"{y_log.kurtosis():.4f}"
    ]
})
display(target_stats)

fig, axes = plt.subplots(1, 2, figsize=(14, 4))
sns.histplot(y_raw / 1000, bins=50, kde=True, ax=axes[0], color="#2b5c8f")
axes[0].set_title("Distribution of Raw Salary Midpoint ($k)")
axes[0].set_xlabel("Salary Midpoint ($k USD)")
axes[0].set_ylabel("Count")

sns.histplot(y_log, bins=50, kde=True, ax=axes[1], color="#2ca02c")
axes[1].set_title("Distribution of Log-Transformed Salary (log1p)")
axes[1].set_xlabel("log1p(Salary Midpoint)")
axes[1].set_ylabel("Count")
plt.tight_layout()
plt.show()
"""))

# Section 5: Train/Test Split
cells.append(nbf.v4.new_markdown_cell("## 5. Train/Test Split (80% Train, 20% Holdout Test)"))
cells.append(nbf.v4.new_code_cell("""split_data = get_train_test_split(df_raw, tech_skills)
X_train_df = split_data["X_train"]
X_test_df = split_data["X_test"]
y_train = split_data["y_train"]
y_test = split_data["y_test"]
metadata_cols = split_data["metadata_cols"]

print(f"Training Partition (80%): {X_train_df.shape[0]:,} samples")
print(f"Holdout Test Partition (20%): {X_test_df.shape[0]:,} samples (Strictly Isolated)")
print(f"Metadata Feature Predictors: {metadata_cols}")
"""))

# Section 6: Leakage Audit
cells.append(nbf.v4.new_markdown_cell("## 6. Leakage Audit"))
cells.append(nbf.v4.new_code_cell("""forbidden_cols = ["salary_min", "salary_max", "salary_midpoint", "log_salary", "cluster_id", "salary_currency", "salary_period"]
leaked_in_train = [c for c in forbidden_cols if c in X_train_df.columns]
leaked_in_test = [c for c in forbidden_cols if c in X_test_df.columns]

print(f"Checking for target-derived features in predictors: {leaked_in_train}")
print(f"Checking for precomputed cluster labels in predictors: {leaked_in_test}")
assert len(leaked_in_train) == 0 and len(leaked_in_test) == 0, "Data leakage detected!"
print("Leakage Audit PASSED: Zero forbidden columns present in predictive features.")
"""))

# Section 7: Feature Set A
cells.append(nbf.v4.new_markdown_cell("## 7. Feature Set A — Original Supervised Features (Skills + Metadata)"))
cells.append(nbf.v4.new_code_cell("""builder = FeatureSetBuilder(metadata_cols, tech_skills)
X_tr_A, X_te_A, fn_A, trans_A = builder.build_feature_set_A(X_train_df, X_test_df)

print(f"Feature Set A (Train Matrix): {X_tr_A.shape[0]:,} rows x {X_tr_A.shape[1]} columns")
print(f"Feature Set A (Test Matrix):  {X_te_A.shape[0]:,} rows x {X_te_A.shape[1]} columns")
print(f"Sample Feature Columns (first 10): {fn_A[:10]}")
"""))

# Section 8: Feature Set B
cells.append(nbf.v4.new_markdown_cell("## 8. Feature Set B — PCA Condensed Features (15 Components + Metadata)"))
cells.append(nbf.v4.new_code_cell("""X_tr_B, X_te_B, fn_B, trans_B = builder.build_feature_set_B(X_train_df, X_test_df)

print(f"Feature Set B (Train Matrix): {X_tr_B.shape[0]:,} rows x {X_tr_B.shape[1]} columns")
print(f"Feature Set B (Test Matrix):  {X_te_B.shape[0]:,} rows x {X_te_B.shape[1]} columns")
print(f"Explained Variance Ratio by 15 Skill PCA Components: {trans_B[1].pca.explained_variance_ratio_.sum() * 100:.2f}%")
"""))

# Section 9: Feature Set C
cells.append(nbf.v4.new_markdown_cell("## 9. Feature Set C — Original Features + Fold-Safe Archetypes (k=7)"))
cells.append(nbf.v4.new_code_cell("""X_tr_C, X_te_C, fn_C, trans_C = builder.build_feature_set_C(X_train_df, X_test_df)

print(f"Feature Set C (Train Matrix): {X_tr_C.shape[0]:,} rows x {X_tr_C.shape[1]} columns")
print(f"Feature Set C (Test Matrix):  {X_te_C.shape[0]:,} rows x {X_te_C.shape[1]} columns")
print(f"Archetype Feature Columns Added: {[c for c in fn_C if c.startswith('archetype_')]}")
"""))

# Section 10: Baseline Model
cells.append(nbf.v4.new_markdown_cell("## 10. Baseline Model (Naive Median & Mean Regressors)"))
cells.append(nbf.v4.new_code_cell("""dummy_median = DummyRegressor(strategy="median").fit(X_tr_A, y_train)
dummy_mean = DummyRegressor(strategy="mean").fit(X_tr_A, y_train)

pred_base_median = dummy_median.predict(X_te_A)
pred_base_mean = dummy_mean.predict(X_te_A)

m_median = compute_metrics(y_test, pred_base_median)
m_mean = compute_metrics(y_test, pred_base_mean)

df_baselines = pd.DataFrame([
    {"Baseline Strategy": "Dummy (Median)", "Test MAE": f"${m_median['MAE']:,.2f}", "Test RMSE": f"${m_median['RMSE']:,.2f}", "Test R2": f"{m_median['R2']:.4f}"},
    {"Baseline Strategy": "Dummy (Mean)", "Test MAE": f"${m_mean['MAE']:,.2f}", "Test RMSE": f"${m_mean['RMSE']:,.2f}", "Test R2": f"{m_mean['R2']:.4f}"}
])
display(df_baselines)
"""))

# Section 11: Model Training
cells.append(nbf.v4.new_markdown_cell("## 11. Model Training Overview"))
cells.append(nbf.v4.new_code_cell("""models_dict = get_default_models()
print("Candidate Algorithms Evaluated in Benchmark:")
for name, m in models_dict.items():
    print(f"  • {name:20s}: {m.__class__.__name__}")
"""))

# Section 12: Cross-Validation
cells.append(nbf.v4.new_markdown_cell("## 12. 5-Fold Cross-Validation Performance (Training Partition Only)"))
cells.append(nbf.v4.new_code_cell("""df_cv_results = pd.read_csv(os.path.join(TABLES_DIR, "phase5_cv_results.csv"))
display(df_cv_results.style.format({
    "CV_MAE_Mean": "${:,.0f}",
    "CV_MAE_Std": "${:,.0f}",
    "CV_RMSE_Mean": "${:,.0f}",
    "CV_RMSE_Std": "${:,.0f}",
    "CV_R2_Mean": "{:.4f}",
    "CV_R2_Std": "{:.4f}",
}))
"""))

# Section 13: Hyperparameter Tuning
cells.append(nbf.v4.new_markdown_cell("## 13. Controlled Hyperparameter Tuning (Top Candidate: XGBoost)"))
cells.append(nbf.v4.new_code_cell("""df_tuning = pd.read_csv(os.path.join(TABLES_DIR, "phase5_hyperparameter_results.csv"))
display(df_tuning.style.format({
    "CV_MAE_Mean": "${:,.0f}",
    "CV_MAE_Std": "${:,.0f}",
    "CV_RMSE_Mean": "${:,.0f}",
    "CV_R2_Mean": "{:.4f}",
}))
"""))

# Section 14: Model Comparison
cells.append(nbf.v4.new_markdown_cell("## 14. Model Comparison (Feature Set A vs. B vs. C)"))
cells.append(nbf.v4.new_code_cell("""df_comp = pd.read_csv(os.path.join(TABLES_DIR, "phase5_model_comparison.csv"))
display(df_comp.style.format({
    "CV_MAE_Mean": "${:,.0f}",
    "CV_MAE_Std": "${:,.0f}",
    "CV_RMSE_Mean": "${:,.0f}",
    "CV_R2_Mean": "{:.4f}",
}))

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(data=df_comp, x="Model", y="CV_MAE_Mean", hue="Feature_Set", ax=ax, palette="Blues_r")
ax.set_title("5-Fold Cross-Validation MAE Across Feature Sets ($)")
ax.set_ylabel("Mean CV MAE ($)")
ax.set_xticklabels(ax.get_xticklabels(), rotation=15)
plt.tight_layout()
plt.show()
"""))

# Section 15: Final Test Evaluation
cells.append(nbf.v4.new_markdown_cell("## 15. ONE Final Holdout Test Evaluation ($N = 6,808$)"))
cells.append(nbf.v4.new_code_cell("""df_test = pd.read_csv(os.path.join(TABLES_DIR, "phase5_test_results.csv"))
display(df_test.style.format({
    "Train_MAE": "${:,.0f}",
    "Test_MAE": "${:,.0f}",
    "Test_RMSE": "${:,.0f}",
    "Test_R2": "{:.4f}",
    "Test_MAPE": "{:.2f}%",
    "Generalization_Gap_MAE": "${:,.0f}",
    "Generalization_Gap_R2": "{:.4f}",
}))
"""))

# Section 16: Bias-Variance Analysis
cells.append(nbf.v4.new_markdown_cell("## 16. Bias-Variance & Generalization Analysis"))
cells.append(nbf.v4.new_code_cell("""df_bv = pd.read_csv(os.path.join(TABLES_DIR, "phase5_bias_variance.csv"))
display(df_bv.style.format({
    "Train_MAE": "${:,.0f}",
    "Test_MAE": "${:,.0f}",
    "Generalization_Gap_MAE": "${:,.0f}",
    "Train_R2": "{:.4f}",
    "Test_R2": "{:.4f}",
    "Generalization_Gap_R2": "{:.4f}",
}))
"""))

# Section 17: Learning Curves
cells.append(nbf.v4.new_markdown_cell("## 17. Learning Curves (Training vs. Validation Sample Size)"))
cells.append(nbf.v4.new_code_cell("""fig_path_lc = os.path.join(FIGURES_DIR, "07_learning_curve.png")
if os.path.exists(fig_path_lc):
    from IPython.display import Image
    display(Image(filename=fig_path_lc))
"""))

# Section 18: Validation Curves
cells.append(nbf.v4.new_markdown_cell("## 18. Validation Curves (Hyperparameter Sensitivity: Ridge vs. XGBoost)"))
cells.append(nbf.v4.new_code_cell("""fig_path_vc1 = os.path.join(FIGURES_DIR, "08_validation_curve_ridge.png")
fig_path_vc2 = os.path.join(FIGURES_DIR, "09_validation_curve_xgboost.png")
from IPython.display import Image
if os.path.exists(fig_path_vc1):
    display(Image(filename=fig_path_vc1))
if os.path.exists(fig_path_vc2):
    display(Image(filename=fig_path_vc2))
"""))

# Section 19: Residual Analysis
cells.append(nbf.v4.new_markdown_cell("## 19. Residual Diagnostics"))
cells.append(nbf.v4.new_code_cell("""fig_path_pva = os.path.join(FIGURES_DIR, "10_predicted_vs_actual.png")
fig_path_rvp = os.path.join(FIGURES_DIR, "11_residual_vs_predicted.png")
fig_path_rd = os.path.join(FIGURES_DIR, "12_residual_distribution.png")

from IPython.display import Image
if os.path.exists(fig_path_pva):
    display(Image(filename=fig_path_pva))
if os.path.exists(fig_path_rvp):
    display(Image(filename=fig_path_rvp))
if os.path.exists(fig_path_rd):
    display(Image(filename=fig_path_rd))
"""))

# Section 20: Feature Importance
cells.append(nbf.v4.new_markdown_cell("## 20. Feature Importance & Permutation Importance"))
cells.append(nbf.v4.new_code_cell("""df_perm = pd.read_csv(os.path.join(TABLES_DIR, "phase5_permutation_importance.csv"))
display(df_perm.head(15).style.format({
    "Permutation_MAE_Mean": "${:,.0f}",
    "MAE_Increase_Mean": "${:,.0f}",
    "MAE_Increase_Std": "${:,.0f}",
}))

fig_path_fi = os.path.join(FIGURES_DIR, "13_feature_importance.png")
fig_path_pi = os.path.join(FIGURES_DIR, "14_permutation_importance.png")
if os.path.exists(fig_path_fi):
    display(Image(filename=fig_path_fi))
if os.path.exists(fig_path_pi):
    display(Image(filename=fig_path_pi))
"""))

# Section 21: Archetype Error Analysis
cells.append(nbf.v4.new_markdown_cell("## 21. Archetype-Level Error Analysis"))
cells.append(nbf.v4.new_code_cell("""df_arch = pd.read_csv(os.path.join(TABLES_DIR, "phase5_archetype_errors.csv"))
display(df_arch.style.format({
    "N_Test": "{:,}",
    "MAE": "${:,.0f}",
    "RMSE": "${:,.0f}",
    "Median_AE": "${:,.0f}",
    "Mean_Error": "${:,.0f}",
    "Relative_MAE": "{:.2%}",
    "Median_Actual_Salary": "${:,.0f}",
    "R2": "{:.4f}",
}))

fig_path_am = os.path.join(FIGURES_DIR, "16_archetype_mae.png")
fig_path_ram = os.path.join(FIGURES_DIR, "17_archetype_relative_mae.png")
if os.path.exists(fig_path_am):
    display(Image(filename=fig_path_am))
if os.path.exists(fig_path_ram):
    display(Image(filename=fig_path_ram))
"""))

# Section 22: RQ1
cells.append(nbf.v4.new_markdown_cell("""## 22. RQ1: Triangulated Skill-Salary Association Analysis
> **RQ1:** Which skills and skill combinations are most associated with higher salaries?
"""))
cells.append(nbf.v4.new_code_cell("""df_rq1 = pd.read_csv(os.path.join(TABLES_DIR, "phase5_rq1_skill_associations.csv"))
display(df_rq1.head(15).style.format({
    "Tree_Gain_Importance": "{:.4f}",
    "Permutation_MAE_Increase": "${:,.0f}",
    "Ridge_Standardized_Coef": "${:,.0f}",
    "Composite_Predictive_Rank": "{:.2f}",
}))
"""))

# Section 23: RQ3
cells.append(nbf.v4.new_markdown_cell("""## 23. RQ3: Systematic Error Differences Across Archetypes
> **RQ3:** Does salary-prediction error differ across skill-based job archetypes?
"""))
cells.append(nbf.v4.new_code_cell("""# Display statistical significance summary
with open(os.path.join(MODELS_DIR, "feature_metadata.json")) as f:
    meta = json.load(f)

kw = meta["kruskal_wallis"]
print("=" * 60)
print("KRUSKAL-WALLIS H-TEST ON ABSOLUTE PREDICTION ERRORS:")
print(f"  H-Statistic: {kw['kruskal_wallis_stat']:.4f}")
print(f"  p-value:     {kw['kruskal_wallis_pval']:.4e}")
print(f"  Statistically Significant at alpha=0.05: {kw['is_significant_005']}")
print("=" * 60)

fig_path_ard = os.path.join(FIGURES_DIR, "18_archetype_residual_distribution.png")
if os.path.exists(fig_path_ard):
    display(Image(filename=fig_path_ard))
"""))

# Section 24: Conclusions
cells.append(nbf.v4.new_markdown_cell("""## 24. Conclusions & Next Steps
### Scientific Findings Summary:
1. **Salary Predictability:** Supervised machine learning reliably predicts tech job market compensation ($R^2 = 0.4233$, $\\text{MAE} = \\$36,381$, $\\text{RMSE} = \\$51,082$), representing a **$\\$14,425 (28.4\\%)$ error reduction** over baseline naive prediction.
2. **Archetype Value Proposition (Section 19):** **Outcome 2 ($C \\approx A$) is empirically demonstrated.** Adding 7-archetype cluster memberships yields equivalent predictive performance ($+\\$43$ difference on holdout test set), demonstrating that while archetypes are descriptive and intuitive taxonomies, high-resolution continuous skill vectors already capture the underlying variance.
3. **RQ1 Skill Associations:** `machine_learning`, `pytorch`, `deep_learning`, `aws`, `python`, `kubernetes`, `sql`, and `c++` exhibit the highest predictive associations with premium salaries.
4. **RQ3 Archetype Errors:** Error distributions differ significantly across archetypes ($H = 88.10$, $p = 7.53 \\times 10^{-17}$). `AI_ML` postings exhibit the lowest absolute MAE ($\\$27,002$) and lowest relative error ($14.4\\%$), while `CLOUD_ARCH` postings have the highest absolute MAE ($\\$46,098$) due to elevated salary variance and higher compensation scale.

---
**PHASE 5 COMPLETE — FROZEN FOR HUMAN REVIEW**
"""))

nb.cells = cells

nb_path = os.path.join(base_dir, "notebooks", "05_salary_modeling.ipynb")
with open(nb_path, "w", encoding="utf-8") as f:
    nbf.write(nb, f)
print(f"Successfully constructed notebook at: {nb_path}")

print("Executing notebook top-to-bottom...")
ep = ExecutePreprocessor(timeout=600, kernel_name="python3")
with open(nb_path, "r", encoding="utf-8") as f:
    nb_to_run = nbf.read(f, as_version=4)

ep.preprocess(nb_to_run, {"metadata": {"path": os.path.join(base_dir, "notebooks")}})

with open(nb_path, "w", encoding="utf-8") as f:
    nbf.write(nb_to_run, f)

print("Notebook 05_salary_modeling.ipynb executed successfully top-to-bottom with 0 errors!")
