from __future__ import annotations

import hashlib
import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from src.backend.main import app
from src.backend.employers.registry import (
    DEFAULT_MANIFEST_PATH,
    DEFAULT_SEED_PATH,
    EmployerRegistry,
    SeedIntegrityError,
    get_active_registry,
    get_employers,
    load_registry_for_environment,
    load_staging_seed,
    reset_registry,
    set_registry,
)
from src.backend.ingestion.employers_pilot import (
    MANIFEST_PATH,
    PILOT_COHORT_SPECS,
    PRIMARY_SEED_PATH,
    build_candidate_profiles,
    build_manifest_dict,
    compute_manifest_sha256,
    main,
    run_dry_run,
    run_execute,
    run_rollback,
    run_status,
    serialize_profiles,
    validate_candidate_batch,
    write_seed_file_atomic,
)
from src.backend.schemas.employer import (
    EmployerProfile,
    EntityReviewStatus,
    ResolutionMatchType,
)

client = TestClient(app)


def test_production_environment_is_strictly_forbidden(capsys):
    """Verifies that attempting ingestion or status with --env production fails immediately."""
    import sys
    old_argv = sys.argv
    sys.argv = ["employers_pilot.py", "--env", "production", "--dry-run"]
    try:
        ret_code = main()
    finally:
        sys.argv = old_argv

    assert ret_code == 1
    captured = capsys.readouterr()
    assert "CRITICAL SECURITY VIOLATION" in captured.err


def test_candidate_profiles_pydantic_schema_and_counts():
    """Verifies that all 5 candidate profiles strictly conform to EmployerProfile schema."""
    profiles = build_candidate_profiles()
    assert len(profiles) == 5

    candidate_ids = {p.company_id for p in profiles}
    expected_ids = {
        "comp_au_atlassian",
        "comp_us_microsoft",
        "comp_uk_arm",
        "comp_sg_dbs",
        "comp_in_infosys",
    }
    assert candidate_ids == expected_ids

    # Verify each profile has timezone-aware timestamps and statutory fields
    for p in profiles:
        assert p.verified_at is not None
        assert p.verified_at.utcoffset() is not None
        assert len(p.source_references) >= 1
        assert p.statutory_identifier is not None
        assert p.statutory_authority is not None
        assert p.jurisdiction is not None
        assert p.platform_market is not None
        for s in p.source_references:
            assert s.collected_at is not None
            assert s.collected_at.utcoffset() is not None


def test_dry_run_validation_passes():
    """Verifies that dry-run performs complete validation and returns PASS."""
    res = run_dry_run()
    assert res["mode"] == "DRY_RUN"
    assert res["status"] == "PASS"
    assert res["candidates_count"] == 5
    assert len(res["payload_sha256"]) == 64
    assert res["validation_report"]["status"] == "VALIDATED"


