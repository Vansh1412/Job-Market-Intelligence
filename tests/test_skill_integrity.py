"""
tests/test_skill_integrity.py
==============================
Strict skill integrity verification suite for India market intelligence (BUG #1, #2, #14).
Validates that:
1. /api/india/skills returns empirical, non-fabricated metrics for all skills.
2. Skills like Python, SAP, React, Java, AWS, SQL, and Machine Learning return
   distinct, specialized profiles (roles, archetypes, co-occurring skills, and salaries).
3. No synthetic step-function logic (e.g. prev > 20 ? 14.5 : 12.0) exists.
4. Descriptive statistics use 'observed salary difference' rather than causal claims.
"""

import pytest
from fastapi.testclient import TestClient
from src.backend.main import app

client = TestClient(app)


def test_india_skills_list_endpoint():
    """Verify GET /api/india/skills returns all empirical skills with real metrics."""
    response = client.get("/api/india/skills")
    assert response.status_code == 200
    data = response.json()
    assert data["country"] == "India"
    assert data["currency"] == "INR"
    assert data["total_skills"] == 284
    skills = data["skills"]
    assert len(skills) == 284

    # Verify first 10 skills contain required empirical fields
    for s in skills[:10]:
        assert "skill" in s
        assert "display_name" in s
        assert "posting_count" in s
        assert "demand_percentage" in s
        assert "observed_median_salary_lpa" in s
        assert "observed_salary_difference_lpa" in s
        assert "associated_roles" in s
        assert "associated_archetypes" in s
        assert "cooccurring_skills" in s
        assert isinstance(s["observed_median_salary_lpa"], (int, float))
        assert s["observed_median_salary_lpa"] > 0


def test_distinct_skill_profiles():
    """Verify Python, SAP, React, Java, AWS, SQL, and ML have distinct empirical profiles."""
    test_skills = ["python", "sap", "react", "java", "aws", "sql", "machine_learning"]
    profiles = {}

    for s_name in test_skills:
        response = client.get(f"/api/india/skills/{s_name}")
        assert response.status_code == 200, f"Failed to fetch detail for {s_name}: {response.text}"
        profiles[s_name] = response.json()

    # 1. Python vs SAP must NOT have identical median salaries or archetypes
    assert profiles["python"]["observed_median_salary_lpa"] != profiles["sap"]["observed_median_salary_lpa"]
    assert profiles["python"]["associated_archetypes"] != profiles["sap"]["associated_archetypes"]

    # 2. React vs Java must have different co-occurring skills
    assert profiles["react"]["cooccurring_skills"] != profiles["java"]["cooccurring_skills"]

    # 3. SAP must be associated with Enterprise/ERP, while Python with AI/Data
    assert any("ERP" in arc or "Enterprise" in arc for arc in profiles["sap"]["associated_archetypes"])
    assert any("AI" in arc or "Data" in arc for arc in profiles["python"]["associated_archetypes"])

    # 4. Verify non-trivial postings counts
    for s_name, prof in profiles.items():
        assert prof["posting_count"] > 0, f"{s_name} has zero postings"
        assert prof["demand_percentage"] > 0, f"{s_name} has zero demand percentage"


def test_no_synthetic_step_function():
    """Verify that observed median salaries vary continuously across skills and do not match step functions."""
    response = client.get("/api/india/skills")
    skills = response.json()["skills"]
    
    # Collect all unique observed median salaries
    unique_medians = set(s["observed_median_salary_lpa"] for s in skills)
    
    # In a synthetic step function, there are only 2 or 3 distinct values (e.g. 14.5, 12.0, 10.5).
    # Empirical calculation yields dozens of distinct medians.
    assert len(unique_medians) >= 15, f"Observed medians appear stepped: only {len(unique_medians)} unique values found"


def test_unknown_skill_detail():
    """Verify unknown skill returns 404 for India."""
    response = client.get("/api/india/skills/nonexistent_xyz_123")
    assert response.status_code == 404


