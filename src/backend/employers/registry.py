from __future__ import annotations

import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Sequence

from src.backend.schemas.employer import EmployerProfile

logger = logging.getLogger("jobintel.employers.registry")


class SeedIntegrityError(Exception):
    """Raised when an employer seed file or manifest fails verification."""
    pass


# Canonical, single authoritative paths for staging seed and manifest
DEFAULT_SEED_PATH = (
    Path(__file__).resolve().parent.parent
    / "data_catalog"
    / "staging_employers.json"
)

DEFAULT_MANIFEST_PATH = (
    Path(__file__).resolve().parent.parent
    / "data_catalog"
    / "staging_employers.manifest.json"
)


class EmployerRegistry:
    def __init__(self, employers: Sequence[EmployerProfile] = ()) -> None:
        employer_map = {employer.company_id: employer for employer in employers}
        if len(employer_map) != len(employers):
            raise ValueError("company identifiers must be unique")
        self._employers = employer_map

    def list(self) -> list[EmployerProfile]:
        return list(self._employers.values())

    def get(self, company_id: str) -> EmployerProfile:
        try:
            return self._employers[company_id]
        except KeyError as exc:
            raise KeyError("employer not found") from exc

    def __len__(self) -> int:
        return len(self._employers)

    def __contains__(self, company_id: str) -> bool:
        return company_id in self._employers


def load_staging_seed(
    seed_path: Path | None = None,
    manifest_path: Path | None = None,
) -> EmployerRegistry:
    """
    Loads and validates the certified staging employer seed file.
    Enforces strict cryptographic checksum verification against the companion manifest.
    Fails closed if the file is missing, corrupt, or fails checksum validation.
    """
    target_seed = seed_path if seed_path is not None else DEFAULT_SEED_PATH
    target_manifest = manifest_path if manifest_path is not None else DEFAULT_MANIFEST_PATH

    if not target_seed.is_file():
        raise SeedIntegrityError(f"Staging employer seed file not found: {target_seed}")

    if not target_manifest.is_file():
        raise SeedIntegrityError(f"Staging employer seed manifest not found: {target_manifest}")

    # Read manifest and extract expected checksum
    try:
        with open(target_manifest, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)
    except Exception as exc:
        raise SeedIntegrityError(f"Failed to parse seed manifest {target_manifest}: {exc}") from exc

    expected_sha256 = manifest_data.get("seed_sha256")
    if not expected_sha256 or len(expected_sha256) != 64:
        raise SeedIntegrityError(f"Invalid or missing seed_sha256 in manifest: {target_manifest}")

    # Read exact binary bytes from seed file to compute raw SHA-256
    try:
        with open(target_seed, "rb") as f:
            raw_bytes = f.read()
    except Exception as exc:
        raise SeedIntegrityError(f"Failed to read seed file {target_seed}: {exc}") from exc

    actual_sha256 = hashlib.sha256(raw_bytes).hexdigest()
    if actual_sha256 != expected_sha256:
        raise SeedIntegrityError(
            f"Seed checksum mismatch for {target_seed}: expected {expected_sha256}, got {actual_sha256}"
        )

    # Parse JSON content
    try:
        data = json.loads(raw_bytes.decode("utf-8"))
    except Exception as exc:
        raise SeedIntegrityError(f"Failed to parse JSON in seed file {target_seed}: {exc}") from exc

    if not isinstance(data, list):
        raise SeedIntegrityError(f"Seed file root must be a JSON array, got {type(data).__name__}")

    # Validate against EmployerProfile Pydantic schema
    try:
        profiles = tuple(EmployerProfile.model_validate(p) for p in data)
    except Exception as exc:
        raise SeedIntegrityError(f"Pydantic schema validation failed for seed {target_seed}: {exc}") from exc

    logger.info(
        "Successfully loaded %d employer profiles from %s (SHA-256: %s)",
        len(profiles),
        target_seed.name,
        actual_sha256,
    )
    return EmployerRegistry(profiles)


def _is_staging_environment(env: Optional[str] = None) -> bool:
    """Determine whether the current process is running in the staging environment."""
    if env is not None and str(env).strip().lower() == "staging":
        return True
    system_env = os.environ.get("JOBINTEL_ENV", "").strip().lower()
    if system_env == "staging":
        return True
    # Render cloud service detection for staging backend
    render_service = os.environ.get("RENDER_SERVICE_NAME", "").strip().lower()
    render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "").strip().lower()
    render_branch = os.environ.get("RENDER_GIT_BRANCH", "").strip()
    if (
        render_service == "jobintel-backend-staging"
        or render_host == "jobintel-backend-staging.onrender.com"
        or render_branch == "staging/sprint2c3"
    ):
        return True
    return False


def load_registry_for_environment(
    env: str | None,
    seed_path: Path | None = None,
    manifest_path: Path | None = None,
) -> EmployerRegistry:
    """
    Explicit, deterministic factory for loading employer registries based on environment.
    - None / empty: Fails closed with ValueError unless staging cloud container detected.
    - 'production': Returns an unseeded registry. Production must never load staging seeds.
    - 'test': Returns an empty registry by default, allowing explicit injection.
    - 'staging': Loads the certified staging seed with checksum verification.
    - Any other value: Fails closed with ValueError.
    """
    if env is None or not str(env).strip():
        if _is_staging_environment():
            return load_staging_seed(seed_path=seed_path, manifest_path=manifest_path)
        raise ValueError("Missing environment configuration: JOBINTEL_ENV must be set")

    normalized = str(env).strip().lower()
    if normalized == "production":
        # Production remains unseeded until hydrated from an authoritative database
        return EmployerRegistry(())
    elif normalized == "test":
        # Test environment initializes empty by default
        return EmployerRegistry(())
    elif normalized == "staging" or _is_staging_environment(normalized):
        return load_staging_seed(seed_path=seed_path, manifest_path=manifest_path)
    else:
        raise ValueError(
            f"Invalid environment configuration: '{env}'. Supported: 'staging', 'production', 'test'"
        )


def _load_initial_registry() -> EmployerRegistry:
    """
    Bootstraps the module-level singleton based strictly on environment.
    Zero runtime test-runner sniffing ('sys.modules').
    """
    if _is_staging_environment():
        try:
            return load_staging_seed()
        except Exception as exc:
            logger.error("Failed to load staging seed during startup: %s", exc)
            raise
    # In production, test, or when unconfigured, default to clean empty registry
    return EmployerRegistry(())


_registry = _load_initial_registry()


def get_active_registry() -> EmployerRegistry:
    return _registry


def get_employers() -> list[EmployerProfile]:
    return _registry.list()


def get_employer(company_id: str) -> EmployerProfile:
    return _registry.get(company_id)


def set_registry(registry: EmployerRegistry) -> None:
    global _registry
    _registry = registry


def reset_registry() -> None:
    global _registry
    _registry = EmployerRegistry(())


def reload_registry(env: str | None = None) -> EmployerRegistry:
    global _registry
    target_env = env if env is not None else os.environ.get("JOBINTEL_ENV", "").strip().lower()
    if target_env == "staging":
        _registry = load_staging_seed()
    elif target_env in ("production", "test") or not target_env:
        _registry = EmployerRegistry(())
    else:
        raise ValueError(f"Invalid environment configuration: '{target_env}'")
    return _registry
