import sys
sys.path.insert(0, ".")
import pandas as pd
import numpy as np
from src.phase5.data import load_raw_modeling_data, get_train_test_split
from src.phase5.evaluation import run_fold_safe_cv, evaluate_baselines_cv
from src.phase5.models import get_default_models

df, tech_skills = load_raw_modeling_data()
split_data = get_train_test_split(df, tech_skills)
X_train_df = split_data['X_train']
y_train = split_data['y_train']
metadata_cols = split_data['metadata_cols']

# Baselines
df_base = evaluate_baselines_cv(X_train_df, y_train)
print("\n=== BASELINES ===")
print(df_base[["Model", "CV_MAE_Mean", "CV_RMSE_Mean", "CV_R2_Mean"]])

# Test Ridge and XGBoost on Set A: Raw target vs Log target
fast_models = {k: v for k, v in get_default_models().items() if k in ["Ridge", "XGBoost"]}

df_raw = run_fold_safe_cv(X_train_df, y_train, metadata_cols, tech_skills, feature_set="A", models=fast_models, use_log_target=False)
df_log = run_fold_safe_cv(X_train_df, y_train, metadata_cols, tech_skills, feature_set="A", models=fast_models, use_log_target=True)

print("\n=== TARGET COMPARISON (Feature Set A) ===")
for df_res, name in [(df_raw, "Raw Target (salary_midpoint)"), (df_log, "Log Target (log1p)")]:
    print(f"-- {name} --")
    for _, r in df_res.iterrows():
        print(f"  {r['Model']:12s} | MAE: ${r['CV_MAE_Mean']:,.0f} | RMSE: ${r['CV_RMSE_Mean']:,.0f} | R2: {r['CV_R2_Mean']:.4f}")