def test_usa_skill_landscape_endpoint():
    """Verify USA skill landscape endpoint returns valid 2D bubble chart data."""
    response = client.get("/api/skills/landscape")
    assert response.status_code == 200
    landscape = response.json()
    assert len(landscape) >= 30, "USA skill landscape should contain at least 30 categorized skills"

    for item in landscape[:10]:
        assert "skill" in item
        assert "category" in item
        assert "prevalence_pct" in item
        assert item["prevalence_pct"] > 0
        assert "median_salary" in item
        assert item["median_salary"] > 0
        assert "postings" in item
        assert item["postings"] > 0


def test_usa_skill_detail_endpoint():
    """Verify USA skill detail endpoint returns empirical metrics, roles, and archetypes."""
    test_skills = ["python", "sql", "aws"]
    for skill_name in test_skills:
        response = client.get(f"/api/skills/detail/{skill_name}")
        assert response.status_code == 200, f"Expected 200 for USA skill {skill_name}, got {response.status_code}"
        data = response.json()

        # Canonical contract fields
        assert data["skill"].lower() == skill_name
        assert data["postings"] > 0, f"Postings for {skill_name} should be > 0"
        assert data["prevalence_pct"] > 0, f"Prevalence for {skill_name} should be > 0"
        assert data["median_salary"] >= 100000, f"Median salary for {skill_name} should be realistic"
        assert isinstance(data["delta_vs_cohort"], (int, float))

        # Empirical associations
        assert isinstance(data["roles"], list)
        assert len(data["roles"]) > 0, f"Roles for {skill_name} should not be empty"
        assert isinstance(data["archetypes"], list)
        assert len(data["archetypes"]) > 0, f"Archetypes for {skill_name} should not be empty"
        assert isinstance(data["combos"], list)
        assert len(data["combos"]) > 0, f"Combos for {skill_name} should not be empty"

        # Backward-compatible convenience aliases
        assert data["median_with"] == data["median_salary"]
        assert data["prevalence"] == data["prevalence_pct"]
        assert data["delta"] == data["delta_vs_cohort"]
        assert data["associated_roles"] == data["roles"]
        assert data["associated_archetypes"] == data["archetypes"]
        assert data["cooccurring_skills"] == data["combos"]


def test_usa_unknown_skill_returns_404():
    """Verify unknown USA skill cleanly returns HTTP 404 rather than 200 with error dict."""
    response = client.get("/api/skills/detail/nonexistent_xyz_999")
    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
    assert "not found" in response.json()["detail"].lower()


def test_usa_skill_distinct_profiles():
    """Verify Python, SQL, and AWS produce distinct empirical roles and archetypes."""
    res_py = client.get("/api/skills/detail/python").json()
    res_sql = client.get("/api/skills/detail/sql").json()
    res_aws = client.get("/api/skills/detail/aws").json()

    assert res_py["median_salary"] != res_sql["median_salary"] or res_py["prevalence_pct"] != res_sql["prevalence_pct"]
    assert res_py["roles"] != res_aws["roles"] or res_py["archetypes"] != res_aws["archetypes"]


def test_skills_frequency_service_when_csv_absent():
    """Verify that skill analytics compute accurately from mounted dataset when CSV is absent (Phase 8.6.6)."""
    import os
    from unittest.mock import patch
    from src.backend import data_service

    orig_exists = os.path.exists

    def mock_exists_no_csv(path):
        if str(path).endswith(".csv"):
            return False
        return orig_exists(path)

    with patch("os.path.exists", side_effect=mock_exists_no_csv):
        data_service.get_skill_frequency_df.cache_clear()
        df_freq = data_service.get_skill_frequency_df()

        assert df_freq is not None
        assert len(df_freq) == 82, f"Expected 82 canonical skills, got {len(df_freq)}"
        required_cols = {"Skill", "Modeling_Count", "Modeling_Prevalence", "Corpus_Count", "Corpus_Prevalence", "Postings", "Prevalence_Pct", "IDF_Score"}
        assert required_cols.issubset(set(df_freq.columns))

        # Check empirical truth for anchor skills
        py_row = df_freq[df_freq["Skill"] == "python"].iloc[0]
        assert py_row["Modeling_Count"] == 11593
        assert py_row["Corpus_Count"] == 31676
        assert round(py_row["Modeling_Prevalence"], 4) == round(11593 / 34036, 4)

    # Restore cache
    data_service.get_skill_frequency_df.cache_clear()


