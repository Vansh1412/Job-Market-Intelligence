"""
Input Validation & Error Handling Automated Test Suite (Phase 7.7 & 7.8)
========================================================================
Validates that invalid, boundary, or malformed inputs to USA and India
prediction endpoints return controlled HTTP 422/400 errors or handle
graceful fallbacks without exposing internal stack traces.
"""

import pytest
from fastapi.testclient import TestClient
from src.backend.main import app

client = TestClient(app)


# -----------------------------------------------------------------------------
# 1. READINESS & HEALTH PROBES (Phase 7.8)
# -----------------------------------------------------------------------------
def test_readiness_probe_success():
    res = client.get("/api/ready")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ready"
    assert data["ready"] is True
    assert data["artifacts_verified_count"] == 10
    assert "USA" in data["markets"]
    assert "India" in data["markets"]


def test_health_probe_success():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "version" in data


# -----------------------------------------------------------------------------
# 2. USA INPUT VALIDATION TESTS (Phase 7.7)
# -----------------------------------------------------------------------------
def test_usa_missing_required_fields():
    # Missing role_family, seniority, city_clean
    res = client.post("/api/usa/predict", json={"is_remote": True})
    assert res.status_code == 422
    err_detail = res.json()["detail"]
    assert any("role_family" in str(e) for e in err_detail)


def test_usa_wrong_types():
    # is_remote passed as string that cannot be coerced to bool
    res = client.post("/api/usa/predict", json={
        "role_family": "Software Engineer",
        "seniority": "Senior",
        "city_clean": "San Francisco",
        "is_remote": "not_a_boolean_value",
        "selected_skills": []
    })
    assert res.status_code == 422


def test_usa_duplicate_skills_graceful_handling():
    # Duplicate skills should not crash or distort counts
    res = client.post("/api/usa/predict", json={
        "role_family": "Software Engineer",
        "seniority": "Senior",
        "city_clean": "San Francisco",
        "is_remote": True,
        "selected_skills": ["skill_python", "skill_python", "skill_python", "skill_aws", "skill_aws"]
    })
    assert res.status_code == 200
    data = res.json()
    assert data["predicted_salary"] > 50000.0
    # Should only count distinct skills
    assert data["num_skills"] <= 5


def test_usa_unknown_skills_graceful_handling():
    # Skills not in the 82 taxonomy should simply be ignored without 500
    res = client.post("/api/usa/predict", json={
        "role_family": "Software Engineer",
        "seniority": "Senior",
        "city_clean": "San Francisco",
        "is_remote": True,
        "selected_skills": ["skill_completely_made_up_123", "skill_nonexistent"]
    })
    assert res.status_code == 200
    data = res.json()
    assert data["archetype"]["archetype_available"] is False


def test_usa_unknown_role_fallback():
    # Unknown role should fall back to 'Other Tech' without crashing
    res = client.post("/api/usa/predict", json={
        "role_family": "Acrobatic Clown Engineer",
        "seniority": "Senior",
        "city_clean": "San Francisco",
        "is_remote": True,
        "selected_skills": ["skill_python"]
    })
    assert res.status_code == 200
    data = res.json()
    assert data["predicted_salary"] > 50000.0


# -----------------------------------------------------------------------------
# 3. INDIA INPUT VALIDATION TESTS (Phase 7.7)
# -----------------------------------------------------------------------------
def test_india_missing_required_fields():
    res = client.post("/api/india/predict", json={"work_mode": "Hybrid"})
    assert res.status_code == 422


def test_india_negative_experience_validation():
    # Negative experience should fail validation
    res = client.post("/api/india/predict", json={
        "normalized_role": "Data Engineer",
        "experience_midpoint_years": -5.0,
        "experience_range_years": 2.0,
        "city_grouped": "Bengaluru",
        "work_mode": "Hybrid",
        "selected_skills": ["skill_spark"]
    })
    assert res.status_code == 422


