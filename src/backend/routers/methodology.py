"""
Methodology API Router — Reproducibility Pipeline, Leakage Controls, and Core Limitations
"""

from fastapi import APIRouter

router = APIRouter(prefix="/methodology", tags=["Methodology"])


@router.get("/pipeline-stages")
def get_pipeline_stages():
    return [
        {"id": "Phase 1", "title": "Data Harvesting & Provenance", "badge": "394,300 raw", "desc": "Ingestion of Tier-1 ATS postings with metadata verification and source provenance audit.", "color": "#8B5CF6"},
        {"id": "Phase 2", "title": "Deduplication & Preprocessing", "badge": "335,995 clean", "desc": "Whitespace and casing normalization; title family categorization; remote work standardization.", "color": "#6366F1"},
        {"id": "Phase 2.1", "title": "Scientific Taxonomy Cleaning", "badge": "82 skills", "desc": "Correction of non-standard token collisions into validated Taxonomy D dictionary.", "color": "#06B6D4"},
        {"id": "Phase 3", "title": "Exploratory Data Analysis", "badge": "Full EDA", "desc": "Corpus distributions, skill frequency, salary association, and pairwise co-occurrence matrices.", "color": "#14B8A6"},
        {"id": "Phase 4.1", "title": "Skill-Bearing Archetype Discovery", "badge": "116,830 pop", "desc": "Quarantined 0-skill postings; PCA 15 components (56.05% var) + K-Means k=7 (ARI 0.7901).", "color": "#10B981"},
        {"id": "Phase 4.2", "title": "Scientific Archetype Audit", "badge": "Frozen SSOT", "desc": "Rigorous statistical validation of cluster stability, separation, and archetype naming.", "color": "#F59E0B"},
        {"id": "Phase 5", "title": "Supervised Salary Modeling", "badge": "34,036 cohort", "desc": "80/20 train/test split; 5 candidate algorithms; Optuna-tuned XGBoost best model ($36,381 MAE).", "color": "#EC4899"},
        {"id": "Phase 6", "title": "Synthesis & Distinction Packaging", "badge": "Complete", "desc": "Defensive reporting, limitation boundary documentation, and artifact verification.", "color": "#8B5CF6"},
    ]


@router.get("/leakage-controls")
def get_leakage_controls():
    return [
        {
            "title": "Fit-on-Train Exclusivity",
            "tag": "Preprocessing Isolation",
            "color": "#10B981",
            "body": "The MetadataTransformer pipeline was fitted strictly on the 80% training partition (N = 27,228). No validation or holdout test statistics leaked into one-hot categories, frequency lookups, or numerical scalers.",
        },
        {
            "title": "Fold-Safe Archetype Assignment",
            "tag": "Clustering Independence",
            "color": "#06B6D4",
            "body": "In Feature Set C, PCA components and K-Means centroids were fitted inside each CV training fold. Holdout test archetypes were predicted via nearest-distance assignment from frozen training centroids.",
        },
    ]


@router.get("/limitations")
def get_limitations():
    return [
        {"id": 1, "title": "Salary Disclosure Bias", "body": "Employers disclosing compensation in ATS records skew toward larger tech enterprises and pay transparency mandate jurisdictions."},
        {"id": 2, "title": "Base Midpoint Incompleteness", "body": "Target reflects base salary midpoints only, excluding equity grants, RSUs, performance bonuses, and signing packages which form a major share of senior tech pay."},
        {"id": 3, "title": "Binary Skill Indicators", "body": "Skills are represented as binary presence/absence indicators (0/1). Depth of expertise, years of experience, and proficiency levels are uncaptured."},
        {"id": 4, "title": "Curated Taxonomy Boundaries", "body": "Taxonomy D covers 82 curated technical competencies. Proprietary frameworks, niche internal tools, and newly emerging libraries are unrepresented."},
        {"id": 5, "title": "Upper-Tail Sparsity", "body": "Postings with midpoints > $350,000 are relatively sparse in standard ATS records, leading to higher prediction residuals in executive architect bands."},
        {"id": 6, "title": "FOUND_TECH Residual Cohort", "body": "The largest archetype (FOUND_TECH, 49.5%) is a heterogeneous residual group (85.3% have ≤2 skills) rather than a tightly coherent professional specialty."},
        {"id": 7, "title": "PCA Dimensionality Loss", "body": "The 15 retained continuous Principal Components capture 56.05% of skill variance; 43.95% remains outside the compressed latent space."},
        {"id": 8, "title": "Observational Bounds (No Causality)", "body": "All findings represent observational labor market associations. Acquiring a skill does not causally produce or guarantee higher market wages."},
        {"id": 9, "title": "Geographic Generalization Limits", "body": "Data is sourced from North American technology job boards; conclusions cannot be automatically generalized to global tech compensation markets."},
    ]
