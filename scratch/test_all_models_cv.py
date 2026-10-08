import sys
sys.path.insert(0, ".")
import time
import pandas as pd
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

# All 5 supervised models on Feature Set A
all_models = get_default_models()
t0 = time.time()
df_A = run_fold_safe_cv(X_train_df, y_train, metadata_cols, tech_skills, feature_set="A", models=all_models)
print(f"Total time for Feature Set A: {time.time() - t0:.1f}s")

# Combine and display
df_comp = pd.concat([df_base, df_A], ignore_index=True)
print("\n=== FEATURE SET A 5-FOLD CV RESULTS ===")
print(df_comp[["Model", "CV_MAE_Mean", "CV_RMSE_Mean", "CV_R2_Mean", "Fit_Time_Sec"]])
