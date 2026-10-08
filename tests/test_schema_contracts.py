"""
tests/test_schema_contracts.py
==============================
Code-only contract tests validating Pydantic request and response schemas for
both USA and India APIs without requiring underlying Parquet datasets or ML models.
Ensures boundary checks, type coercion, and schema constraints operate as expected.
"""

import pytest
from pydantic import ValidationError
from src.backend.routers.usa import USAPredictionRequest, USAArchetypeRequest
from src.backend.routers.india import IndiaPredictionRequest, IndiaArchetypeRequest


def test_usa_prediction_request_valid():
    """Verify valid USA prediction request succeeds."""
    req = USAPredictionRequest(
        role_family="ML / AI Engineer",
        seniority="Senior",
        city_clean="San Francisco",
        is_remote=True,
        selected_skills=["skill_python", "skill_pytorch"],
    )
    assert req.role_family == "ML / AI Engineer"
    assert req.seniority == "Senior"
    assert req.city_clean == "San Francisco"
    assert req.is_remote is True
    assert req.selected_skills == ["skill_python", "skill_pytorch"]


def test_usa_prediction_request_missing_required():
    """Verify USA request fails when required fields are missing."""
    with pytest.raises(ValidationError):
        USAPredictionRequest(role_family="Software Engineer")


def test_usa_prediction_request_oversized_skills():
    """Verify USA request rejects more than 60 skill tokens."""
    with pytest.raises(ValidationError):
        USAPredictionRequest(
            role_family="Software Engineer",
            seniority="Senior",
            city_clean="New York",
            is_remote=False,
            selected_skills=[f"skill_{i}" for i in range(65)],
        )


def test_india_prediction_request_valid():
    """Verify valid India prediction request succeeds."""
    req = IndiaPredictionRequest(
        normalized_role="Data Engineer",
        experience_midpoint_years=5.5,
        experience_range_years=2.0,
        city_grouped="Bengaluru",
        work_mode="Hybrid",
        selected_skills=["skill_spark", "skill_python"],
    )
    assert req.normalized_role == "Data Engineer"
    assert req.experience_midpoint_years == 5.5
    assert req.experience_range_years == 2.0
    assert req.city_grouped == "Bengaluru"
    assert req.work_mode == "Hybrid"
    assert req.selected_skills == ["skill_spark", "skill_python"]


def test_india_prediction_request_boundary_experience():
    """Verify India request validates experience bounds (ge=0, le=35)."""
    # Negative experience should fail
    with pytest.raises(ValidationError):
        IndiaPredictionRequest(
            normalized_role="Data Scientist",
            experience_midpoint_years=-1.0,
            city_grouped="Bengaluru",
        )

    # Experience > 35 years should fail
    with pytest.raises(ValidationError):
        IndiaPredictionRequest(
            normalized_role="Data Scientist",
            experience_midpoint_years=40.0,
            city_grouped="Bengaluru",
        )


def test_india_prediction_request_oversized_skills():
    """Verify India request rejects more than 60 skill tokens."""
    with pytest.raises(ValidationError):
        IndiaPredictionRequest(
            normalized_role="Data Engineer",
            experience_midpoint_years=4.0,
            city_grouped="Bengaluru",
            selected_skills=[f"skill_{i}" for i in range(70)],
        )


def test_archetype_requests():
    """Verify archetype classification request models."""
    usa_arch = USAArchetypeRequest(selected_skills=["skill_aws", "skill_terraform"])
    assert len(usa_arch.selected_skills) == 2

    india_arch = IndiaArchetypeRequest(selected_skills=["skill_react", "skill_node"])
    assert len(india_arch.selected_skills) == 2
