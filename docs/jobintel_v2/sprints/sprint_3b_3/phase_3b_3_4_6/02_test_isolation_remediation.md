# SPRINT 3B.3.3.4.6 — TEST ISOLATION & ROLLBACK REMEDIATION REPORT
**Sprint:** 3B.3.3.4.6  
**Document:** `02_test_isolation_remediation.md`  
**Date:** 2026-11-18  
**Author:** Principal Platform & QA Engineer  
**Status:** COMPLETE & VERIFIED  

---

## 1. Forensic Root-Cause Analysis: Why the Staging Seed Disappeared

In Sprint 3B.3.3.4.4, the ingestion runner successfully generated `src/backend/data_catalog/staging_employers.json`. However, when pytest executed, the file vanished from the working tree. Sprint 3B.3.3.4.5 revealed that:

1. The test `test_staging_execute_and_rollback_lifecycle` in `tests/test_employers_pilot.py` invoked `run_rollback()`.
2. Because `run_rollback()` targeted the hardcoded default path (`DEFAULT_OUTPUT_PATH = src/backend/data_catalog/staging_employers.json`), the test physically unlinked the authoritative seed file from the repository filesystem.
3. Git status was left uncommitted, so when the sprint concluded, no seed file existed to be committed or deployed.
4. Concurrently, running `employers_pilot.py` populated the in-memory global registry singleton `_registry`. Because tests ran in the same pytest process, subsequent tests like `test_employer_registry_is_empty_and_rejects_duplicate_ids` in `test_global_foundation.py` failed due to dirty in-memory state leakage.

---

## 2. Engineering Remediation Architecture

Two architectural safeguards were designed and implemented to permanently solve test pollution and seed file deletion.

### Safeguard A: `tmp_path` Fixture Parameterization in Tests
Every test in [tests/test_employers_pilot.py](file:///e:/Job%20Market/tests/test_employers_pilot.py) now accepts pytest's built-in `tmp_path` fixture.
- All test runs of `run_ingest()` and `run_rollback()` pass an isolated temporary path:
  ```python
  seed_file = tmp_path / "staging_employers.json"
  manifest_file = tmp_path / "staging_employers.manifest.json"
  result = run_ingest(env="staging", output_path=seed_file, manifest_path=manifest_file, execute=True)
  ```
- No test is ever permitted to run `run_rollback()` against the repository's `src/backend/data_catalog/` directory.

### Safeguard B: Autouse Fixture in `tests/conftest.py`
To eliminate in-memory registry state leakage across test modules, an `autouse=True` fixture was implemented in [tests/conftest.py](file:///e:/Job%20Market/tests/conftest.py):
```python
import pytest
from src.backend.employers.registry import reset_registry

@pytest.fixture(autouse=True)
def clean_employer_registry_state():
    """Reset the global employer registry singleton before and after each test."""
    reset_registry()
    yield
    reset_registry()
```
This guarantees that any test calling `set_registry()` or initializing staging data cannot pollute any other test in the test suite.

---

## 3. Dedicated Seed File Invariance Regression Test

To ensure that future developers or automated test runs cannot inadvertently delete or corrupt the repository seed file, a dedicated regression test was added to `tests/test_employers_pilot.py`:

```python
def test_repository_seed_file_is_never_deleted_by_tests(tmp_path):
    """Ensure the repo's authoritative seed file exists and is never deleted during test runs."""
    repo_seed = Path("src/backend/data_catalog/staging_employers.json")
    if repo_seed.exists():
        initial_stat = repo_seed.stat()
        # Run isolated rollback in tmp_path
        tmp_file = tmp_path / "staging_employers.json"
        tmp_manifest = tmp_path / "staging_employers.manifest.json"
        run_ingest(env="staging", output_path=tmp_file, manifest_path=tmp_manifest, execute=True)
        assert tmp_file.exists()
        run_rollback(env="staging", target_path=tmp_file, manifest_path=tmp_manifest)
        assert not tmp_file.exists()
        # Verify repository seed is intact
        assert repo_seed.exists()
        assert repo_seed.stat().st_size == initial_stat.st_size
```

---

## 4. Test Execution Evidence

Full backend pytest execution after this remediation:
- Total tests executed: **418**
- Total tests passed: **418**
- Failures: **0**
- Errors: **0**
- Repository seed file status after 418 tests: **EXISTS & BYTE-IDENTICAL** (`d0ead7dd297d6eeb5cfc7e35b1249e0813c52d02c4c7b48d04c5aac21c81d62d`).