def test_prevalence_computation_deterministic_fixture():
    """Verify prevalence math on small deterministic fixture."""
    import pandas as pd
    import numpy as np

    fixture = pd.DataFrame({
        "skill_a": [1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
        "skill_b": [0, 1, 1, 1, 1, 0, 0, 0, 0, 0],
        "skill_c": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    })
    n = len(fixture)
    assert n == 10
    prev_a = fixture["skill_a"].sum() / n
    prev_b = fixture["skill_b"].sum() / n
    prev_c = fixture["skill_c"].sum() / n

    assert prev_a == 0.3
    assert prev_b == 0.4
    assert prev_c == 0.0


def test_skills_explorer_endpoints_without_csv():
    """Verify USA Skills Explorer API routes succeed when CSV tables are deleted/absent."""
    import os
    from unittest.mock import patch
    from src.backend import data_service

    orig_exists = os.path.exists

    def mock_exists_no_csv(path):
        if str(path).endswith(".csv"):
            return False
        return orig_exists(path)

    with patch("os.path.exists", side_effect=mock_exists_no_csv):
        data_service.get_skill_frequency_df.cache_clear()
        data_service.get_skill_salary_association_df.cache_clear()
        data_service.get_skill_cooccurrence_df.cache_clear()
        data_service.get_cluster_skill_lift_df.cache_clear()

        # 1. Detail endpoint for Python
        res_detail = client.get("/api/skills/detail/python")
        assert res_detail.status_code == 200
        detail = res_detail.json()
        assert detail["skill"] == "python"
        assert detail["postings"] > 0
        assert detail["prevalence_pct"] > 0
        assert detail["median_salary"] > 0
        assert len(detail["roles"]) > 0
        assert len(detail["archetypes"]) > 0
        assert len(detail["combos"]) > 0

        # 2. Unknown skill still returns 404
        res_404 = client.get("/api/skills/detail/nonexistent_xyz_999")
        assert res_404.status_code == 404

        # 3. Frequency endpoint
        res_freq = client.get("/api/skills/frequency")
        assert res_freq.status_code == 200
        freq_list = res_freq.json()
        assert len(freq_list) == 82
        assert freq_list[0]["Postings"] > 0

        # 4. Landscape endpoint
        res_land = client.get("/api/skills/landscape")
        assert res_land.status_code == 200
        land_list = res_land.json()
        assert len(land_list) >= 30

        # 5. USA skills endpoint
        res_usa = client.get("/api/usa/skills")
        assert res_usa.status_code == 200
        assert len(res_usa.json()["skills"]) == 82

    # Restore cache
    data_service.get_skill_frequency_df.cache_clear()
    data_service.get_skill_salary_association_df.cache_clear()
    data_service.get_skill_cooccurrence_df.cache_clear()
    data_service.get_cluster_skill_lift_df.cache_clear()


def test_service_does_not_fabricate_when_source_unavailable():
    """Verify data service raises FileNotFoundError and does NOT fabricate data when datasets are missing."""
    import os
    from unittest.mock import patch
    from src.backend import data_service

    def mock_no_files(path):
        return False

    with patch("os.path.exists", side_effect=mock_no_files):
        data_service.get_skill_frequency_df.cache_clear()
        with pytest.raises(FileNotFoundError):
            data_service.get_skill_frequency_df()

    data_service.get_skill_frequency_df.cache_clear()


