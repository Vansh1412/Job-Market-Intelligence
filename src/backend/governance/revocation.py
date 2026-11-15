from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
import threading
from typing import Final, Iterable
from src.backend.governance.schemas import (
    RevocationConfigurationManifest,
    RevocationRecord,
    RevocationScope,
)

logger = logging.getLogger("jobintel.governance.revocation")

DEFAULT_REVOCATION_MANIFEST_PATH: Final[Path] = Path("src/backend/config/revocation_manifest.json")


class RevocationRegistry:
    """
    Thread-safe, in-memory registry of revocation records enforcing hierarchical revocation checks.
    Supports persistent loading from version-controlled configuration manifests.
    """

    def __init__(self, records: Iterable[RevocationRecord] = ()) -> None:
        self._lock = threading.RLock()
        self._records_by_id: dict[str, RevocationRecord] = {}
        self._by_source: dict[str, list[RevocationRecord]] = {}
        self._by_dataset: dict[str, list[RevocationRecord]] = {}
        self._by_release: dict[str, list[RevocationRecord]] = {}
        self._by_approval: dict[str, list[RevocationRecord]] = {}
        self._by_model: dict[str, list[RevocationRecord]] = {}
        self._release_to_dataset: dict[str, str] = {}
        self._release_to_source: dict[str, str] = {}
        self._last_invalidation: datetime = datetime.now(timezone.utc)
        self._is_healthy: bool = True
        self._status: str = "HEALTHY"
        self._load_error: str | None = None
        self._manifest_path: str | None = None
        for record in records:
            self.register(record)

    def bind_hierarchy(
        self,
        *,
        release_id: str | None = None,
        dataset_id: str | None = None,
        source_id: str | None = None,
    ) -> None:
        """Bind release-to-dataset or release-to-source relationships for hierarchical resolution."""
        with self._lock:
            if release_id:
                if dataset_id:
                    self._release_to_dataset[release_id] = dataset_id
                if source_id:
                    self._release_to_source[release_id] = source_id

    def register(self, record: RevocationRecord) -> None:
        """Register a new revocation record and update index."""
        with self._lock:
            existing = self._records_by_id.get(record.revocation_id)
            if existing is not None:
                logger.warning(
                    "Duplicate revocation ID '%s' detected. Replacing previous entry.",
                    record.revocation_id,
                )
                old_list = getattr(self, f"_by_{existing.scope.value.lower()}", {}).get(existing.target_identifier, [])
                if existing in old_list:
                    old_list.remove(existing)

            self._records_by_id[record.revocation_id] = record
            ident = record.target_identifier

            if record.scope == RevocationScope.SOURCE:
                self._by_source.setdefault(ident, []).append(record)
            elif record.scope == RevocationScope.DATASET:
                self._by_dataset.setdefault(ident, []).append(record)
            elif record.scope == RevocationScope.RELEASE:
                self._by_release.setdefault(ident, []).append(record)
            elif record.scope == RevocationScope.APPROVAL:
                self._by_approval.setdefault(ident, []).append(record)
            elif record.scope == RevocationScope.MODEL:
                self._by_model.setdefault(ident, []).append(record)

            self._last_invalidation = datetime.now(timezone.utc)

    @staticmethod
    def _is_active(record: RevocationRecord) -> bool:
        """Return True if revocation is active; False if expired."""
        if record.expires_at is not None:
            now = datetime.now(timezone.utc)
            if now >= record.expires_at:
                return False
        return True

    @staticmethod
    def _get_active_record(records: list[RevocationRecord]) -> RevocationRecord | None:
        for rec in reversed(records):
            if RevocationRegistry._is_active(rec):
                return rec
        return None

    def check_revocation(
        self,
        source_id: str,
        dataset_id: str | None = None,
        dataset_release_id: str | None = None,
        approval_id: str | None = None,
        model_id: str | None = None,
    ) -> RevocationRecord | None:
        """
        Check whether an entity is revoked.
        Hierarchical evaluation order:
        1. Source-wide revocation (highest precedence - affects all datasets, releases, approvals, models under source)
        2. Dataset-wide revocation (affects all releases of the dataset)
        3. Release-specific revocation (affects only the targeted release)
        4. Approval-specific revocation (affects only the targeted approval)
        5. Model-specific revocation (blocks inference using the targeted model)
        """
        with self._lock:
            # 1. Source Scope
            if source_records := self._by_source.get(source_id):
                if active := self._get_active_record(source_records):
                    return active

            # 2. Dataset Scope (resolve from release if not explicitly supplied)
            resolved_dataset_id = dataset_id or (
                self._release_to_dataset.get(dataset_release_id) if dataset_release_id else None
            )
            if resolved_dataset_id and (dataset_records := self._by_dataset.get(resolved_dataset_id)):
                if active := self._get_active_record(dataset_records):
                    return active

            # 3. Release Scope
            if dataset_release_id and (rel_records := self._by_release.get(dataset_release_id)):
                if active := self._get_active_record(rel_records):
                    return active

            # 4. Approval Scope
            if approval_id and (appr_records := self._by_approval.get(approval_id)):
                if active := self._get_active_record(appr_records):
                    return active

            # 5. Model Scope
            if model_id and (model_records := self._by_model.get(model_id)):
                if active := self._get_active_record(model_records):
                    return active

            return None

    def invalidate_cache(self) -> None:
        """Trigger an auditable cache invalidation event."""
        with self._lock:
            self._last_invalidation = datetime.now(timezone.utc)

    @property
    def last_invalidation_timestamp(self) -> datetime:
        with self._lock:
            return self._last_invalidation

    @property
    def is_healthy(self) -> bool:
        with self._lock:
            return self._is_healthy

    @property
    def status(self) -> str:
        with self._lock:
            return self._status

    @property
    def load_error(self) -> str | None:
        with self._lock:
            return self._load_error

    @property
    def manifest_path(self) -> str | None:
        with self._lock:
            return self._manifest_path

    def __len__(self) -> int:
        with self._lock:
            return len(self._records_by_id)

    def __bool__(self) -> bool:
        return True

    @classmethod
    def load_from_manifest_file(cls, file_path: Path | str | None = None) -> RevocationRegistry:
        """
        Load validated revocation configuration from an on-disk JSON manifest.
        Safely handles missing or malformed configuration files without crashing,
        while explicitly recording failure state so the policy engine fails closed.
        """
        path = Path(file_path) if file_path else DEFAULT_REVOCATION_MANIFEST_PATH
        if not path.exists():
            logger.warning("Revocation manifest file not found at %s. Marking registry degraded (MISSING_MANIFEST).", path)
            reg = cls()
            reg._is_healthy = False
            reg._status = "MISSING_MANIFEST"
            reg._load_error = f"Manifest not found at {path}"
            reg._manifest_path = str(path)
            return reg

        try:
            with open(path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
        except Exception as exc:
            logger.error("Failed to parse revocation manifest JSON from %s: %s. Marking registry degraded (MALFORMED_JSON).", path, exc)
            reg = cls()
            reg._is_healthy = False
            reg._status = "MALFORMED_JSON"
            reg._load_error = str(exc)
            reg._manifest_path = str(path)
            return reg

        try:
            manifest = RevocationConfigurationManifest.model_validate(raw_data)
            registry = cls(manifest.revocations)
            registry._is_healthy = True
            registry._status = "HEALTHY"
            registry._manifest_path = str(path)
            logger.info("Successfully loaded %d revocation records from %s", len(registry), path)
            return registry
        except Exception as exc:
            logger.error("Schema validation failed for revocation manifest from %s: %s. Marking registry degraded (UNSUPPORTED_SCHEMA).", path, exc)
            reg = cls()
            reg._is_healthy = False
            reg._status = "UNSUPPORTED_SCHEMA"
            reg._load_error = str(exc)
            reg._manifest_path = str(path)
            return reg
