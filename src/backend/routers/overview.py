"""
Overview API Router — Corpus KPIs, Funnel Attrition, and Research Questions
"""

from fastapi import APIRouter
from src.backend.data_service import get_funnel_df

router = APIRouter(prefix="/api/overview", tags=["Overview"])


@router.get("/kpis")
def get_overview_kpis():
    return {
        "raw_harvested": {"value": 394300, "label": "Raw Postings", "sub": "DataForge ATS Tier 1 Ingestion", "accent": "#8B5CF6"},
        "curated_corpus": {"value": 335995, "label": "Curated Tech Corpus", "sub": "Exact Casing/Whitespace Deduplication", "accent": "#6366F1"},
        "skill_bearing": {"value": 116830, "label": "Skill-Bearing Postings", "sub": "≥1 Parsed Skill · Clustering Population", "accent": "#06B6D4"},
        "salary_cohort": {"value": 34036, "label": "Salary Modeling Cohort", "sub": "Verified Direct USD Midpoints ($30k–$600k)", "accent": "#10B981"},
        "holdout_mae": {"value": "$36,381", "num": 36381, "label": "Holdout Test MAE", "delta": "28.4% vs baseline", "accent": "#EC4899"},
        "holdout_r2": {"value": "0.4233", "num": 0.4233, "label": "Holdout Test R²", "sub": "57.7% Unexplained Variance", "accent": "#8B5CF6"},
        "holdout_rmse": {"value": "$51,082", "num": 51082, "label": "Holdout Test RMSE", "delta": "24.5% vs baseline", "accent": "#06B6D4"},
        "archetypes_count": {"value": 7, "label": "Discovered Archetypes", "sub": "Mean Stability ARI: 0.7901", "accent": "#F59E0B"},
        "skills_count": {"value": 82, "label": "Curated Skills", "sub": "Taxonomy D Standardized Vocabulary", "accent": "#14B8A6"},
    }


@router.get("/funnel")
def get_funnel():
    df = get_funnel_df()
    return df.to_dict(orient="records")


@router.get("/research-questions")
def get_research_questions():
    return [
        {
            "id": "RQ1",
            "number": "Research Question 1",
            "title": "Skill–Salary Associations",
            "question": "Which skills and skill combinations are most associated with higher salaries?",
            "status": "SUPPORTED",
            "color": "#8B5CF6",
            "finding": "AI/ML tools (PyTorch, Deep Learning, TensorFlow) and infrastructure stacks exhibit top observed salary medians ($195k–$197k). Conditional XGBoost importance is dominated by ML, cloud architecture, and systems engineering.",
            "metrics": [
                {"label": "Top Single Skill Median", "value": "$197,500 (PyTorch)"},
                {"label": "Top Stack Median", "value": "$212,500 (PyTorch + Cloud)"},
            ],
        },
        {
            "id": "RQ2",
            "number": "Research Question 2",
            "title": "Latent Archetype Discovery",
            "question": "Do job postings naturally form meaningful skill-based archetypes?",
            "status": "SUPPORTED (WITH OVERLAP)",
            "color": "#06B6D4",
            "finding": "Identified 7 stable clusters (mean ARI = 0.7901). Largest cluster (FOUND_TECH, 49.5%) is a heterogeneous residual cohort dominated by low-specificity postings (85.3% have ≤2 skills).",
            "metrics": [
                {"label": "Number of Clusters", "value": "k = 7 (PCA 15 dims)"},
                {"label": "Stability Metric", "value": "ARI = 0.7901 (K-Fold Bootstrap)"},
            ],
        },
        {
            "id": "RQ3",
            "number": "Research Question 3",
            "title": "Archetype-Specific Error Variance",
            "question": "Does salary-prediction error differ meaningfully across archetypes?",
            "status": "CONFIRMED STATISTICALLY",
            "color": "#10B981",
            "finding": "Kruskal-Wallis H = 88.10 (p = 7.53×10⁻¹⁷) confirms statistically significant error variance. AI_ML has lowest MAE ($27,002) while CLOUD_ARCH has highest ($46,098).",
            "metrics": [
                {"label": "Lowest Error Cluster", "value": "AI_ML ($27,002 MAE)"},
                {"label": "Highest Error Cluster", "value": "CLOUD_ARCH ($46,098 MAE)"},
            ],
        },
    ]


@router.get("/data-flow")
def get_data_flow():
    return [
        {"stage": "Raw Postings", "count": 394300, "pct": "100.0%", "desc": "DataForge ATS Tier 1 Ingestion", "color": "#8B5CF6"},
        {"stage": "Curated Corpus", "count": 335995, "pct": "85.2%", "desc": "Exact deduplication & casing normalization", "color": "#6366F1"},
        {"stage": "Skill-Bearing", "count": 116830, "pct": "29.6%", "desc": "≥1 Parsed technical skill (Clustering population)", "color": "#06B6D4"},
        {"stage": "Salary Model", "count": 34036, "pct": "8.6%", "desc": "Explicit USD compensation midpoints ($30k–$600k)", "color": "#10B981"},
        {"stage": "Archetypes", "count": 7, "pct": "k = 7", "desc": "Discovered latent market roles", "color": "#F59E0B"},
    ]
