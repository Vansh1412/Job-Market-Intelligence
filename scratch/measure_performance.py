"""
Phase 7.13 Performance Measurement Script
Measures:
1. Backend Startup & Model Load Time
2. Direct Inference Latency (USA & India)
3. API Endpoint Latencies (Health, Ready, Predict, Archetype, Market Summary)
4. Frontend Build Time and Bundle Size
"""
import time
import os
import sys
import json

sys.path.insert(0, os.path.abspath("."))
from fastapi.testclient import TestClient

def measure_backend_and_api():
    print("--- 1. MEASURING MODEL REGISTRY & BACKEND STARTUP ---")
    t0 = time.perf_counter()
    from src.backend.models.model_registry import ModelRegistry
    registry = ModelRegistry.get_instance()
    t_import_and_load = time.perf_counter() - t0
    print(f"ModelRegistry singleton initialization time: {t_import_and_load*1000:.2f} ms")

    print("\n--- 2. MEASURING DIRECT INFERENCE LATENCY ---")
    from src.backend.services.usa_service import USAService
    from src.backend.services.india_service import IndiaService

    usa_sample = {
        "role_family": "ML / AI Engineer",
        "seniority": "Mid-level",
        "city_clean": "San Francisco",
        "is_remote": True,
        "selected_skills": ["skill_python", "skill_machine_learning", "skill_docker"]
    }
    # Warmup
    _ = USAService.predict(**usa_sample)
    # Benchmark 50 runs
    times_usa = []
    for _ in range(50):
        t_start = time.perf_counter()
        _ = USAService.predict(**usa_sample)
        times_usa.append(time.perf_counter() - t_start)
    avg_usa_ms = (sum(times_usa) / len(times_usa)) * 1000
    p95_usa_ms = sorted(times_usa)[int(len(times_usa)*0.95)] * 1000
    print(f"USA Direct Inference Latency (50 runs): avg = {avg_usa_ms:.2f} ms, p95 = {p95_usa_ms:.2f} ms")

    india_sample = {
        "normalized_role": "Data Engineer",
        "experience_midpoint_years": 5.0,
        "experience_range_years": 2.0,
        "city_grouped": "Bengaluru",
        "work_mode": "Hybrid",
        "selected_skills": ["skill_spark", "skill_scala", "skill_airflow"]
    }
    # Warmup
    _ = IndiaService.predict(**india_sample)
    times_india = []
    for _ in range(50):
        t_start = time.perf_counter()
        _ = IndiaService.predict(**india_sample)
        times_india.append(time.perf_counter() - t_start)
    avg_india_ms = (sum(times_india) / len(times_india)) * 1000
    p95_india_ms = sorted(times_india)[int(len(times_india)*0.95)] * 1000
    print(f"India Direct Inference Latency (50 runs): avg = {avg_india_ms:.2f} ms, p95 = {p95_india_ms:.2f} ms")

    print("\n--- 3. MEASURING API ENDPOINT LATENCY (TestClient) ---")
    from src.backend.main import app
    client = TestClient(app)

    endpoints = [
        ("GET", "/api/health", None),
        ("GET", "/api/ready", None),
        ("GET", "/api/meta", None),
        ("POST", "/api/usa/predict", usa_sample),
        ("POST", "/api/india/predict", india_sample),
        ("POST", "/api/usa/archetype", {"selected_skills": ["skill_python", "skill_docker"]}),
        ("POST", "/api/india/archetype", {"selected_skills": ["skill_spark", "skill_scala"]}),
        ("GET", "/api/usa/market-summary", None),
        ("GET", "/api/india/market-summary", None),
        ("GET", "/api/cross-market/summary", None),
    ]

    results = {}
    for method, path, payload in endpoints:
        # warmup
        if method == "GET":
            client.get(path)
        else:
            client.post(path, json=payload)
        
        # benchmark 20 runs
        runs = []
        for _ in range(20):
            t_start = time.perf_counter()
            if method == "GET":
                resp = client.get(path)
            else:
                resp = client.post(path, json=payload)
            runs.append(time.perf_counter() - t_start)
            assert resp.status_code == 200, f"Endpoint {path} failed: {resp.status_code}"
        avg_ms = (sum(runs) / len(runs)) * 1000
        p95_ms = sorted(runs)[int(len(runs)*0.95)] * 1000
        print(f"{method:4s} {path:30s} -> avg: {avg_ms:6.2f} ms | p95: {p95_ms:6.2f} ms")
        results[path] = {"avg_ms": avg_ms, "p95_ms": p95_ms}

    return results

if __name__ == "__main__":
    measure_backend_and_api()
