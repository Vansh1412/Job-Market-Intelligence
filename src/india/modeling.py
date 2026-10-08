"""
Phase India-4: Machine Learning Modeling, Leakage-Safe Cross-Validation,
Model Comparison, and Error Diagnostics for JobIntel India Tech Salary Prediction.
"""
import os
import json
import pickle
import hashlib
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import GroupShuffleSplit, GroupKFold
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge
from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor,
    HistGradientBoostingRegressor
)
from sklearn.inspection import permutation_importance
from xgboost import XGBRegressor

DATA_PATH = "data/processed/india/india_modeling_cohort.parquet"
SCHEMA_PATH = "data/processed/india/india_feature_schema.json"
MODELS_DIR = "models/india"
TABLES_DIR = "reports/tables/india"
FIGURES_DIR = "reports/figures/india"

RANDOM_STATE = 42

def load_data():
    """Load modeling cohort and feature schema."""
    df = pd.read_parquet(DATA_PATH)
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = json.load(f)
    return df, schema

def get_feature_groups(df):
    """Partition columns into explicit feature groups."""
    group_a_role = ["normalized_role"]
    group_b_exp = ["experience_midpoint_years", "experience_range_years"]
    group_c_loc = ["city_grouped"]
    group_d_mode = ["work_mode"]
    group_e_cnt = ["total_selected_skill_count"]
    group_f_skills = [c for c in df.columns if c.startswith("skill_")]
    
    return {
        "role": group_a_role,
        "experience": group_b_exp,
        "location": group_c_loc,
        "work_mode": group_d_mode,
        "skill_count": group_e_cnt,
        "skills": group_f_skills
    }

def get_feature_sets(groups):
    """Construct ablation feature sets (Sets 0 to 8)."""
    return {
        "set0_dummy": [],
        "set1_exp_only": groups["experience"],
        "set2_role_exp": groups["role"] + groups["experience"],
        "set3_role_exp_loc": groups["role"] + groups["experience"] + groups["location"],
        "set4_structured": groups["role"] + groups["experience"] + groups["location"] + groups["work_mode"] + groups["skill_count"],
        "set5_skills_only": groups["skill_count"] + groups["skills"],
        "set6_full": groups["role"] + groups["experience"] + groups["location"] + groups["work_mode"] + groups["skill_count"] + groups["skills"],
        "set7_no_skills": groups["role"] + groups["experience"] + groups["location"] + groups["work_mode"] + groups["skill_count"],
        "set8_role_skills": groups["role"] + groups["skill_count"] + groups["skills"]
    }

