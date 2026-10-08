"""
Phase 5: Cross-Validation & Evaluation Engine
============================================
INT234 Predictive Analytics — Job Market Intelligence

Executes 5-fold cross-validation with strict fold-safe feature construction
for Feature Sets A, B, and C.
"""

import time
import numpy as np
import pandas as pd
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    mean_absolute_error,
    root_mean_squared_error,
    r2_score,
    mean_absolute_percentage_error,
)
from sklearn.base import clone

from src.phase5.feature_sets import FeatureSetBuilder
from src.phase5.models import get_baseline_models, get_default_models

RANDOM_STATE = 42
N_SPLITS = 5


def compute_metrics(y_true, y_pred):
    """Computes standard regression evaluation metrics in original USD dollars."""
    mae = float(mean_absolute_error(y_true, y_pred))
    rmse = float(root_mean_squared_error(y_true, y_pred))
    r2 = float(r2_score(y_true, y_pred))
    mape = float(mean_absolute_percentage_error(y_true, y_pred)) * 100.0
    return {"MAE": mae, "RMSE": rmse, "R2": r2, "MAPE": mape}


def evaluate_baselines_cv(X_train_df, y_train, n_splits=N_SPLITS):
    """Evaluates DummyRegressor baselines using 5-fold CV."""
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_STATE)
    baseline_models = get_baseline_models()
    results = []

    for name, model in baseline_models.items():
        fold_metrics = []
        for train_idx, val_idx in kf.split(X_train_df):
            y_tr, y_val = y_train[train_idx], y_train[val_idx]
            m = clone(model)
            m.fit(X_train_df.iloc[train_idx], y_tr)
            y_pred = m.predict(X_train_df.iloc[val_idx])
            fold_metrics.append(compute_metrics(y_val, y_pred))

        df_m = pd.DataFrame(fold_metrics)
        results.append({
            "Feature_Set": "Baseline",
            "Model": name,
            "CV_MAE_Mean": df_m["MAE"].mean(),
            "CV_MAE_Std": df_m["MAE"].std(),
            "CV_RMSE_Mean": df_m["RMSE"].mean(),
            "CV_RMSE_Std": df_m["RMSE"].std(),
            "CV_R2_Mean": df_m["R2"].mean(),
            "CV_R2_Std": df_m["R2"].std(),
            "CV_MAPE_Mean": df_m["MAPE"].mean(),
        })

    return pd.DataFrame(results)


def run_fold_safe_cv(X_train_df, y_train, metadata_cols, tech_skills, feature_set="A", models=None, use_log_target=False):
    """
    Executes 5-fold CV strictly on training partition.
    For each fold, transformers (OHE, PCA, KMeans) are fitted ONLY on the fold training data.
    """
    if models is None:
        models = get_default_models()

    kf = KFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE)
    builder = FeatureSetBuilder(metadata_cols, tech_skills)

    cv_records = []
    print(f"\n[CV RUN] Starting 5-Fold CV for Feature Set {feature_set} (Log Target = {use_log_target})...", flush=True)

    # Pre-split folds
    folds = list(kf.split(X_train_df))

    for model_name, base_estimator in models.items():
        t0 = time.time()
        fold_metrics = []
        train_fold_metrics = []

        for fold_idx, (tr_idx, val_idx) in enumerate(folds, start=1):
            X_tr_fold = X_train_df.iloc[tr_idx]
            X_val_fold = X_train_df.iloc[val_idx]
            y_tr_fold = y_train[tr_idx]
            y_val_fold = y_train[val_idx]

            # Fold-safe feature construction
            if feature_set == "A":
                X_tr_mat, X_val_mat, _, _ = builder.build_feature_set_A(X_tr_fold, X_val_fold)
            elif feature_set == "B":
                X_tr_mat, X_val_mat, _, _ = builder.build_feature_set_B(X_tr_fold, X_val_fold)
            elif feature_set == "C":
                X_tr_mat, X_val_mat, _, _ = builder.build_feature_set_C(X_tr_fold, X_val_fold)
            else:
                raise ValueError(f"Unknown feature set: {feature_set}")

            # Optional model-specific scaling (for linear/Ridge/MLP)
            needs_scaling = model_name in ["Ridge", "MLP Regressor"]
            if needs_scaling:
                dense_scaler = StandardScaler()
                X_tr_mat = dense_scaler.fit_transform(X_tr_mat)
                X_val_mat = dense_scaler.transform(X_val_mat)

            # Fit regressor
            model = clone(base_estimator)
            y_fit_target = np.log1p(y_tr_fold) if use_log_target else y_tr_fold
            model.fit(X_tr_mat, y_fit_target)

            # Predict on validation fold
            y_pred_val_raw = model.predict(X_val_mat)
            y_pred_val = np.expm1(y_pred_val_raw) if use_log_target else y_pred_val_raw

            # Also predict on train fold for bias/variance check
            y_pred_tr_raw = model.predict(X_tr_mat)
            y_pred_tr = np.expm1(y_pred_tr_raw) if use_log_target else y_pred_tr_raw

            val_m = compute_metrics(y_val_fold, y_pred_val)
            tr_m = compute_metrics(y_tr_fold, y_pred_tr)

            fold_metrics.append(val_m)
            train_fold_metrics.append(tr_m)

        elapsed = time.time() - t0
        df_val_m = pd.DataFrame(fold_metrics)
        df_tr_m = pd.DataFrame(train_fold_metrics)

        res = {
            "Feature_Set": f"Set {feature_set}",
            "Model": model_name,
            "Target": "log1p(salary)" if use_log_target else "salary_midpoint",
            "CV_MAE_Mean": float(df_val_m["MAE"].mean()),
            "CV_MAE_Std": float(df_val_m["MAE"].std()),
            "CV_RMSE_Mean": float(df_val_m["RMSE"].mean()),
            "CV_RMSE_Std": float(df_val_m["RMSE"].std()),
            "CV_R2_Mean": float(df_val_m["R2"].mean()),
            "CV_R2_Std": float(df_val_m["R2"].std()),
            "CV_MAPE_Mean": float(df_val_m["MAPE"].mean()),
            "Train_MAE_Mean": float(df_tr_m["MAE"].mean()),
            "Train_RMSE_Mean": float(df_tr_m["RMSE"].mean()),
            "Train_R2_Mean": float(df_tr_m["R2"].mean()),
            "Fit_Time_Sec": np.round(elapsed, 1),
        }
        cv_records.append(res)
        print(f"  [{feature_set}] {model_name:18s} | Val MAE: ${res['CV_MAE_Mean']:,.0f} (+/- ${res['CV_MAE_Std']:,.0f}) | Val RMSE: ${res['CV_RMSE_Mean']:,.0f} | Val R²: {res['CV_R2_Mean']:.4f} | Time: {elapsed:.1f}s", flush=True)

    return pd.DataFrame(cv_records)
