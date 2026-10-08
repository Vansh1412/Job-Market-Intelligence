"""
Archetype Inference Parity Automated Test Suite (Phase 7.5)
===========================================================
Validates bitwise and categorical equivalence between direct on-disk
archetype pipeline transformations and FastAPI archetype endpoints.
Tests normal, specialized, sparse, and zero-skill regimes.
"""

import pytest
from fastapi.testclient import TestClient

from src.backend.main import app
from src.backend.services.usa_service import USAService
from src.backend.services.india_service import IndiaService
from src.backend.services.archetype_service import ArchetypeService

client = TestClient(app)


# -----------------------------------------------------------------------------
# 1. USA ARCHETYPE PARITY TESTS (k=7)
# -----------------------------------------------------------------------------
@pytest.mark.parametrize("skills, expected_available, expected_code", [
    (["skill_llm", "skill_machine_learning"], True, "AI_ML"),
    (["skill_react", "skill_typescript", "skill_javascript", "skill_html", "skill_css"], True, "WEB_FRONT"),
    (["skill_kubernetes", "skill_docker", "skill_terraform", "skill_aws"], True, "DEVOPS_PLAT"),
    (["skill_aws", "skill_azure"], True, "CLOUD_ARCH"),
    (["skill_python", "skill_c++", "skill_robotics"], True, "SYS_ENG"),
    (["skill_sql", "skill_snowflake", "skill_airflow", "skill_tableau"], True, "DATA_BI"),
    (["skill_git"], True, "FOUND_TECH"),
    ([], False, "ZERO_SKILL"),
])
def test_usa_archetype_parity(skills, expected_available, expected_code):
    # Direct inference via ArchetypeService
    _, skills_arr = USAService.build_feature_vector("Software Engineer", "Senior", "New York", True, skills)
    direct_res = ArchetypeService.classify_usa_skills(skills_arr, len(skills))

    # API inference via FastAPI
    api_res = client.post("/api/usa/predict", json={
        "role_family": "Software Engineer",
        "seniority": "Senior",
        "city_clean": "New York",
        "is_remote": True,
        "selected_skills": skills,
    })
    assert api_res.status_code == 200
    api_data = api_res.json()["archetype"]

    assert direct_res["archetype_available"] == expected_available
    assert api_data["archetype_available"] == expected_available
    assert direct_res["code"] == expected_code
    assert api_data["code"] == expected_code

    if expected_available:
        assert direct_res["cluster_id"] == api_data["cluster_id"]
        assert direct_res["pca_coordinates"] == api_data["pca_coordinates"]


# -----------------------------------------------------------------------------
# 2. INDIA ARCHETYPE PARITY TESTS (k=6)
# -----------------------------------------------------------------------------
@pytest.mark.parametrize("skills, expected_available, expected_id", [
    (["skill_spark", "skill_scala", "skill_airflow"], True, "IND_ARC_01"),
    (["skill_java", "skill_spring_boot", "skill_microservices"], True, "IND_ARC_02"),
    (["skill_python", "skill_machine_learning", "skill_deep_learning"], True, "IND_ARC_03"),
    (["skill_development", "skill_react"], True, "IND_ARC_04"),
    (["skill_sap", "skill_consulting", "skill_fico", "skill_sap_fico", "skill_mm"], True, "IND_ARC_06"),
    (["skill_sql"], True, "IND_ARC_05"),
    ([], False, "IND_ARC_UNASSIGNED"),
])
def test_india_archetype_parity(skills, expected_available, expected_id):
    # Direct inference via ArchetypeService
    _, skills_arr, skill_count = IndiaService.build_feature_dataframe(
        "Software Engineer", 4.0, 2.0, "Bengaluru", "Hybrid", skills
    )
    direct_res = ArchetypeService.classify_india_skills(skills_arr, skill_count)

    # API inference via FastAPI
    api_res = client.post("/api/india/predict", json={
        "normalized_role": "Software Engineer",
        "experience_midpoint_years": 4.0,
        "experience_range_years": 2.0,
        "city_grouped": "Bengaluru",
        "work_mode": "Hybrid",
        "selected_skills": skills,
    })
    assert api_res.status_code == 200
    api_data = api_res.json()["archetype"]

    assert direct_res["archetype_available"] == expected_available
    assert api_data["archetype_available"] == expected_available
    assert direct_res["archetype_id"] == expected_id
    assert api_data["archetype_id"] == expected_id

    if expected_available:
        assert direct_res["cluster_id"] == api_data["cluster_id"]
        assert direct_res["pca_coordinates"] == api_data["pca_coordinates"]
