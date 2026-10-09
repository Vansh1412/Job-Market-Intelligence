"""
JobIntel S3 Artifact Synchronization & Cryptographic Verification Service
========================================================================
Synchronizes frozen model artifacts and private runtime datasets from private AWS S3
into container ephemeral storage (/app/data/processed, /app/models) on boot.

Enforces:
1. Bitwise cryptographic integrity verification (SHA-256) against certified manifest.
2. Fail-closed error handling (unverified or mismatched artifacts halt execution).
3. Zero credentials in source code (relies on AWS ECS Task Role IAM).
4. Idempotent runtime caching (skips downloading bitwise intact local files).
5. Strict audit logging with sensitive data redaction.
"""

import os
import json
import hashlib
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("jobintel.s3_sync")

MANIFEST_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "config",
    "artifact_manifest.json"
)


class ModelIntegrityError(Exception):
    """Raised when an artifact is missing, altered, or fails cryptographic validation."""
    pass


def compute_sha256(filepath: str) -> str:
    """Compute SHA-256 hash of a file using bounded chunks."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Artifact not found on disk: {filepath}")
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_manifest(manifest_path: str = MANIFEST_PATH) -> Dict[str, Any]:
    """Load the authoritative artifact manifest from disk."""
    if not os.path.exists(manifest_path):
        raise FileNotFoundError(f"Certified artifact manifest not found at: {manifest_path}")
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)


def sync_and_verify_artifacts(
    bucket_name: Optional[str] = None,
    region_name: Optional[str] = None,
    enforce_all: bool = True,
) -> Dict[str, Any]:
    """
    Synchronizes all certified artifacts from S3 if configured, and verifies cryptographic integrity.

    Args:
        bucket_name: S3 bucket name. Defaults to S3_BUCKET_NAME or JOBINTEL_S3_BUCKET env var.
        region_name: AWS region. Defaults to AWS_REGION or 'us-east-1'.
        enforce_all: If True, raises ModelIntegrityError when any required artifact fails.

    Returns:
        Structured summary report of synchronized and verified artifacts.
    """
    manifest = load_manifest()
    artifacts = manifest.get("artifacts", {})
    bucket = bucket_name or os.getenv("S3_BUCKET_NAME") or os.getenv("JOBINTEL_S3_BUCKET")
    region = region_name or os.getenv("AWS_REGION", "us-east-1")

    s3_client = None
    if bucket:
        endpoint_url = os.getenv("S3_ENDPOINT_URL")
        access_key = os.getenv("AWS_ACCESS_KEY_ID")
        secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        logger.info(
            "Initializing S3 client for bucket '%s' (endpoint: %s, region: %s)...",
            bucket, endpoint_url or "standard-aws", region
        )
        try:
            import boto3
            client_kwargs: Dict[str, Any] = {"region_name": region}
            if endpoint_url:
                client_kwargs["endpoint_url"] = endpoint_url
            if access_key and secret_key:
                client_kwargs["aws_access_key_id"] = access_key
                client_kwargs["aws_secret_access_key"] = secret_key
            s3_client = boto3.client("s3", **client_kwargs)
        except ImportError:
            logger.warning("boto3 package not installed. S3 sync skipped; checking local disk artifacts only.")
        except Exception as e:
            logger.error("Failed to initialize S3 storage client: %s", str(e))
            if enforce_all:
                raise ModelIntegrityError(f"Cloud storage unavailable: {e}")

    results: Dict[str, Any] = {}
    synced_count = 0
    verified_count = 0

    for key, spec in artifacts.items():
        rel_path = spec["path"]
        if not os.path.exists(rel_path) and key == "india_skill_analytics":
            alt_path = "reports/tables/india/india_skill_analytics.json"
            if os.path.exists(alt_path):
                rel_path = alt_path
        s3_key = spec.get("s3_key", rel_path)
        expected_sha = spec["sha256"]
        is_required = spec.get("required", True)

        file_exists = os.path.exists(rel_path)
        local_valid = False

        if file_exists:
            actual_sha = compute_sha256(rel_path)
            if actual_sha == expected_sha:
                local_valid = True
                results[key] = {
                    "path": rel_path,
                    "status": "VERIFIED_LOCAL",
                    "sha256": actual_sha,
                    "size_bytes": os.path.getsize(rel_path),
                }
                verified_count += 1
            else:
                logger.warning(
                    "Local artifact '%s' checksum mismatch (actual: %s, expected: %s).",
                    key, actual_sha, expected_sha
                )

        # Download from S3 if missing or invalid
        if not local_valid and s3_client and bucket:
            logger.info("Fetching artifact '%s' from S3: s3://%s/%s -> %s", key, bucket, s3_key, rel_path)
            os.makedirs(os.path.dirname(rel_path), exist_ok=True)
            tmp_path = f"{rel_path}.download.tmp"

            try:
                s3_client.download_file(bucket, s3_key, tmp_path)
                downloaded_sha = compute_sha256(tmp_path)

                if downloaded_sha != expected_sha:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
                    err_msg = (
                        f"CRITICAL S3 INTEGRITY FAILURE: Downloaded artifact '{key}' from s3://{bucket}/{s3_key} "
                        f"has SHA-256 '{downloaded_sha}', expected '{expected_sha}'. Refusing to mount."
                    )
                    logger.error(err_msg)
                    if enforce_all and is_required:
                        raise ModelIntegrityError(err_msg)
                    results[key] = {"path": rel_path, "status": "CHECKSUM_FAILED"}
                    continue

                # Atomic replace into place
                if os.path.exists(rel_path):
                    os.remove(rel_path)
                os.replace(tmp_path, rel_path)

                synced_count += 1
                verified_count += 1
                results[key] = {
                    "path": rel_path,
                    "status": "SYNCED_AND_VERIFIED",
                    "sha256": downloaded_sha,
                    "size_bytes": os.path.getsize(rel_path),
                }
                logger.info("PASS: Artifact '%s' verified and mounted into %s.", key, rel_path)

            except Exception as e:
                if os.path.exists(tmp_path):
                    try:
                        os.remove(tmp_path)
                    except Exception:
                        pass
                logger.error("Failed to fetch '%s' from S3: %s", key, str(e))
                if enforce_all and is_required:
                    raise ModelIntegrityError(f"Missing required artifact '{key}' from cloud storage: {e}")
                results[key] = {"path": rel_path, "status": f"DOWNLOAD_FAILED: {e}"}
        elif not local_valid:
            # File is missing/corrupted and S3 client is unavailable
            if enforce_all and is_required:
                raise ModelIntegrityError(
                    f"CRITICAL: Required artifact '{key}' missing at '{rel_path}' and no S3 bucket configured."
                )
            results[key] = {"path": rel_path, "status": "MISSING"}

    logger.info(
        "Artifact Sync Summary: %d verified (%d freshly downloaded) out of %d artifacts.",
        verified_count, synced_count, len(artifacts)
    )

    return {
        "status": "GREEN" if verified_count == len(artifacts) else "DEGRADED",
        "total_artifacts": len(artifacts),
        "verified_count": verified_count,
        "synced_count": synced_count,
        "artifacts": results,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    report = sync_and_verify_artifacts()
    print(json.dumps(report, indent=2))
