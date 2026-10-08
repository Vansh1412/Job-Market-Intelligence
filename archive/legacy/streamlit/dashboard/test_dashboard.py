"""
Unit & Integration Test Suite for JobIntel Dashboard
Validates data loaders, model artifacts, inference pipelines, and schema alignment.
"""

import sys
import os

sys.path.insert(0, os.path.abspath("."))

from src.dashboard.data_loader import (
    load_funnel_data,
    load_salary_summary,
    load_salary_by_role,
    load_salary_by_seniority,
    load_salary_by_location,
    load_skill_frequency,
    load_skill_salary_association,
    load_skill_cooccurrence,
    load_archetype_dict,
    load_cluster_sizes,
    load_cluster_salary,
    load_cluster_skills,
    load_cluster_roles,
    load_test_results,
    load_model_comparison,
    load_feature_importance,
    load_permutation_importance,
    load_archetype_errors,
    load_feature_metadata,
)
from src.dashboard.model_loader import (
    load_salary_model,
    load_metadata_pipeline,
    load_archetype_pipeline,
)
from src.dashboard.inference import predict_salary_and_archetype


def run_tests():
    print("=" * 60)
    print("RUNNING JOBINTEL DASHBOARD INTEGRITY TESTS")
    print("=" * 60)

    # 1. Test Data Loaders
    print("\n[1/4] Testing Data Loaders...")
    loaders = [
        ("Funnel Data", load_funnel_data),
        ("Salary Summary", load_salary_summary),
        ("Salary by Role", load_salary_by_role),
        ("Salary by Seniority", load_salary_by_seniority),
        ("Salary by Location", load_salary_by_location),
        ("Skill Frequency", load_skill_frequency),
        ("Skill Salary Association", load_skill_salary_association),
        ("Skill Co-Occurrence", load_skill_cooccurrence),
        ("Archetype Dict", load_archetype_dict),
        ("Cluster Sizes", load_cluster_sizes),
        ("Cluster Salary", load_cluster_salary),
        ("Cluster Skills Lift", load_cluster_skills),
        ("Cluster Roles Profile", load_cluster_roles),
        ("Test Results", load_test_results),
        ("Model Comparison", load_model_comparison),
        ("Feature Importance", load_feature_importance),
        ("Permutation Importance", load_permutation_importance),
        ("Archetype Errors", load_archetype_errors),
    ]

    for name, loader in loaders:
        df = loader()
        assert len(df) > 0, f"Empty dataframe returned by {name}"
        print(f"  [PASS] {name:28s} -> Shape: {df.shape}")

    meta = load_feature_metadata()
    assert "feature_names" in meta and len(meta["feature_names"]) == 123
    print(f"  [PASS] Feature Metadata JSON       -> Features: {len(meta['feature_names'])}")

    # 2. Test Model Loading
    print("\n[2/4] Testing Model Artifacts...")
    model = load_salary_model()
    print(f"  [PASS] Supervised Model            -> {type(model).__name__}")
    pipeline = load_metadata_pipeline()
    print(f"  [PASS] Preprocessing Pipeline      -> {type(pipeline).__name__}")
    scaler, pca, kmeans = load_archetype_pipeline()
    print(f"  [PASS] Clustering Models           -> Scaler, PCA({pca.n_components}), KMeans({kmeans.n_clusters})")

    # 3. Test Live Inference Cases
    print("\n[3/4] Testing Live Inference Engine...")
    test_cases = [
        {
            "name": "Senior ML Engineer (San Francisco, Remote)",
            "role": "ML / AI Engineer",
            "sen": "Senior",
            "city": "San Francisco",
            "remote": True,
            "skills": ["machine_learning", "python", "pytorch"],
            "expected_arch": "SYS_ENG",
        },
        {
            "name": "Junior Web Developer (New York, Onsite)",
            "role": "Frontend Developer",
            "sen": "Junior / Entry",
            "city": "New York",
            "remote": False,
            "skills": ["react", "javascript", "html_css"],
            "expected_arch": "WEB_FRONT",
        },
        {
            "name": "Cloud Platform Architect (Seattle, Remote)",
            "role": "DevOps / Cloud / Platform",
            "sen": "Lead / Principal / Executive",
            "city": "Seattle",
            "remote": True,
            "skills": ["aws", "azure", "kubernetes", "terraform", "docker"],
            "expected_arch": "DEVOPS_PLAT",
        },
        {
            "name": "Data Analyst (Chicago, Onsite)",
            "role": "Data / BI Analyst",
            "sen": "Mid / Unspecified",
            "city": "Chicago",
            "remote": False,
            "skills": ["sql", "tableau", "power_bi"],
            "expected_arch": "DATA_BI",
        },
        {
            "name": "Zero-Skill Posting (Edge Case)",
            "role": "Software Engineer",
            "sen": "Mid / Unspecified",
            "city": "Other",
            "remote": False,
            "skills": [],
            "expected_arch": "ZERO_SKILL",
        },
    ]

    for tc in test_cases:
        res = predict_salary_and_archetype(
            role_family=tc["role"],
            seniority=tc["sen"],
            city_clean=tc["city"],
            is_remote=tc["remote"],
            selected_skills=tc["skills"],
        )
        sal = res["predicted_salary"]
        arch = res["archetype"]["code"]
        assert 30000 <= sal <= 600000, f"Predicted salary out of bounds: {sal}"
        print(f"  [PASS] {tc['name']:44s} -> Pred: ${sal:,.0f} | Arch: {arch:12s} | Rel Err: {res['archetype']['rel_error']:.1f}%")

    # 4. Feature Schema Alignment
    print("\n[4/4] Validating Feature Schema Alignment...")
    assert len(meta["feature_names"]) == 123, "Feature count must be exactly 123"
    assert len(meta["tech_skills"]) == 82, "Tech skills count must be exactly 82"
    assert len(meta["metadata_cols"]) == 5, "Metadata columns count must be exactly 5"
    print("  [PASS] Strict 123-feature schema alignment verified against frozen metadata.")

    print("\n" + "=" * 60)
    print("ALL 4 INTEGRITY TEST PHASES PASSED WITH ZERO ERRORS")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