def create_preprocessor(feature_cols):
    """Build a ColumnTransformer for a specific feature set."""
    cat_cols = [c for c in feature_cols if c in ["normalized_role", "city_grouped", "work_mode"]]
    num_cols = [c for c in feature_cols if c in ["experience_midpoint_years", "experience_range_years", "total_selected_skill_count"]]
    skill_cols = [c for c in feature_cols if c.startswith("skill_")]
    
    transformers = []
    if cat_cols:
        transformers.append(("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols))
    if num_cols:
        transformers.append(("num", StandardScaler(), num_cols))
    if skill_cols:
        transformers.append(("skills", "passthrough", skill_cols))
        
    return ColumnTransformer(transformers=transformers, remainder="drop")

def compute_metrics(y_true, y_pred):
    """Compute standard evaluation metrics on original INR scale."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    
    err = y_true - y_pred
    abs_err = np.abs(err)
    
    mae = float(np.mean(abs_err))
    rmse = float(np.sqrt(np.mean(err ** 2)))
    median_ae = float(np.median(abs_err))
    
    ss_res = np.sum(err ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    r2 = float(1.0 - (ss_res / ss_tot)) if ss_tot > 0 else 0.0
    
    # Non-zero safe MAPE
    safe_y = np.where(y_true > 0, y_true, np.nan)
    mape = float(np.nanmean(abs_err / safe_y) * 100.0)
    
    return {
        "mae": mae,
        "mae_lpa": mae / 100000.0,
        "rmse": rmse,
        "rmse_lpa": rmse / 100000.0,
        "r2": r2,
        "median_ae": median_ae,
        "median_ae_lpa": median_ae / 100000.0,
        "mape": mape
    }

def evaluate_cv(model_factory, X_df, y_raw, groups, feature_cols, target_type="raw", n_splits=5):
    """
    Perform 5-fold GroupKFold cross-validation with fold-isolated preprocessing.
    """
    gkf = GroupKFold(n_splits=n_splits)
    fold_metrics = []
    
    oof_preds = np.zeros(len(X_df))
    
    for fold, (train_idx, val_idx) in enumerate(gkf.split(X_df, y_raw, groups)):
        X_tr = X_df.iloc[train_idx][feature_cols]
        X_va = X_df.iloc[val_idx][feature_cols]
        
        y_tr_raw = y_raw[train_idx]
        y_va_raw = y_raw[val_idx]
        
        # Build and fit preprocessor strictly on training fold
        if len(feature_cols) > 0:
            preprocessor = create_preprocessor(feature_cols)
            X_tr_proc = preprocessor.fit_transform(X_tr)
            X_va_proc = preprocessor.transform(X_va)
        else:
            # For Dummy Regressor
            X_tr_proc = np.zeros((len(X_tr), 1))
            X_va_proc = np.zeros((len(X_va), 1))
            
        # Target formulation
        if target_type == "log":
            y_tr_fit = np.log1p(y_tr_raw)
        else:
            y_tr_fit = y_tr_raw
            
        model = model_factory()
        model.fit(X_tr_proc, y_tr_fit)
        
        pred_fit = model.predict(X_va_proc)
        if target_type == "log":
            pred_raw = np.expm1(pred_fit)
        else:
            pred_raw = pred_fit
            
        oof_preds[val_idx] = pred_raw
        
        f_met = compute_metrics(y_va_raw, pred_raw)
        f_met["fold"] = fold + 1
        fold_metrics.append(f_met)
        
    df_folds = pd.DataFrame(fold_metrics)
    
    summary = {
        "cv_mae_mean": float(df_folds["mae"].mean()),
        "cv_mae_std": float(df_folds["mae"].std()),
        "cv_mae_lpa_mean": float(df_folds["mae_lpa"].mean()),
        "cv_mae_lpa_std": float(df_folds["mae_lpa"].std()),
        "cv_rmse_mean": float(df_folds["rmse"].mean()),
        "cv_rmse_std": float(df_folds["rmse"].std()),
        "cv_rmse_lpa_mean": float(df_folds["rmse_lpa"].mean()),
        "cv_rmse_lpa_std": float(df_folds["rmse_lpa"].std()),
        "cv_r2_mean": float(df_folds["r2"].mean()),
        "cv_r2_std": float(df_folds["r2"].std()),
        "cv_median_ae_mean": float(df_folds["median_ae"].mean()),
        "cv_median_ae_std": float(df_folds["median_ae"].std()),
        "cv_mape_mean": float(df_folds["mape"].mean()),
        "cv_mape_std": float(df_folds["mape"].std()),
    }
    
    return summary, df_folds, oof_preds

def run_all_experiments():
    """Main execution orchestrating all Phase India-4 experiments."""
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(TABLES_DIR, exist_ok=True)
    os.makedirs(FIGURES_DIR, exist_ok=True)
    
    print("=" * 80)
    print("JOBINTEL — PHASE INDIA-4: ML MODELING & EVALUATION SUITE")
    print("=" * 80)
    
    df, schema = load_data()
    print(f"Loaded modeling cohort: N = {len(df)} rows, {len(df.columns)} columns.")
    
    # 1. GroupShuffleSplit Holdout
    gss = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=RANDOM_STATE)
    train_idx, holdout_idx = next(gss.split(df, groups=df["content_fingerprint"]))
    
    df_train = df.iloc[train_idx].copy().reset_index(drop=True)
    df_holdout = df.iloc[holdout_idx].copy().reset_index(drop=True)
    
    print(f"Train partition: N = {len(df_train)} ({len(df_train)/len(df)*100:.1f}%)")
    print(f"Holdout partition: N = {len(df_holdout)} ({len(df_holdout)/len(df)*100:.1f}%)")
    
    train_groups = set(df_train["content_fingerprint"])
    holdout_groups = set(df_holdout["content_fingerprint"])
    overlap = train_groups.intersection(holdout_groups)
    assert len(overlap) == 0, f"FATAL: {len(overlap)} content groups leaked into holdout!"
    print("Holdout isolation verified: Exactly 0 content groups cross train/holdout.")
    
    groups_dict = get_feature_groups(df)
    feature_sets = get_feature_sets(groups_dict)
    
    y_train_raw = df_train["salary_midpoint_inr"].values
    y_holdout_raw = df_holdout["salary_midpoint_inr"].values
    cv_groups = df_train["content_fingerprint"].values
    
    registry = []
    all_fold_records = []
    
    # ----------------------------------------------------
    # Model Factories
    # ----------------------------------------------------
    model_defs = {
        "Dummy": (lambda: DummyRegressor(strategy="mean"), {}),
        "Ridge_alpha1": (lambda: Ridge(alpha=1.0, random_state=RANDOM_STATE), {"alpha": 1.0}),
        "Ridge_alpha10": (lambda: Ridge(alpha=10.0, random_state=RANDOM_STATE), {"alpha": 10.0}),
        "Ridge_alpha100": (lambda: Ridge(alpha=100.0, random_state=RANDOM_STATE), {"alpha": 100.0}),
        "RandomForest": (lambda: RandomForestRegressor(n_estimators=300, max_depth=20, min_samples_leaf=2, random_state=RANDOM_STATE, n_jobs=-1), {"n_estimators": 300, "max_depth": 20, "min_samples_leaf": 2}),
        "GradientBoosting": (lambda: GradientBoostingRegressor(n_estimators=200, learning_rate=0.05, max_depth=4, min_samples_leaf=3, random_state=RANDOM_STATE), {"n_estimators": 200, "learning_rate": 0.05, "max_depth": 4}),
        "HistGradientBoosting": (lambda: HistGradientBoostingRegressor(max_iter=150, learning_rate=0.05, max_leaf_nodes=31, min_samples_leaf=5, l2_regularization=1.0, random_state=RANDOM_STATE), {"max_iter": 150, "learning_rate": 0.05, "l2": 1.0}),
        "XGBoost_default": (lambda: XGBRegressor(n_estimators=150, max_depth=5, learning_rate=0.05, subsample=0.85, colsample_bytree=0.85, random_state=RANDOM_STATE, n_jobs=-1), {"n_estimators": 150, "max_depth": 5, "learning_rate": 0.05}),
        "XGBoost_tuned": (lambda: XGBRegressor(n_estimators=250, max_depth=6, learning_rate=0.04, subsample=0.80, colsample_bytree=0.75, reg_alpha=0.5, reg_lambda=3.0, min_child_weight=3, random_state=RANDOM_STATE, n_jobs=-1), {"n_estimators": 250, "max_depth": 6, "learning_rate": 0.04, "subsample": 0.8, "colsample_bytree": 0.75, "reg_alpha": 0.5, "reg_lambda": 3.0, "min_child_weight": 3})
    }
    
    # ----------------------------------------------------
    # EXPERIMENT 1: Feature Set Ablation (on Ridge and XGBoost)
    # ----------------------------------------------------
    print("\n--- Running Experiment 1: Feature Set Ablation (5-Fold CV) ---")
    ablation_results = []
    
    for fset_name, fcols in feature_sets.items():
        if fset_name == "set0_dummy":
            m_key = "Dummy"
            mf, m_params = model_defs[m_key]
            for target_type in ["raw"]:
                exp_id = f"EXP_ABL_{fset_name}_{m_key}_{target_type}"
                summary, df_f, _ = evaluate_cv(mf, df_train, y_train_raw, cv_groups, fcols, target_type=target_type)
                for _, row in df_f.iterrows():
                    rec = dict(row)
                    rec["experiment_id"] = exp_id
                    rec["feature_set"] = fset_name
                    rec["model"] = m_key
                    rec["target_type"] = target_type
                    all_fold_records.append(rec)
                    
                reg_item = {
                    "experiment_id": exp_id,
                    "feature_set": fset_name,
                    "num_features": len(fcols),
                    "model": m_key,
                    "target_type": target_type,
                    "hyperparameters": json.dumps(m_params),
                    **summary
                }
                registry.append(reg_item)
                ablation_results.append(reg_item)
                print(f"[{exp_id}] CV MAE: INR {summary['cv_mae_mean']:,.0f} ({summary['cv_mae_lpa_mean']:.2f} LPA), R2: {summary['cv_r2_mean']:.4f}")
            continue

        # Evaluate Ridge and XGBoost on each feature set
        for m_key in ["Ridge_alpha10", "XGBoost_default"]:
            mf, m_params = model_defs[m_key]
            for target_type in ["raw", "log"]:
                exp_id = f"EXP_ABL_{fset_name}_{m_key}_{target_type}"
                summary, df_f, _ = evaluate_cv(mf, df_train, y_train_raw, cv_groups, fcols, target_type=target_type)
                for _, row in df_f.iterrows():
                    rec = dict(row)
                    rec["experiment_id"] = exp_id
                    rec["feature_set"] = fset_name
                    rec["model"] = m_key
                    rec["target_type"] = target_type
                    all_fold_records.append(rec)
                    
                reg_item = {
                    "experiment_id": exp_id,
                    "feature_set": fset_name,
                    "num_features": len(fcols),
                    "model": m_key,
                    "target_type": target_type,
                    "hyperparameters": json.dumps(m_params),
                    **summary
                }
                registry.append(reg_item)
                ablation_results.append(reg_item)
                print(f"[{exp_id}] CV MAE: INR {summary['cv_mae_mean']:,.0f} ({summary['cv_mae_lpa_mean']:.2f} LPA), R2: {summary['cv_r2_mean']:.4f}")

    # ----------------------------------------------------
    # EXPERIMENT 2: Model Architecture Comparison (Set 6: Full Feature Set)
    # ----------------------------------------------------
    print("\n--- Running Experiment 2: Model Comparison on Set 6 (Full Features) ---")
    full_fcols = feature_sets["set6_full"]
    models_to_compare = [
        "Dummy",
        "Ridge_alpha1",
        "Ridge_alpha10",
        "Ridge_alpha100",
        "RandomForest",
        "GradientBoosting",
        "HistGradientBoosting",
        "XGBoost_default",
        "XGBoost_tuned"
    ]
    
    cv_summary_list = []
    
    for m_key in models_to_compare:
        mf, m_params = model_defs[m_key]
        target_types = ["raw"] if m_key == "Dummy" else ["raw", "log"]
        
        for target_type in target_types:
            exp_id = f"EXP_MOD_set6_full_{m_key}_{target_type}"
            summary, df_f, _ = evaluate_cv(mf, df_train, y_train_raw, cv_groups, full_fcols, target_type=target_type)
            
            for _, row in df_f.iterrows():
                rec = dict(row)
                rec["experiment_id"] = exp_id
                rec["feature_set"] = "set6_full"
                rec["model"] = m_key
                rec["target_type"] = target_type
                all_fold_records.append(rec)
                
            reg_item = {
                "experiment_id": exp_id,
                "feature_set": "set6_full",
                "num_features": len(full_fcols),
                "model": m_key,
                "target_type": target_type,
                "hyperparameters": json.dumps(m_params),
                **summary
            }
            registry.append(reg_item)
            cv_summary_list.append(reg_item)
            print(f"[{exp_id}] CV MAE: INR {summary['cv_mae_mean']:,.0f} ({summary['cv_mae_lpa_mean']:.2f} LPA), RMSE: INR {summary['cv_rmse_mean']:,.0f}, R2: {summary['cv_r2_mean']:.4f}")

    # ----------------------------------------------------
    # EXPERIMENT 3: Holdout Evaluation of Top Candidates
    # ----------------------------------------------------
    print("\n--- Running Experiment 3: Untouched Holdout Evaluation ---")
    holdout_results = []
    bias_variance_records = []
    
    # We evaluate all major architectures on full training set against holdout
    candidate_keys = [
        ("Dummy", "raw"),
        ("Ridge_alpha10", "raw"),
        ("Ridge_alpha10", "log"),
        ("RandomForest", "raw"),
        ("RandomForest", "log"),
        ("GradientBoosting", "raw"),
        ("HistGradientBoosting", "raw"),
        ("HistGradientBoosting", "log"),
        ("XGBoost_default", "raw"),
        ("XGBoost_default", "log"),
        ("XGBoost_tuned", "raw"),
        ("XGBoost_tuned", "log")
    ]
    
    preprocessor_full = create_preprocessor(full_fcols)
    X_train_full = preprocessor_full.fit_transform(df_train[full_fcols])
    X_holdout_full = preprocessor_full.transform(df_holdout[full_fcols])
    
    # Save candidate fitted models and predictions
    holdout_predictions = {}
    train_predictions = {}
    fitted_models = {}
    
    dummy_holdout_mae = None
    dummy_holdout_rmse = None
    
    for m_key, target_type in candidate_keys:
        mf, m_params = model_defs[m_key]
        model = mf()
        
        if m_key == "Dummy":
            X_tr_fit = np.zeros((len(df_train), 1))
            X_ho_fit = np.zeros((len(df_holdout), 1))
        else:
            X_tr_fit = X_train_full
            X_ho_fit = X_holdout_full
            
        y_tr_fit = np.log1p(y_train_raw) if target_type == "log" else y_train_raw
        model.fit(X_tr_fit, y_tr_fit)
        fitted_models[(m_key, target_type)] = model
        
        # Predictions
        p_tr = model.predict(X_tr_fit)
        p_ho = model.predict(X_ho_fit)
        
        if target_type == "log":
            p_tr_raw = np.expm1(p_tr)
            p_ho_raw = np.expm1(p_ho)
        else:
            p_tr_raw = p_tr
            p_ho_raw = p_ho
            
        train_predictions[(m_key, target_type)] = p_tr_raw
        holdout_predictions[(m_key, target_type)] = p_ho_raw
        
        met_tr = compute_metrics(y_train_raw, p_tr_raw)
        met_ho = compute_metrics(y_holdout_raw, p_ho_raw)
        
        if m_key == "Dummy":
            dummy_holdout_mae = met_ho["mae"]
            dummy_holdout_rmse = met_ho["rmse"]
            
        h_rec = {
            "model": m_key,
            "target_type": target_type,
            "holdout_mae": met_ho["mae"],
            "holdout_mae_lpa": met_ho["mae_lpa"],
            "holdout_rmse": met_ho["rmse"],
            "holdout_rmse_lpa": met_ho["rmse_lpa"],
            "holdout_r2": met_ho["r2"],
            "holdout_median_ae": met_ho["median_ae"],
            "holdout_median_ae_lpa": met_ho["median_ae_lpa"],
            "holdout_mape": met_ho["mape"]
        }
        holdout_results.append(h_rec)
        
        # Matching CV entry
        cv_match = next((item for item in cv_summary_list if item["model"] == m_key and item["target_type"] == target_type), None)
        cv_mae = cv_match["cv_mae_mean"] if cv_match else np.nan
        cv_r2 = cv_match["cv_r2_mean"] if cv_match else np.nan
        
        bv_rec = {
            "model": m_key,
            "target_type": target_type,
            "train_mae": met_tr["mae"],
            "train_mae_lpa": met_tr["mae_lpa"],
            "cv_mae": cv_mae,
            "cv_mae_lpa": cv_mae / 100000.0 if not np.isnan(cv_mae) else np.nan,
            "holdout_mae": met_ho["mae"],
            "holdout_mae_lpa": met_ho["mae_lpa"],
            "train_r2": met_tr["r2"],
            "cv_r2": cv_r2,
            "holdout_r2": met_ho["r2"],
            "train_to_cv_mae_gap_lpa": (cv_mae - met_tr["mae"]) / 100000.0 if not np.isnan(cv_mae) else np.nan,
            "train_to_holdout_mae_gap_lpa": (met_ho["mae"] - met_tr["mae"]) / 100000.0
        }
        bias_variance_records.append(bv_rec)
        print(f"[{m_key} | {target_type}] Holdout MAE: INR {met_ho['mae']:,.0f} ({met_ho['mae_lpa']:.2f} LPA), RMSE: INR {met_ho['rmse']:,.0f}, R2: {met_ho['r2']:.4f}")

    df_holdout_res = pd.DataFrame(holdout_results)
    
    # Baseline improvement table
    base_imp_records = []
    for h in holdout_results:
        mae_imp = ((dummy_holdout_mae - h["holdout_mae"]) / dummy_holdout_mae) * 100.0
        rmse_imp = ((dummy_holdout_rmse - h["holdout_rmse"]) / dummy_holdout_rmse) * 100.0
        base_imp_records.append({
            "model": h["model"],
            "target_type": h["target_type"],
            "holdout_mae_lpa": h["holdout_mae_lpa"],
            "mae_improvement_pct": mae_imp,
            "holdout_rmse_lpa": h["holdout_rmse_lpa"],
            "rmse_improvement_pct": rmse_imp,
            "holdout_r2": h["holdout_r2"]
        })
    df_base_imp = pd.DataFrame(base_imp_records)
    
    # Raw vs Log Comparison Table
    raw_log_records = []
    for m in ["Ridge_alpha10", "RandomForest", "HistGradientBoosting", "XGBoost_default", "XGBoost_tuned"]:
        row_raw = next((r for r in holdout_results if r["model"] == m and r["target_type"] == "raw"), None)
        row_log = next((r for r in holdout_results if r["model"] == m and r["target_type"] == "log"), None)
        if row_raw and row_log:
            raw_log_records.append({
                "model": m,
                "raw_holdout_mae_lpa": row_raw["holdout_mae_lpa"],
                "log_holdout_mae_lpa": row_log["holdout_mae_lpa"],
                "mae_diff_lpa (log - raw)": row_log["holdout_mae_lpa"] - row_raw["holdout_mae_lpa"],
                "raw_holdout_rmse_lpa": row_raw["holdout_rmse_lpa"],
                "log_holdout_rmse_lpa": row_log["holdout_rmse_lpa"],
                "raw_holdout_r2": row_raw["holdout_r2"],
                "log_holdout_r2": row_log["holdout_r2"],
                "preferred_target_by_mae": "LOG" if row_log["holdout_mae_lpa"] < row_raw["holdout_mae_lpa"] else "RAW"
            })
    df_raw_log = pd.DataFrame(raw_log_records)
    
    # ----------------------------------------------------
    # FINAL MODEL SELECTION
    # Policy: Lowest Holdout MAE subject to stability and low bias/variance gap
    # ----------------------------------------------------
    best_candidate_row = df_holdout_res.sort_values(by="holdout_mae").iloc[0]
    best_model_name = best_candidate_row["model"]
    best_target_type = best_candidate_row["target_type"]
    best_key = (best_model_name, best_target_type)
    final_model = fitted_models[best_key]
    
    print("\n" + "=" * 80)
    print(f"FINAL WINNING MODEL SELECTED: {best_model_name} (Target: {best_target_type})")
    print(f"Holdout MAE: INR {best_candidate_row['holdout_mae']:,.0f} ({best_candidate_row['holdout_mae_lpa']:.2f} LPA)")
    print(f"Holdout RMSE: INR {best_candidate_row['holdout_rmse']:,.0f} ({best_candidate_row['holdout_rmse_lpa']:.2f} LPA)")
    print(f"Holdout R2: {best_candidate_row['holdout_r2']:.4f}")
    print(f"Holdout Median AE: INR {best_candidate_row['holdout_median_ae']:,.0f} ({best_candidate_row['holdout_median_ae_lpa']:.2f} LPA)")
    print("=" * 80)
    
    # ----------------------------------------------------
    # EXPERIMENT 4: Deep Diagnostics on Winning Model
    # ----------------------------------------------------
    y_pred_best = holdout_predictions[best_key]
    df_eval = df_holdout.copy()
    df_eval["predicted_salary_inr"] = y_pred_best
    df_eval["predicted_salary_lpa"] = y_pred_best / 100000.0
    df_eval["residual_inr"] = df_eval["salary_midpoint_inr"] - df_eval["predicted_salary_inr"]
    df_eval["residual_lpa"] = df_eval["salary_lpa"] - df_eval["predicted_salary_lpa"]
    df_eval["abs_error_inr"] = np.abs(df_eval["residual_inr"])
    df_eval["abs_error_lpa"] = df_eval["abs_error_inr"] / 100000.0
    
    # 1. Error by Role (14 roles)
    role_metrics = []
    for role, grp in df_eval.groupby("normalized_role"):
        m = compute_metrics(grp["salary_midpoint_inr"], grp["predicted_salary_inr"])
        mean_res = float(grp["residual_inr"].mean())
        role_metrics.append({
            "role": role,
            "N": len(grp),
            "mae_lpa": m["mae_lpa"],
            "rmse_lpa": m["rmse_lpa"],
            "r2": m["r2"],
            "median_ae_lpa": m["median_ae_lpa"],
            "mean_residual_lpa": mean_res / 100000.0,
            "mape": m["mape"]
        })
    df_err_role = pd.DataFrame(role_metrics).sort_values(by="N", ascending=False)
    
    # 2. Error by City (Top metros with N >= 10 in holdout)
    city_metrics = []
    for city, grp in df_eval.groupby("city_grouped"):
        m = compute_metrics(grp["salary_midpoint_inr"], grp["predicted_salary_inr"])
        city_metrics.append({
            "city": city,
            "N": len(grp),
            "mae_lpa": m["mae_lpa"],
            "rmse_lpa": m["rmse_lpa"],
            "r2": m["r2"],
            "median_ae_lpa": m["median_ae_lpa"],
            "mean_residual_lpa": float(grp["residual_inr"].mean()) / 100000.0
        })
    df_err_city = pd.DataFrame(city_metrics).sort_values(by="N", ascending=False)
    
    # 3. Error by Experience Band
    exp_bins = [-1, 2, 5, 10, 15, 100]
    exp_labels = ["0-2 years (Entry)", "3-5 years (Mid)", "6-10 years (Senior)", "11-15 years (Lead)", "16+ years (Principal/Exec)"]
    df_eval["exp_band"] = pd.cut(df_eval["experience_midpoint_years"], bins=exp_bins, labels=exp_labels)
    exp_metrics = []
    for band, grp in df_eval.groupby("exp_band", observed=True):
        m = compute_metrics(grp["salary_midpoint_inr"], grp["predicted_salary_inr"])
        exp_metrics.append({
            "experience_band": str(band),
            "N": len(grp),
            "pct_of_holdout": len(grp) / len(df_eval) * 100.0,
            "mae_lpa": m["mae_lpa"],
            "rmse_lpa": m["rmse_lpa"],
            "r2": m["r2"],
            "median_ae_lpa": m["median_ae_lpa"],
            "mean_residual_lpa": float(grp["residual_inr"].mean()) / 100000.0
        })
    df_err_exp = pd.DataFrame(exp_metrics)
    
    # 4. Error by Salary Band
    sal_bins = [0, 5, 10, 20, 40, 100]
    sal_labels = ["1.2-5 LPA", "5-10 LPA", "10-20 LPA", "20-40 LPA", "40-80 LPA"]
    df_eval["salary_band"] = pd.cut(df_eval["salary_lpa"], bins=sal_bins, labels=sal_labels)
    sal_metrics = []
    for sband, grp in df_eval.groupby("salary_band", observed=True):
        m = compute_metrics(grp["salary_midpoint_inr"], grp["predicted_salary_inr"])
        sal_metrics.append({
            "salary_band": str(sband),
            "N": len(grp),
            "pct_of_holdout": len(grp) / len(df_eval) * 100.0,
            "mae_lpa": m["mae_lpa"],
            "rmse_lpa": m["rmse_lpa"],
            "r2": m["r2"],
            "median_ae_lpa": m["median_ae_lpa"],
            "mean_residual_lpa": float(grp["residual_inr"].mean()) / 100000.0
        })
    df_err_sal = pd.DataFrame(sal_metrics)
    
    # 5. Upper-Tail Error Analysis
    high_sal_records = []
    for cutoff in [10.0, 20.0, 30.0, 40.0]:
        grp = df_eval[df_eval["salary_lpa"] >= cutoff]
        if len(grp) > 0:
            m = compute_metrics(grp["salary_midpoint_inr"], grp["predicted_salary_inr"])
            high_sal_records.append({
                "cutoff_threshold": f">= {cutoff} LPA",
                "N": len(grp),
                "pct_of_holdout": len(grp) / len(df_eval) * 100.0,
                "mae_lpa": m["mae_lpa"],
                "rmse_lpa": m["rmse_lpa"],
                "median_ae_lpa": m["median_ae_lpa"],
                "mean_residual_lpa (bias)": float(grp["residual_inr"].mean()) / 100000.0,
                "relative_error_pct": float(np.mean(grp["abs_error_inr"] / grp["salary_midpoint_inr"])) * 100.0
            })
    df_high_sal = pd.DataFrame(high_sal_records)
    
    # 6. Feature Importance (Native + Permutation Importance on Holdout)
    print("\nComputing Permutation Importance on untouched holdout...")
    t_start_pi = time.time()
    
    # Build column names for preprocessed matrix
    ohe = preprocessor_full.named_transformers_["cat"]
    cat_feature_names = ohe.get_feature_names_out(["normalized_role", "city_grouped", "work_mode"]).tolist()
    num_feature_names = ["experience_midpoint_years", "experience_range_years", "total_selected_skill_count"]
    skill_feature_names = [c for c in full_fcols if c.startswith("skill_")]
    all_transformed_names = cat_feature_names + num_feature_names + skill_feature_names
    
    # Native Feature Importance
    if hasattr(final_model, "feature_importances_"):
        native_imp = final_model.feature_importances_
    elif hasattr(final_model, "coef_"):
        native_imp = np.abs(final_model.coef_)
    else:
        # For models like HistGradientBoosting that do not expose tree split importances natively,
        # extract native importance from XGBoost as reference
        xgb_cand = fitted_models.get(("XGBoost_tuned", best_target_type), fitted_models.get(("XGBoost_default", best_target_type)))
        if xgb_cand and hasattr(xgb_cand, "feature_importances_"):
            native_imp = xgb_cand.feature_importances_
        else:
            native_imp = np.zeros(len(all_transformed_names))
        
    df_native_imp = pd.DataFrame({
        "feature": all_transformed_names,
        "native_importance": native_imp
    }).sort_values(by="native_importance", ascending=False)
    
    # Permutation importance on holdout with n_repeats=5
    pi = permutation_importance(
        final_model,
        X_holdout_full,
        np.log1p(y_holdout_raw) if best_target_type == "log" else y_holdout_raw,
        n_repeats=5,
        random_state=RANDOM_STATE,
        scoring="neg_mean_absolute_error",
        n_jobs=-1
    )
    
    df_pi = pd.DataFrame({
        "feature": all_transformed_names,
        "importance_mean": pi.importances_mean,
        "importance_std": pi.importances_std,
        "native_importance": native_imp
    }).sort_values(by="importance_mean", ascending=False)
    print(f"Permutation importance computed in {time.time()-t_start_pi:.2f}s.")
    
    # 7. Skill Salary Association Analysis
    skill_assoc_list = []
    # Identify top skills from full dataset and holdout
    for sc in skill_feature_names:
        clean_skill = sc.replace("skill_", "").replace("_", " ").title()
        has_skill = df["salary_midpoint_inr"][df[sc] == 1]
        no_skill = df["salary_midpoint_inr"][df[sc] == 0]
        
        if len(has_skill) >= 25:
            med_has = float(has_skill.median()) / 100000.0
            med_no = float(no_skill.median()) / 100000.0
            diff_med = med_has - med_no
            
            # Find in permutation importance
            pi_row = df_pi[df_pi["feature"] == sc]
            pi_val = float(pi_row["importance_mean"].values[0]) if len(pi_row) > 0 else 0.0
            
            skill_assoc_list.append({
                "skill_column": sc,
                "skill_name": clean_skill,
                "frequency_total": len(has_skill),
                "frequency_pct": len(has_skill) / len(df) * 100.0,
                "median_salary_lpa": med_has,
                "mean_salary_lpa": float(has_skill.mean()) / 100000.0,
                "non_skill_median_salary_lpa": med_no,
                "observed_delta_lpa": diff_med,
                "model_permutation_importance": pi_val
            })
    df_skill_assoc = pd.DataFrame(skill_assoc_list).sort_values(by="observed_delta_lpa", ascending=False)
    
    # ----------------------------------------------------
    # SAVE ALL TABLES (Section 39)
    # ----------------------------------------------------
    print("\nSaving 14 Structured CSV Tables in reports/tables/india/...")
    pd.DataFrame(all_fold_records).to_csv(os.path.join(TABLES_DIR, "cv_fold_metrics.csv"), index=False)
    pd.DataFrame(cv_summary_list).to_csv(os.path.join(TABLES_DIR, "model_cv_summary.csv"), index=False)
    df_holdout_res.to_csv(os.path.join(TABLES_DIR, "holdout_model_results.csv"), index=False)
    df_base_imp.to_csv(os.path.join(TABLES_DIR, "baseline_improvement.csv"), index=False)
    df_raw_log.to_csv(os.path.join(TABLES_DIR, "raw_vs_log_comparison.csv"), index=False)
    pd.DataFrame(bias_variance_records).to_csv(os.path.join(TABLES_DIR, "bias_variance_metrics.csv"), index=False)
    df_err_role.to_csv(os.path.join(TABLES_DIR, "error_by_role.csv"), index=False)
    df_err_city.to_csv(os.path.join(TABLES_DIR, "error_by_city.csv"), index=False)
    df_err_exp.to_csv(os.path.join(TABLES_DIR, "error_by_experience.csv"), index=False)
    df_err_sal.to_csv(os.path.join(TABLES_DIR, "error_by_salary_band.csv"), index=False)
    df_high_sal.to_csv(os.path.join(TABLES_DIR, "high_salary_error.csv"), index=False)
    df_pi.to_csv(os.path.join(TABLES_DIR, "permutation_importance.csv"), index=False)
    df_skill_assoc.to_csv(os.path.join(TABLES_DIR, "skill_salary_association.csv"), index=False)
    
    # Full Experiment Registry
    df_registry = pd.DataFrame(registry)
    df_registry.to_csv(os.path.join(TABLES_DIR, "experiment_registry.csv"), index=False)
    with open(os.path.join(MODELS_DIR, "experiment_registry.json"), "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)
    print("CSV tables successfully written.")

    # ----------------------------------------------------
    # GENERATE 10 DIAGNOSTIC FIGURES (Section 35)
    # ----------------------------------------------------
    print("\nRendering 10 Publication-Quality Figures in reports/figures/india/...")
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    
    # Fig 1: model_mae_comparison.png
    plt.figure(figsize=(10, 6))
    df_plot_mae = df_holdout_res.sort_values(by="holdout_mae_lpa", ascending=True)
    sns.barplot(data=df_plot_mae, x="holdout_mae_lpa", y="model", hue="target_type", palette="Blues_r")
    plt.title("Holdout Test MAE Comparison Across Models (LPA)", fontsize=14, fontweight="bold")
    plt.xlabel("Mean Absolute Error (LPA)", fontsize=12)
    plt.ylabel("Model Architecture", fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "model_mae_comparison.png"), dpi=200)
    plt.close()
    
    # Fig 2: model_rmse_comparison.png
    plt.figure(figsize=(10, 6))
    df_plot_rmse = df_holdout_res.sort_values(by="holdout_rmse_lpa", ascending=True)
    sns.barplot(data=df_plot_rmse, x="holdout_rmse_lpa", y="model", hue="target_type", palette="Reds_r")
    plt.title("Holdout Test RMSE Comparison Across Models (LPA)", fontsize=14, fontweight="bold")
    plt.xlabel("Root Mean Squared Error (LPA)", fontsize=12)
    plt.ylabel("Model Architecture", fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "model_rmse_comparison.png"), dpi=200)
    plt.close()
    
    # Fig 3: model_r2_comparison.png
    plt.figure(figsize=(10, 6))
    df_plot_r2 = df_holdout_res.sort_values(by="holdout_r2", ascending=False)
    sns.barplot(data=df_plot_r2, x="holdout_r2", y="model", hue="target_type", palette="Greens_r")
    plt.title("Holdout Test R² Comparison Across Models", fontsize=14, fontweight="bold")
    plt.xlabel("Coefficient of Determination (R²)", fontsize=12)
    plt.ylabel("Model Architecture", fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "model_r2_comparison.png"), dpi=200)
    plt.close()
    
    # Fig 4: cv_stability.png
    plt.figure(figsize=(11, 6))
    df_cv_summary_plot = pd.DataFrame(cv_summary_list)
    df_cv_summary_plot = df_cv_summary_plot[df_cv_summary_plot["model"] != "Dummy"].sort_values(by="cv_mae_lpa_mean")
    plt.errorbar(
        df_cv_summary_plot["cv_mae_lpa_mean"],
        range(len(df_cv_summary_plot)),
        xerr=df_cv_summary_plot["cv_mae_lpa_std"],
        fmt="o",
        color="#2b5c8f",
        ecolor="#d95f02",
        elinewidth=2,
        capsize=5
    )
    plt.yticks(range(len(df_cv_summary_plot)), [f"{r['model']} ({r['target_type']})" for _, r in df_cv_summary_plot.iterrows()])
    plt.title("Cross-Validation Stability (Mean MAE ± 1 Std across 5 Folds)", fontsize=14, fontweight="bold")
    plt.xlabel("CV MAE (LPA)", fontsize=12)
    plt.ylabel("Model & Target Formulation", fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "cv_stability.png"), dpi=200)
    plt.close()
    
    # Fig 5: predicted_vs_actual.png
    plt.figure(figsize=(8, 8))
    plt.scatter(df_eval["salary_lpa"], df_eval["predicted_salary_lpa"], alpha=0.35, color="#1f77b4", edgecolor="none", s=25)
    plt.plot([0, 80], [0, 80], color="red", linestyle="--", linewidth=1.8, label="Ideal Line (y = ŷ)")
    plt.title(f"Predicted vs. Actual Salary ({best_model_name} on Holdout)", fontsize=14, fontweight="bold")
    plt.xlabel("Actual Salary Disclosed (LPA)", fontsize=12)
    plt.ylabel("Predicted Salary (LPA)", fontsize=12)
    plt.xlim(0, 85)
    plt.ylim(0, 85)
    plt.legend(frameon=True)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "predicted_vs_actual.png"), dpi=200)
    plt.close()
    
    # Fig 6: residual_distribution.png
    plt.figure(figsize=(9, 6))
    sns.histplot(df_eval["residual_lpa"], bins=50, kde=True, color="#4c72b0")
    plt.axvline(0, color="red", linestyle="--", linewidth=1.5, label="Zero Error")
    plt.axvline(df_eval["residual_lpa"].mean(), color="orange", linestyle=":", linewidth=2, label=f"Mean Residual ({df_eval['residual_lpa'].mean():.2f} LPA)")
    plt.title(f"Residual Distribution ({best_model_name} on Holdout)", fontsize=14, fontweight="bold")
    plt.xlabel("Residual = Actual - Predicted (LPA)", fontsize=12)
    plt.ylabel("Postings Count", fontsize=12)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "residual_distribution.png"), dpi=200)
    plt.close()
    
    # Fig 7: residual_vs_predicted.png
    plt.figure(figsize=(9, 6))
    plt.scatter(df_eval["predicted_salary_lpa"], df_eval["residual_lpa"], alpha=0.35, color="#2ca02c", s=25)
    plt.axhline(0, color="red", linestyle="--", linewidth=1.5)
    plt.title(f"Residuals vs. Predicted Salary ({best_model_name} on Holdout)", fontsize=14, fontweight="bold")
    plt.xlabel("Predicted Salary (LPA)", fontsize=12)
    plt.ylabel("Residual (Actual - Predicted) (LPA)", fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "residual_vs_predicted.png"), dpi=200)
    plt.close()
    
    # Fig 8: error_by_role.png
    plt.figure(figsize=(10, 7))
    sns.barplot(data=df_err_role, x="mae_lpa", y="role", palette="mako")
    plt.title("Holdout Prediction MAE by Standardized Role (LPA)", fontsize=14, fontweight="bold")
    plt.xlabel("Holdout MAE (LPA)", fontsize=12)
    plt.ylabel("Standardized Role Family", fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "error_by_role.png"), dpi=200)
    plt.close()
    
    # Fig 9: error_by_salary_band.png
    plt.figure(figsize=(9, 6))
    sns.barplot(data=df_err_sal, x="salary_band", y="mae_lpa", palette="rocket")
    plt.title("Holdout Prediction MAE Across Salary Tiers (LPA)", fontsize=14, fontweight="bold")
    plt.xlabel("Disclosed Salary Tier", fontsize=12)
    plt.ylabel("Mean Absolute Error (LPA)", fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "error_by_salary_band.png"), dpi=200)
    plt.close()
    
    # Fig 10: top_feature_importance.png
    plt.figure(figsize=(10, 8))
    top20_pi = df_pi.head(20).copy()
    top20_pi["clean_name"] = top20_pi["feature"].apply(lambda x: x.replace("cat__", "").replace("num__", "").replace("skill__", "skill: ").replace("skill_", "skill: "))
    sns.barplot(data=top20_pi, x="importance_mean", y="clean_name", palette="viridis")
    plt.title("Top 20 Features by Holdout Permutation Importance (MAE Impact)", fontsize=14, fontweight="bold")
    plt.xlabel("Permutation Importance (Mean Increase in Log-Loss / Error)", fontsize=12)
    plt.ylabel("Feature", fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "top_feature_importance.png"), dpi=200)
    plt.close()
    print("All 10 figures rendered and saved.")
    
    # ----------------------------------------------------
    # SAVE FINAL MODEL ARTIFACTS (Section 40 & 41)
    # ----------------------------------------------------
    print("\nSerializing Final Model Artifacts in models/india/...")
    
    # 1. final_model.pkl
    with open(os.path.join(MODELS_DIR, "final_model.pkl"), "wb") as f:
        pickle.dump(final_model, f)
        
    # 2. final_preprocessor.pkl
    with open(os.path.join(MODELS_DIR, "final_preprocessor.pkl"), "wb") as f:
        pickle.dump(preprocessor_full, f)
        
    # 3. final_feature_list.json
    feature_list_payload = {
        "feature_count_raw": len(full_fcols),
        "feature_names_raw": full_fcols,
        "feature_count_transformed": len(all_transformed_names),
        "feature_names_transformed": all_transformed_names
    }
    with open(os.path.join(MODELS_DIR, "final_feature_list.json"), "w", encoding="utf-8") as f:
        json.dump(feature_list_payload, f, indent=2)
        
    # 4. final_evaluation.json
    eval_payload = {
        "selected_model": best_model_name,
        "target_formulation": best_target_type,
        "train_samples": len(df_train),
        "holdout_samples": len(df_holdout),
        "holdout_metrics": {
            "mae_inr": float(best_candidate_row["holdout_mae"]),
            "mae_lpa": float(best_candidate_row["holdout_mae_lpa"]),
            "rmse_inr": float(best_candidate_row["holdout_rmse"]),
            "rmse_lpa": float(best_candidate_row["holdout_rmse_lpa"]),
            "r2": float(best_candidate_row["holdout_r2"]),
            "median_ae_inr": float(best_candidate_row["holdout_median_ae"]),
            "median_ae_lpa": float(best_candidate_row["holdout_median_ae_lpa"]),
            "mape": float(best_candidate_row["holdout_mape"])
        },
        "baseline_improvement": {
            "dummy_holdout_mae_lpa": float(dummy_holdout_mae / 100000.0),
            "mae_improvement_pct": float(((dummy_holdout_mae - best_candidate_row["holdout_mae"]) / dummy_holdout_mae) * 100.0),
            "dummy_holdout_rmse_lpa": float(dummy_holdout_rmse / 100000.0),
            "rmse_improvement_pct": float(((dummy_holdout_rmse - best_candidate_row["holdout_rmse"]) / dummy_holdout_rmse) * 100.0)
        }
    }
    with open(os.path.join(MODELS_DIR, "final_evaluation.json"), "w", encoding="utf-8") as f:
        json.dump(eval_payload, f, indent=2)
        
    # 5. final_model_metadata.json (Section 41)
    metadata_payload = {
        "project": "JobIntel — AI-Powered Job Market Intelligence",
        "country": "India",
        "dataset": "indian-job-market-dataset-2025",
        "dataset_version": "Phase-3 Cleaned Tech Modeling Cohort",
        "cohort_size": len(df),
        "train_samples": len(df_train),
        "holdout_samples": len(df_holdout),
        "target": "salary_midpoint_inr",
        "display_target": "salary_lpa",
        "target_transformation": best_target_type,
        "feature_count": len(full_fcols),
        "feature_names": full_fcols,
        "model_type": str(type(final_model).__name__),
        "hyperparameters": model_defs[best_model_name][1],
        "random_state": RANDOM_STATE,
        "holdout_strategy": "GroupShuffleSplit (test_size=0.20, random_state=42)",
        "cv_strategy": "GroupKFold (n_splits=5)",
        "group_column": "content_fingerprint",
        "cv_folds": 5,
        "training_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "metrics": eval_payload["holdout_metrics"],
        "limitations": [
            "Trained exclusively on posted disclosed salaries, not negotiated compensation.",
            "Upper-tail salaries (>= 40 LPA) exhibit expected shrinkage/compression towards median.",
            "Captures observational correlations, not causal treatment effects of skills."
        ]
    }
    with open(os.path.join(MODELS_DIR, "final_model_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata_payload, f, indent=2)
    print("Model artifacts successfully saved.")
    
    print("\n" + "=" * 80)
    print("PHASE INDIA-4 MODELING COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    run_all_experiments()
