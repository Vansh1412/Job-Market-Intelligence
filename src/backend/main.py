"""
JobIntel Production Backend Application — FastAPI
==================================================
Unified cross-market AI-powered job salary and career intelligence engine.
Exposes typed REST endpoints for USA, India, and Comparative Analytics.
Guarantees frozen model artifact verification via Centralized ModelRegistry.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.backend.models.model_registry import get_model_registry
from src.backend.utils.s3_sync import sync_and_verify_artifacts
from src.backend.routers import (
    usa,
    india,
    cross_market,
    overview,
    salary,
    skills,
    archetypes,
    predict,
    models,
    error_analysis,
    methodology,
    v1,
    uk_salary,
    occupations,
    demand,
)

from contextlib import asynccontextmanager
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("jobintel.api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Synchronize cloud artifacts, verify cryptographic signatures, and warm up model artifacts on server boot."""
    logger.info("Starting JobIntel Unified API Server...")
    try:
        sync_report = sync_and_verify_artifacts(enforce_all=False)
        logger.info(
            "Cloud Artifact Sync Report: Status %s (Mandatory: %s, Metadata: %s, Optional Cohorts: %s, Completeness: %s)",
            sync_report["status"],
            sync_report.get("mandatory_models_verified", "9/9"),
            sync_report.get("metadata_verified", "6/6"),
            sync_report.get("optional_datasets_available", "0/4"),
            sync_report.get("sync_completeness", "PARTIAL_MANDATORY_VERIFIED"),
        )
    except Exception as e:
        logger.error("Cloud Artifact Sync encountered an error: %s", str(e))

    registry = get_model_registry()
    status = registry.get_status_report()
    logger.info(
        "Model Registry Status: %s (Mandatory Models: %d/%d verified, Optional Cohorts: %d/%d mounted)",
        status["status"],
        status["mandatory_verified_count"],
        status.get("mandatory_total_count", 9),
        status.get("optional_verified_count", 0),
        status.get("optional_total_count", 1),
    )
    yield
    logger.info("Shutting down JobIntel API Server.")

app = FastAPI(
    title="JobIntel Unified API",
    description="Cross-Market AI-Powered Job Salary & Career Intelligence Engine (USA + India)",
    version="2.0.0",
    lifespan=lifespan,
)

import os

# Standard default CORS origins for local development and production deployments
DEFAULT_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://job-market-intelligence-dusky.vercel.app",
    "https://job-market-intelligence.vercel.app",
    "https://jobintel.vercel.app",
    "https://jobintel-staging.vercel.app",
]

# Configurable CORS origins for development and production deployments
raw_origins = os.getenv("CORS_ORIGINS", "")
env_origins = [o.strip() for o in raw_origins.split(",") if o.strip()]

# Merge while preserving order, ensuring uniqueness, and strictly forbidding wildcards
allowed_origins: list[str] = []
for orig in DEFAULT_CORS_ORIGINS + env_origins:
    if orig and orig != "*" and orig not in allowed_origins:
        allowed_origins.append(orig)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Unified & Domain Routers under both /api and root /
# Guarantees seamless backward compatibility for frontends configured with or without an /api base URL.
api_routers = [
    usa.router,
    india.router,
    cross_market.router,
    overview.router,
    salary.router,
    skills.router,
    archetypes.router,
    predict.router,
    models.router,
    error_analysis.router,
    methodology.router,
]

for r in api_routers:
    app.include_router(r, prefix="/api")
    app.include_router(r)

app.include_router(v1.router, prefix="/api")
app.include_router(uk_salary.router, prefix="/api")
app.include_router(occupations.router, prefix="/api")
app.include_router(occupations.router)
app.include_router(salary.v1_salary_router, prefix="/api")
app.include_router(salary.v1_salary_router)
app.include_router(demand.router, prefix="/api")
app.include_router(demand.router)


@app.get("/")
def root():
    return {
        "status": "online",
        "service": "JobIntel Unified Job Market Intelligence API",
        "version": "2.0.0",
        "markets_supported": ["USA", "India"],
        "pipeline_status": "Phase India-6 Live Production Integration (SSOT)",
    }


@app.get("/health")
@app.get("/api/health")
def health_check():
    """Liveness probe: returns HTTP 200 if the web process is running and responsive."""
    registry = get_model_registry()
    status = registry.get_status_report()
    return {
        "status": "healthy" if status["status"] == "GREEN" else "degraded",
        "service": "JobIntel Unified API",
        "version": "2.0.0",
        "registry": status,
    }


@app.get("/ready")
@app.get("/api/ready")
def readiness_check():
    """Readiness probe: answers 'Are all required production models available?'."""
    from fastapi.responses import JSONResponse
    registry = get_model_registry()
    status = registry.get_status_report()
    is_ready = status["status"] == "GREEN" and (
        status["artifacts_verified_count"] == 10 or status.get("mandatory_verified_count", 0) >= 9
    )
    if is_ready:
        return {
            "status": "ready",
            "ready": True,
            "artifacts_verified_count": status["artifacts_verified_count"],
            "markets": ["USA", "India"],
        }
    return JSONResponse(
        status_code=503,
        content={
            "status": "not_ready",
            "ready": False,
            "reason": "Required production model artifacts missing or failed checksum validation.",
            "details": status,
        },
    )


@app.get("/meta")
@app.get("/api/meta")
def get_metadata():
    """Returns comprehensive metadata, research parameters, and cohort metrics."""
    return {
        "project": "JobIntel — AI-Powered Job Market Intelligence",
        "version": "2.0.0",
        "date": "October 2026",
        "status": "Production Frozen",
        "governance": {
            "zero_retraining": True,
            "zero_fx_currency_conversion": True,
            "deterministic_inference": True,
            "leakage_controls_certified": True,
        },
        "usa_pipeline": {
            "country": "USA",
            "currency": "USD",
            "target": "Annual Base Salary ($)",
            "cohort_size": 34036,
            "feature_count": 123,
            "algorithm": "XGBoost Regressor (Tuned)",
            "holdout_mae": 36380.64,
            "holdout_rmse": 51082.06,
            "r2_score": 0.4233,
            "mape": 21.71,
            "archetype_clusters": 7,
        },
        "india_pipeline": {
            "country": "India",
            "currency": "INR",
            "target": "Annual Salary Midpoint (₹ Lakhs Per Annum)",
            "cohort_size": 5859,
            "feature_count": 290,
            "algorithm": "HistGradientBoostingRegressor",
            "holdout_mae_lpa": 3.71,
            "holdout_mae_inr": 371472.71,
            "holdout_rmse_lpa": 6.22,
            "r2_score": 0.580,
            "median_absolute_error_lpa": 2.08,
            "archetype_clusters": 6,
        },
    }