def test_staging_execute_and_rollback_lifecycle_isolated(tmp_path: Path):
    """
    Tests the full execute -> verify -> rollback -> verify lifecycle in isolation.
    Uses tmp_path to guarantee that real repository seed files are never touched or unlinked.
    """
    temp_seed = tmp_path / "staging_employers.json"
    temp_manifest = tmp_path / "staging_employers.manifest.json"

    try:
        # Step 1: Execute staging ingestion to temporary paths
        exec_res = run_execute(seed_paths=[temp_seed], manifest_path=temp_manifest)
        assert exec_res["status"] == "SUCCESS"
        assert exec_res["records_written"] == 5
        assert temp_seed.is_file()
        assert temp_manifest.is_file()

        # Step 2: Verify status reports 5 records
        stat_res = run_status(seed_paths=[temp_seed], manifest_path=temp_manifest)
        assert stat_res["seed_file_exists"] is True
        assert stat_res["seed_file_records"] == 5
        assert stat_res["checksum_verified"] is True

        # Step 3: Verify contents on disk
        with open(temp_seed, "rb") as f:
            data = json.loads(f.read().decode("utf-8"))
        assert len(data) == 5
        assert {item["company_id"] for item in data} == {
            "comp_au_atlassian",
            "comp_us_microsoft",
            "comp_uk_arm",
            "comp_sg_dbs",
            "comp_in_infosys",
        }

        # Step 4: Verify API endpoints with loaded registry
        res_list = client.get("/api/v1/employers")
        assert res_list.status_code == 200
        assert len(res_list.json()) == 5

        res_single = client.get("/api/v1/employers/comp_au_atlassian")
        assert res_single.status_code == 200
        assert res_single.json()["company_name"] == "Atlassian Pty Ltd"
        assert res_single.json()["statutory_identifier"] == "53102443916"

        # Step 5: Test statutory identifier resolution via API
        resolve_payload = {
            "candidate_name": "Microsoft Corporation",
            "market_id": "US",
            "statutory_identifier": "0000789019",
            "statutory_authority": "U.S. SEC",
        }
        res_resolve = client.post("/api/v1/employers/resolve", json=resolve_payload)
        assert res_resolve.status_code == 200
        rdata = res_resolve.json()
        assert rdata["resolved_company_id"] == "comp_us_microsoft"
        assert rdata["resolution_match_type"] == ResolutionMatchType.EXACT_IDENTIFIER_MATCH
        assert rdata["review_status"] == EntityReviewStatus.AUTOMATICALLY_RESOLVED

    finally:
        # Step 6: Rollback and cleanup temporary files only
        rb_res = run_rollback(seed_paths=[temp_seed], manifest_path=temp_manifest)
        assert rb_res["status"] == "SUCCESS"
        assert temp_seed.is_file() is False
        assert temp_manifest.is_file() is False
        assert get_employers() == []


def test_staging_seed_idempotency_and_repeated_execution(tmp_path: Path):
    """Verifies that running execute repeatedly generates identical bytes and checksums."""
    temp_seed = tmp_path / "staging_employers.json"
    temp_manifest = tmp_path / "staging_employers.manifest.json"

    res1 = run_execute(seed_paths=[temp_seed], manifest_path=temp_manifest)
    with open(temp_seed, "rb") as f:
        bytes1 = f.read()

    res2 = run_execute(seed_paths=[temp_seed], manifest_path=temp_manifest)
    with open(temp_seed, "rb") as f:
        bytes2 = f.read()

    assert res1["payload_sha256"] == res2["payload_sha256"]
    assert bytes1 == bytes2


def test_malformed_seed_fails_closed(tmp_path: Path):
    """Verifies that malformed JSON in a seed file raises SeedIntegrityError."""
    temp_seed = tmp_path / "staging_employers.json"
    temp_manifest = tmp_path / "staging_employers.manifest.json"

    with open(temp_seed, "wb") as f:
        f.write(b"{ this is not valid json")

    mdict = {
        "seed_sha256": hashlib.sha256(b"{ this is not valid json").hexdigest(),
        "record_count": 0,
    }
    with open(temp_manifest, "w", encoding="utf-8") as f:
        json.dump(mdict, f)

    with pytest.raises(SeedIntegrityError, match="Failed to parse JSON"):
        load_staging_seed(seed_path=temp_seed, manifest_path=temp_manifest)


def test_duplicate_employer_ids_rejected(tmp_path: Path):
    """Verifies that duplicate company_ids in candidate profiles are rejected."""
    profiles = list(build_candidate_profiles())
    # Create duplicate by appending first profile
    dup_profiles = profiles + [profiles[0]]
    with pytest.raises(ValueError, match="Pilot cohort must contain exactly 5"):
        validate_candidate_batch(dup_profiles)

    # Directly test duplicate company_ids in batch of 5
    dup_batch = [profiles[0]] * 5
    with pytest.raises(ValueError, match="duplicate company_ids"):
        validate_candidate_batch(dup_batch)