def test_india_excessive_experience_validation():
    # Experience > 35 years should fail validation
    res = client.post("/api/india/predict", json={
        "normalized_role": "Data Engineer",
        "experience_midpoint_years": 80.0,
        "experience_range_years": 2.0,
        "city_grouped": "Bengaluru",
        "work_mode": "Hybrid",
        "selected_skills": ["skill_spark"]
    })
    assert res.status_code == 422


def test_india_duplicate_skills_graceful_handling():
    res = client.post("/api/india/predict", json={
        "normalized_role": "Data Engineer",
        "experience_midpoint_years": 5.0,
        "experience_range_years": 2.0,
        "city_grouped": "Bengaluru",
        "work_mode": "Hybrid",
        "selected_skills": ["skill_spark", "skill_spark", "skill_spark"]
    })
    assert res.status_code == 200
    data = res.json()
    assert data["predicted_salary_lpa"] > 2.0


def test_india_unsupported_role_fallback():
    # Unknown role falls back to 'Other Technology'
    res = client.post("/api/india/predict", json={
        "normalized_role": "Underwater Welder",
        "experience_midpoint_years": 4.0,
        "experience_range_years": 2.0,
        "city_grouped": "Bengaluru",
        "work_mode": "Hybrid",
        "selected_skills": ["skill_spark"]
    })
    assert res.status_code == 200
    data = res.json()
    assert data["predicted_salary_lpa"] > 2.0


def test_india_unsupported_city_fallback():
    # Unknown city falls back to 'Other'
    res = client.post("/api/india/predict", json={
        "normalized_role": "Data Engineer",
        "experience_midpoint_years": 4.0,
        "experience_range_years": 2.0,
        "city_grouped": "Atlantis Metro",
        "work_mode": "Hybrid",
        "selected_skills": ["skill_spark"]
    })
    assert res.status_code == 200
    data = res.json()
    assert data["predicted_salary_lpa"] > 2.0


def test_usa_oversized_skills_rejected():
    """Verify that requests with excessive skills list (>60 items) are rejected with HTTP 422."""
    res = client.post("/api/usa/predict", json={
        "role_family": "Software Engineer",
        "seniority": "Senior",
        "city_clean": "San Francisco",
        "is_remote": True,
        "selected_skills": [f"skill_{i}" for i in range(100)]
    })
    assert res.status_code == 422, f"Expected 422 for oversized skills list, got {res.status_code}"


def test_india_oversized_skills_rejected():
    """Verify that India requests with excessive skills list (>60 items) are rejected with HTTP 422."""
    res = client.post("/api/india/predict", json={
        "normalized_role": "Data Engineer",
        "experience_midpoint_years": 4.0,
        "experience_range_years": 2.0,
        "city_grouped": "Bengaluru",
        "work_mode": "Hybrid",
        "selected_skills": [f"skill_{i}" for i in range(100)]
    })
    assert res.status_code == 422, f"Expected 422 for oversized skills list, got {res.status_code}"


def test_cors_preflight_credentials_policy():
    """Verify CORS preflight headers enforce standard credentials policy on localhost."""
    res = client.options("/api/health", headers={
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "GET"
    })
    assert res.status_code == 200
    assert "access-control-allow-origin" in res.headers
    assert res.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert res.headers.get("access-control-allow-credentials") == "true"


def test_cors_allowed_vercel_origin_header():
    """Verify exact production Vercel origin receives correct Access-Control-Allow-Origin header."""
    vercel_origin = "https://job-market-intelligence-dusky.vercel.app"
    for endpoint in ["/health", "/meta", "/india/options", "/api/india/options"]:
        res = client.get(endpoint, headers={"Origin": vercel_origin})
        assert res.status_code == 200, f"Expected 200 on {endpoint}, got {res.status_code}"
        assert res.headers.get("access-control-allow-origin") == vercel_origin, (
            f"Missing or incorrect ACAO header on {endpoint}: {res.headers.get('access-control-allow-origin')}"
        )
        assert res.headers.get("access-control-allow-credentials") == "true"


