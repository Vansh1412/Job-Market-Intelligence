# SPRINT 3B.3.3.4.6 — REGISTRY INITIALIZATION & ENVIRONMENT GATING DESIGN
**Sprint:** 3B.3.3.4.6  
**Document:** `03_registry_initialization_design.md`  
**Date:** 2026-11-18  
**Author:** Principal Backend Engineer & Full-Stack Architect  
**Status:** COMPLETE & VERIFIED  

---

## 1. Critique of the `sys.modules` Anti-Pattern

In previous iterations, `src/backend/employers/registry.py` contained code checking:
```python
if "pytest" in sys.modules:
    # return empty registry
```
This was a dangerous anti-pattern for several critical reasons:
1. **Conflation of Runtime Config with Process Inspection:** Python code should behave deterministically based on explicit configuration (environment variables, dependency injection), never by inspecting loaded modules.
2. **Inability to Test Realistic Scenarios:** Under pytest, it was impossible to write unit tests that verified whether the staging seed loaded correctly on startup, because `pytest` was always in `sys.modules`.
3. **Fragility Across Test Runners:** If tests were invoked via a script or different runner (e.g., `python -m unittest`, custom integration runner), the gate would fail silently.
4. **Violation of Production Safety Invariants:** Relying on absence of `pytest` in production meant that if a production container ever imported pytest for smoke tests, production behavior would mutate.

---

## 2. Hardened Architecture: Explicit Environment Variable Gating

The anti-pattern was completely excised and replaced with explicit, environment-driven initialization in [src/backend/employers/registry.py](file:///e:/Job%20Market/src/backend/employers/registry.py):

```python
def load_staging_seed(
    seed_path: Union[str, Path] = DEFAULT_SEED_PATH,
    manifest_path: Optional[Union[str, Path]] = DEFAULT_MANIFEST_PATH,
    verify_checksum: bool = True,
) -> List[EmployerProfile]:
    """Load and cryptographically verify the staging seed catalog."""
    p = Path(seed_path)
    if not p.exists():
        raise SeedIntegrityError(f"Authoritative seed file does not exist: {p}")

    raw_bytes = p.read_bytes()
    if verify_checksum and manifest_path is not None:
        mp = Path(manifest_path)
        if mp.exists():
            with open(mp, "r", encoding="utf-8") as mf:
                manifest_data = json.load(mf)
            expected_digest = manifest_data.get("sha256")
            actual_digest = hashlib.sha256(raw_bytes).hexdigest()
            if expected_digest and actual_digest != expected_digest:
                raise SeedIntegrityError(
                    f"Seed file integrity violation: expected {expected_digest}, observed {actual_digest}"
                )

    data = json.loads(raw_bytes.decode("utf-8"))
    return [EmployerProfile(**item) for item in data]
```

### Environment Dispatch Logic:
```python
def load_registry_for_environment(env: Optional[str] = None) -> EmployerRegistry:
    target_env = (env or os.getenv("JOBINTEL_ENV", "development")).strip().lower()
    if target_env == "staging":
        if DEFAULT_SEED_PATH.exists():
            profiles = load_staging_seed(DEFAULT_SEED_PATH, DEFAULT_MANIFEST_PATH)
            return EmployerRegistry(profiles)
        logger.warning(f"JOBINTEL_ENV=staging but seed path {DEFAULT_SEED_PATH} does not exist.")
    return EmployerRegistry([])
```

---

## 3. FastAPI Dependency Injection Integration

In [src/backend/routers/v1.py](file:///e:/Job%20Market/src/backend/routers/v1.py), the router endpoints now accept the registry via FastAPI's `Depends` system:

```python
def get_current_registry() -> EmployerRegistry:
    return get_registry()

@router.get("/employers", response_model=List[EmployerProfile])
def list_employers(
    market: Optional[str] = Query(None, description="ISO market code"),
    registry: EmployerRegistry = Depends(get_current_registry),
):
    ...
```

### Benefits of this Pattern:
1. **100% Backward Compatible:** Normal calls to `get_registry()` proceed unchanged.
2. **First-Class Test Ergonomics:** Tests can cleanly override the registry per endpoint using `app.dependency_overrides[get_current_registry] = lambda: custom_registry`.
3. **No Process Pollution:** Global state does not need to be mutated to test isolated scenarios.
