"""
Phase 5: Regression Models & Hyperparameter Spaces
==================================================
INT234 Predictive Analytics — Job Market Intelligence
"""

from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from xgboost import XGBRegressor

RANDOM_STATE = 42


def get_baseline_models():
    """Returns naive baseline estimators to anchor predictive error."""
    return {
        "Dummy (Median)": DummyRegressor(strategy="median"),
        "Dummy (Mean)": DummyRegressor(strategy="mean"),
    }


def get_default_models():
    """
    Returns the primary supervised regressors with defensible default configurations.
    Used for 5-fold CV comparison across Feature Sets A, B, and C.
    """
    return {
        "Ridge": Ridge(alpha=10.0, random_state=RANDOM_STATE),
        "Random Forest": RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_leaf=5,
            random_state=RANDOM_STATE,
            n_jobs=-1
        ),
        "Gradient Boosting": GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            min_samples_leaf=5,
            random_state=RANDOM_STATE
        ),
        "XGBoost": XGBRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            tree_method="hist",
            random_state=RANDOM_STATE,
            n_jobs=-1
        ),
        "MLP Regressor": MLPRegressor(
            hidden_layer_sizes=(64, 32),
            activation="relu",
            alpha=0.01,
            batch_size=512,
            learning_rate_init=0.01,
            max_iter=100,
            early_stopping=True,
            n_iter_no_change=10,
            validation_fraction=0.1,
            random_state=RANDOM_STATE
        ),
    }


def get_tuning_grids():
    """
    Compact, meaningful hyperparameter search spaces per Section 17.
    Avoids combinatorial explosion while finding optimal bias/variance compromise.
    """
    return {
        "Ridge": {
            "alpha": [0.1, 1.0, 10.0, 50.0, 100.0, 500.0]
        },
        "Random Forest": {
            "n_estimators": [100, 200],
            "max_depth": [10, 15, 20],
            "min_samples_leaf": [2, 5, 10],
        },
        "Gradient Boosting": {
            "n_estimators": [100, 150],
            "learning_rate": [0.05, 0.1],
            "max_depth": [3, 5],
        },
        "XGBoost": {
            "n_estimators": [100, 150],
            "learning_rate": [0.05, 0.1],
            "max_depth": [4, 6],
            "subsample": [0.8, 1.0],
        },
        "MLP Regressor": {
            "hidden_layer_sizes": [(64, 32), (128, 64)],
            "alpha": [0.001, 0.01, 0.1],
            "learning_rate_init": [0.001, 0.005],
        },
    }