def test_cors_preflight_get_india_options_succeeds():
    """Verify GET /india/options and /api/india/options CORS preflight succeeds for Vercel origin."""
    vercel_origin = "https://job-market-intelligence-dusky.vercel.app"
    for path in ["/india/options", "/api/india/options"]:
        res = client.options(path, headers={
            "Origin": vercel_origin,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "content-type"
        })
        assert res.status_code == 200, f"Preflight OPTIONS failed on {path} with status {res.status_code}"
        assert res.headers.get("access-control-allow-origin") == vercel_origin
        assert res.headers.get("access-control-allow-credentials") == "true"
        allow_methods = res.headers.get("access-control-allow-methods", "")
        assert "GET" in allow_methods or "*" in allow_methods


def test_cors_preflight_post_india_predict_succeeds():
    """Verify POST /india/predict and /api/india/predict CORS preflight succeeds for Vercel origin."""
    vercel_origin = "https://job-market-intelligence-dusky.vercel.app"
    for path in ["/india/predict", "/api/india/predict"]:
        res = client.options(path, headers={
            "Origin": vercel_origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type"
        })
        assert res.status_code == 200, f"Preflight OPTIONS failed on {path} with status {res.status_code}"
        assert res.headers.get("access-control-allow-origin") == vercel_origin
        assert res.headers.get("access-control-allow-credentials") == "true"
        allow_methods = res.headers.get("access-control-allow-methods", "")
        assert "POST" in allow_methods or "*" in allow_methods


def test_cors_unapproved_origin_rejected():
    """Verify an unapproved origin is strictly rejected without CORS headers."""
    unapproved_origin = "https://malicious-unapproved-site.com"
    # Preflight rejected with 400 Disallowed CORS origin
    res_preflight = client.options("/india/options", headers={
        "Origin": unapproved_origin,
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "content-type"
    })
    assert res_preflight.status_code == 400
    assert "access-control-allow-origin" not in res_preflight.headers

    # Simple request does not receive CORS allow header
    res_get = client.get("/india/options", headers={"Origin": unapproved_origin})
    assert res_get.status_code == 200
    assert "access-control-allow-origin" not in res_get.headers


def test_cors_existing_localhost_origins_continue_passing():
    """Verify existing localhost and canonical origins continue passing CORS preflights."""
    allowed_test_origins = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "https://job-market-intelligence.vercel.app",
        "https://jobintel.vercel.app",
    ]
    for origin in allowed_test_origins:
        res = client.options("/india/options", headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET"
        })
        assert res.status_code == 200, f"Expected 200 for allowed origin {origin}, got {res.status_code}"
        assert res.headers.get("access-control-allow-origin") == origin
        assert res.headers.get("access-control-allow-credentials") == "true"


def test_cors_error_responses_preserve_cors_headers():
    """Verify CORS headers are preserved even on 422 and 404 error responses for allowed origins."""
    vercel_origin = "https://job-market-intelligence-dusky.vercel.app"

    # 422 Unprocessable Entity
    res_422 = client.post("/india/predict", json={}, headers={"Origin": vercel_origin})
    assert res_422.status_code == 422
    assert res_422.headers.get("access-control-allow-origin") == vercel_origin

    # 404 Not Found
    res_404 = client.get("/nonexistent-endpoint-xyz", headers={"Origin": vercel_origin})
    assert res_404.status_code == 404
    assert res_404.headers.get("access-control-allow-origin") == vercel_origin


def test_cors_no_wildcard_origin():
    """Verify wildcard '*' is never used as an allowed origin."""
    from src.backend.main import allowed_origins
    assert "*" not in allowed_origins, "Wildcard '*' origin is strictly forbidden in production!"

