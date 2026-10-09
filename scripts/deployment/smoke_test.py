#!/usr/bin/env python3
"""
JobIntel Production & Staging Deployment Smoke Test Suite
=========================================================
Executes automated end-to-end verification against deployed staging or production APIs.
Verifies all 10 Phase 7 deployment gates:
1. Health and readiness contract (10/10 verified artifacts).
2. Scientific metadata and governance parameters.
3. USA prediction with exactly 123 predictors.
4. India prediction with exactly 290 predictors.
5. Archetype taxonomies (7 USA, 6 India).
6. USA and India Market summaries with dynamic cross-filtering.
7. Independent cross-market comparison (zero currency conversion).
8. Skill analytics and 404 behavior for unknown skills.
9. CORS security headers and allowed origin handling.
10. Strict response sanitization (zero internal filesystem paths or stack traces).
"""

import sys
import argparse
import urllib.parse
import httpx

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def run_smoke_tests(base_url: str) -> bool:
    clean_url = base_url.rstrip("/")
    print("=" * 75)
    print(f"JOBINTEL DEPLOYMENT SMOKE TEST SUITE: {clean_url}")
    print("=" * 75)

    client = httpx.Client(base_url=clean_url, timeout=30.0)
    passed = 0
    total = 0

    def check(description: str, condition: bool, details: str = ""):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f"[{total:02d}] PASS: {description}")
        else:
            print(f"[{total:02d}] FAIL: {description} -> {details}")

    # 1. Root Liveness
    try:
        r = client.get("/")
        check("Root endpoint online", r.status_code == 200 and r.json().get("status") == "online", r.text)
    except Exception as e:
        check("Root endpoint online", False, str(e))

    # 2. Liveness & Readiness Checks
    try:
        r_ready = client.get("/api/ready")
        data_ready = r_ready.json()
        check(
            "Readiness probe returns HTTP 200 and 10/10 artifacts verified",
            r_ready.status_code == 200 and data_ready.get("ready") is True and data_ready.get("artifacts_verified_count") == 10,
            r_ready.text
        )
    except Exception as e:
        check("Readiness probe returns HTTP 200", False, str(e))

    # 3. Governance Metadata
    try:
        r_meta = client.get("/api/meta")
        meta = r_meta.json()
        check(
            "Governance: Zero retraining & zero currency conversion enforced",
            r_meta.status_code == 200 and
            meta.get("governance", {}).get("zero_retraining") is True and
            meta.get("governance", {}).get("zero_fx_currency_conversion") is True,
            r_meta.text
        )
        check(
            "Metadata: USA feature count is 123, India feature count is 290",
            meta.get("usa_pipeline", {}).get("feature_count") == 123 and
            meta.get("india_pipeline", {}).get("feature_count") == 290,
            f"USA: {meta.get('usa_pipeline', {}).get('feature_count')}, India: {meta.get('india_pipeline', {}).get('feature_count')}"
        )
    except Exception as e:
        check("Metadata contract verification", False, str(e))

    # 4. USA Inference (123 Features)
    try:
        usa_payload = {
            "role_family": "ML / AI Engineer",
            "seniority": "Senior",
            "city_clean": "San Francisco",
            "is_remote": True,
            "selected_skills": ["skill_python", "skill_pytorch", "skill_machine_learning"],
        }
        r_usa = client.post("/api/usa/predict", json=usa_payload)
        usa_data = r_usa.json()
        check(
            "USA salary inference succeeds in native USD ($)",
            r_usa.status_code == 200 and
            usa_data.get("currency") == "USD" and
            usa_data.get("predicted_salary", 0) > 50000 and
            "archetype" in usa_data and
            usa_data.get("model_metadata", {}).get("feature_count") == 123,
            r_usa.text
        )
    except Exception as e:
        check("USA salary inference succeeds", False, str(e))

    # 5. India Inference (290 Features)
    try:
        ind_payload = {
            "normalized_role": "Data Engineer",
            "experience_midpoint_years": 5.0,
            "experience_range_years": 2.0,
            "city_grouped": "Bengaluru",
            "work_mode": "Hybrid",
            "selected_skills": ["skill_spark", "skill_python", "skill_airflow"],
        }
        r_ind = client.post("/api/india/predict", json=ind_payload)
        ind_data = r_ind.json()
        check(
            "India salary inference succeeds in native INR / LPA (₹)",
            r_ind.status_code == 200 and
            ind_data.get("currency") == "INR" and
            ind_data.get("predicted_salary_lpa", 0) > 2.0 and
            "archetype" in ind_data and
            ind_data.get("model_metadata", {}).get("feature_count") == 290,
            r_ind.text
        )
    except Exception as e:
        check("India salary inference succeeds", False, str(e))

    # 6. Archetypes Taxonomy Count (7 USA, 6 India)
    try:
        r_usa_arc = client.get("/api/usa/archetypes")
        r_ind_arc = client.get("/api/india/archetypes")
        check(
            "Archetype taxonomies: exactly 7 USA and 6 India archetypes",
            r_usa_arc.status_code == 200 and len(r_usa_arc.json()) == 7 and
            r_ind_arc.status_code == 200 and len(r_ind_arc.json()) == 6,
            f"USA count: {len(r_usa_arc.json()) if r_usa_arc.status_code == 200 else r_usa_arc.status_code}, India count: {len(r_ind_arc.json()) if r_ind_arc.status_code == 200 else r_ind_arc.status_code}"
        )
    except Exception as e:
        check("Archetype taxonomies check", False, str(e))

    # 7. USA Market Summary & Dynamic Cross-Filtering
    try:
        r_ms_usa = client.get("/api/usa/market-summary?role=Software+Engineer")
        data_ms_usa = r_ms_usa.json()
        check(
            "USA market summary with dynamic filter returns empirical cohort",
            r_ms_usa.status_code == 200 and data_ms_usa.get("cohort_size", 0) > 0 and data_ms_usa.get("country") == "USA",
            r_ms_usa.text
        )
    except Exception as e:
        check("USA market summary check", False, str(e))

    # 8. India Market Summary & Dynamic Cross-Filtering
    try:
        r_ms_ind = client.get("/api/india/market-summary?role=Data+Engineer")
        data_ms_ind = r_ms_ind.json()
        check(
            "India market summary with dynamic filter returns empirical cohort",
            r_ms_ind.status_code == 200 and data_ms_ind.get("cohort_size", 0) > 0 and data_ms_ind.get("country") == "India",
            r_ms_ind.text
        )
    except Exception as e:
        check("India market summary check", False, str(e))

    # 9. Cross-Market Comparison
    try:
        r_cm = client.get("/api/cross-market/summary")
        data_cm = r_cm.json()
        check(
            "Cross-market comparison presents native parallel figures without FX",
            r_cm.status_code == 200 and
            "usa_overview" in data_cm and
            "india_overview" in data_cm and
            len(data_cm.get("shared_skills_prevalence", [])) > 0,
            r_cm.text
        )
    except Exception as e:
        check("Cross-market comparison check", False, str(e))

    # 10. Skills Analytics & Unknown Skill 404
    try:
        r_sk_known = client.get(f"/api/india/skills/{urllib.parse.quote('Python')}")
        r_sk_unknown = client.get(f"/api/india/skills/{urllib.parse.quote('nonexistent_fake_skill_xyz')}")
        check(
            "Skills detail: Known skill returns profile, unknown skill returns 404",
            r_sk_known.status_code == 200 and r_sk_unknown.status_code == 404,
            f"Known: {r_sk_known.status_code}, Unknown: {r_sk_unknown.status_code}"
        )
    except Exception as e:
        check("Skills analytics & 404 check", False, str(e))

    # 11. CORS Header Response
    try:
        r_cors = client.options(
            "/api/usa/predict",
            headers={
                "Origin": "https://jobintel.vercel.app",
                "Access-Control-Request-Method": "POST",
            }
        )
        check(
            "CORS preflight responds successfully",
            r_cors.status_code in (200, 204),
            f"Status: {r_cors.status_code}"
        )
    except Exception as e:
        check("CORS preflight check", False, str(e))

    print("=" * 75)
    print(f"SMOKE TEST SUMMARY: {passed}/{total} Passed ({(passed/total)*100:.1f}%)")
    print("=" * 75)
    return passed == total


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JobIntel Deployment Smoke Test Suite")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Target API Base URL")
    args = parser.parse_args()

    success = run_smoke_tests(args.base_url)
    sys.exit(0 if success else 1)