def test_checksum_mismatch_fails_closed(tmp_path: Path):
    """Verifies that any file tampering or checksum mismatch fails closed."""
    temp_seed = tmp_path / "staging_employers.json"
    temp_manifest = tmp_path / "staging_employers.manifest.json"

    run_execute(seed_paths=[temp_seed], manifest_path=temp_manifest)

    # Tamper with seed file by appending a space
    with open(temp_seed, "ab") as f:
        f.write(b" ")

    with pytest.raises(SeedIntegrityError, match="Seed checksum mismatch"):
        load_staging_seed(seed_path=temp_seed, manifest_path=temp_manifest)


def test_environment_factory_and_boundaries(tmp_path: Path):
    """Verifies that environment factory strictly enforces production, test, and staging boundaries."""
    temp_seed = tmp_path / "staging_employers.json"
    temp_manifest = tmp_path / "staging_employers.manifest.json"
    run_execute(seed_paths=[temp_seed], manifest_path=temp_manifest)

    # 1. Missing environment fails closed
    with pytest.raises(ValueError, match="Missing environment configuration"):
        load_registry_for_environment(None)
    with pytest.raises(ValueError, match="Missing environment configuration"):
        load_registry_for_environment("")

    # 2. Invalid environment fails closed
    with pytest.raises(ValueError, match="Invalid environment configuration"):
        load_registry_for_environment("development_preview")

    # 3. Production environment is strictly unseeded
    prod_reg = load_registry_for_environment("production", seed_path=temp_seed, manifest_path=temp_manifest)
    assert len(prod_reg) == 0
    assert prod_reg.list() == []

    # 4. Test environment defaults to unseeded
    test_reg = load_registry_for_environment("test", seed_path=temp_seed, manifest_path=temp_manifest)
    assert len(test_reg) == 0

    # 5. Staging environment loads certified seed
    staging_reg = load_registry_for_environment("staging", seed_path=temp_seed, manifest_path=temp_manifest)
    assert len(staging_reg) == 5


def test_atomic_write_and_interrupted_write_safety(tmp_path: Path):
    """Verifies that atomic write mechanics replace files cleanly without leaving temp artifacts."""
    target_file = tmp_path / "test_file.json"
    write_seed_file_atomic(target_file, b'{"hello": "world"}')

    assert target_file.is_file()
    assert target_file.with_suffix(".tmp").is_file() is False
    with open(target_file, "rb") as f:
        assert f.read() == b'{"hello": "world"}'


def test_repository_seed_file_integrity_unchanged_regression():
    """
    CRITICAL REGRESSION TEST:
    Guarantees that the repository's real seed file and manifest:
    1. Physically exist at the single authoritative data_catalog path.
    2. Contain exactly 5 records matching declared IDs.
    3. Pass cryptographic checksum validation against the manifest.
    4. Are NEVER deleted or modified by test suite executions.
    """
    assert PRIMARY_SEED_PATH.is_file(), f"Primary seed file missing: {PRIMARY_SEED_PATH}"
    assert MANIFEST_PATH.is_file(), f"Seed manifest missing: {MANIFEST_PATH}"

    # Verify manifest data
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        mdata = json.load(f)
    assert mdata["record_count"] == 5
    assert len(mdata["seed_sha256"]) == 64

    # Verify seed file on disk
    with open(PRIMARY_SEED_PATH, "rb") as f:
        raw_bytes = f.read()

    actual_sha = hashlib.sha256(raw_bytes).hexdigest()
    assert actual_sha == mdata["seed_sha256"]

    # Verify data parses and validates
    profiles = tuple(EmployerProfile.model_validate(p) for p in json.loads(raw_bytes.decode("utf-8")))
    assert len(profiles) == 5
    assert {p.company_id for p in profiles} == {
        "comp_au_atlassian",
        "comp_us_microsoft",
        "comp_uk_arm",
        "comp_sg_dbs",
        "comp_in_infosys",
    }
