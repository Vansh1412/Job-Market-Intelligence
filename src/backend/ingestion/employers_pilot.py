from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from src.backend.employers.registry import (
    EmployerRegistry,
    get_active_registry,
    get_employers,
    reload_registry,
    reset_registry,
    set_registry,
)
from src.backend.employers.resolver import EmployerEntityResolver, parse_statutory_token
from src.backend.schemas.employer import (
    EmployerCategory,
    EmployerLocation,
    EmployerLocationType,
    EmployerProfile,
    EmployerResolutionRequest,
    EmployerSourceReference,
    EmployerVerificationStatus,
    EntityReviewStatus,
    ResolutionMatchType,
)
from src.backend.schemas.market import MarketId

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("jobintel.ingestion.employers_pilot")

# Single authoritative paths
PRIMARY_SEED_PATH = (
    Path(__file__).resolve().parent.parent
    / "data_catalog"
    / "staging_employers.json"
)

MANIFEST_PATH = (
    Path(__file__).resolve().parent.parent
    / "data_catalog"
    / "staging_employers.manifest.json"
)

# Reference timestamp for 5-pilot cohort collection & verification
PILOT_TIMESTAMP = datetime(2026, 11, 18, 0, 0, 0, tzinfo=timezone.utc)

PILOT_COHORT_SPECS: list[dict] = [
    {
        "company_id": "comp_au_atlassian",
        "company_name": "Atlassian Pty Ltd",
        "headquarters_country": "AU",
        "headquarters_country_code": "AU",
        "platform_market": "AU",
        "jurisdiction": "Australia",
        "company_category": EmployerCategory.OTHER_INTERNATIONAL,
        "industry": "Software & Cloud Collaboration Tools",
        "official_website": "https://www.atlassian.com",
        "operating_markets": (MarketId.AU, MarketId.US, MarketId.IN),
        "statutory_authority": "ASIC",
        "statutory_identifier": "53102443916",
        "headcount_value": None,
        "headcount_band": "1,000 to 4,999",
        "headcount_basis": "WGEA Size Band (1,000 to 4,999)",
        "headcount_scope": "DOMESTIC_OPERATING_BAND",
        "observation_date": "2024",
        "source_license": "CC-BY 4.0 (Australian Government)",
        "attribution_requirement": "Source: Australian Business Register / WGEA, licensed under CC BY 4.0",
        "publication_status": "APPROVED",
        "source_references": (
            EmployerSourceReference(
                source_name="Australian Business Register",
                source_organization="Australian Taxation Office",
                source_reference="https://abr.business.gov.au/ABN/View?id=53102443916",
                collected_at=PILOT_TIMESTAMP,
            ),
        ),
        "locations": (
            EmployerLocation(
                city="Sydney",
                state_or_region="New South Wales",
                country_code="AU",
                location_type=EmployerLocationType.HEADQUARTERS,
                verification_status=EmployerVerificationStatus.VERIFIED,
                verification_source=EmployerSourceReference(
                    source_name="ASIC Registered Entity Record",
                    source_organization="ASIC",
                    source_reference="https://abr.business.gov.au/ABN/View?id=53102443916",
                    collected_at=PILOT_TIMESTAMP,
                ),
                verified_at=PILOT_TIMESTAMP,
            ),
        ),
        "verification_status": EmployerVerificationStatus.VERIFIED,
        "verified_at": PILOT_TIMESTAMP,
    },
    {
        "company_id": "comp_us_microsoft",
        "company_name": "Microsoft Corporation",
        "headquarters_country": "US",
        "headquarters_country_code": "US",
        "platform_market": "US",
        "jurisdiction": "United States",
        "company_category": EmployerCategory.OTHER_INTERNATIONAL,
        "industry": "Cloud Computing, Enterprise Software & Hardware",
        "official_website": "https://www.microsoft.com",
        "operating_markets": (
            MarketId.US,
            MarketId.UK,
            MarketId.IN,
            MarketId.AU,
            MarketId.SG,
        ),
        "statutory_authority": "U.S. SEC",
        "statutory_identifier": "0000789019",
        "headcount_value": 228000,
        "headcount_band": None,
        "headcount_basis": "SEC Form 10-K Consolidated Full-Time Employees",
        "headcount_scope": "GLOBAL_CONSOLIDATED",
        "observation_date": "2024-06-30",
        "source_license": "Public Domain (17 U.S.C. 105)",
        "attribution_requirement": "Source: U.S. Securities and Exchange Commission Form 10-K",
        "publication_status": "APPROVED",
        "source_references": (
            EmployerSourceReference(
                source_name="SEC EDGAR",
                source_organization="U.S. Securities and Exchange Commission",
                source_reference="https://www.sec.gov/edgar/browse/?CIK=0000789019",
                collected_at=PILOT_TIMESTAMP,
            ),
        ),
        "locations": (
            EmployerLocation(
                city="Redmond",
                state_or_region="Washington",
                country_code="US",
                location_type=EmployerLocationType.HEADQUARTERS,
                verification_status=EmployerVerificationStatus.VERIFIED,
                verification_source=EmployerSourceReference(
                    source_name="SEC Form 10-K Filing",
                    source_organization="U.S. Securities and Exchange Commission",
                    source_reference="https://www.sec.gov/edgar/browse/?CIK=0000789019",
                    collected_at=PILOT_TIMESTAMP,
                ),
                verified_at=PILOT_TIMESTAMP,
            ),
        ),
        "verification_status": EmployerVerificationStatus.VERIFIED,
        "verified_at": PILOT_TIMESTAMP,
    },
    {
        "company_id": "comp_uk_arm",
        "company_name": "Arm Limited",
        "headquarters_country": "UK",
        "headquarters_country_code": "GB",
        "platform_market": "UK",
        "jurisdiction": "United Kingdom",
        "company_category": EmployerCategory.OTHER_INTERNATIONAL,
        "industry": "Semiconductor IP & Processor Architecture",
        "official_website": "https://www.arm.com",
        "operating_markets": (MarketId.UK, MarketId.US, MarketId.IN),
        "statutory_authority": "Companies House",
        "statutory_identifier": "02557590",
        "headcount_value": None,
        "headcount_band": "1,000 to 4,999",
        "headcount_basis": "UK Gender Pay Gap Reporting Band",
        "headcount_scope": "UK_OPERATING_BAND",
        "observation_date": "2024-04-05",
        "source_license": "Open Government Licence v3.0",
        "attribution_requirement": "Contains public sector information licensed under the Open Government Licence v3.0",
        "publication_status": "APPROVED",
        "source_references": (
            EmployerSourceReference(
                source_name="Companies House (UK)",
                source_organization="UK Department for Business and Trade",
                source_reference="https://find-and-update.company-information.service.gov.uk/company/02557590",
                collected_at=PILOT_TIMESTAMP,
            ),
        ),
        "locations": (
            EmployerLocation(
                city="Cambridge",
                state_or_region="Cambridgeshire",
                country_code="GB",
                location_type=EmployerLocationType.HEADQUARTERS,
                verification_status=EmployerVerificationStatus.VERIFIED,
                verification_source=EmployerSourceReference(
                    source_name="Companies House Certificate of Incorporation",
                    source_organization="Companies House (UK)",
                    source_reference="https://find-and-update.company-information.service.gov.uk/company/02557590",
                    collected_at=PILOT_TIMESTAMP,
                ),
                verified_at=PILOT_TIMESTAMP,
            ),
        ),
        "verification_status": EmployerVerificationStatus.VERIFIED,
        "verified_at": PILOT_TIMESTAMP,
    },
    {
        "company_id": "comp_sg_dbs",
        "company_name": "DBS Bank Ltd.",
        "headquarters_country": "SG",
        "headquarters_country_code": "SG",
        "platform_market": "SG",
        "jurisdiction": "Singapore",
        "company_category": EmployerCategory.OTHER_INTERNATIONAL,
        "industry": "Financial Services & Commercial Banking",
        "official_website": "https://www.dbs.com",
        "operating_markets": (MarketId.SG, MarketId.IN, MarketId.AU, MarketId.UK),
        "statutory_authority": "ACRA",
        "statutory_identifier": "196800306E",
        "headcount_value": 36000,
        "headcount_band": None,
        "headcount_basis": "Disclosed Operating Workforce",
        "headcount_scope": "GROUP_OPERATING_TOTAL",
        "observation_date": "2023-12-31",
        "source_license": "Singapore Open Data Licence",
        "attribution_requirement": "Source: ACRA Bizfile / DBS Annual Disclosures under Singapore Open Data Licence",
        "publication_status": "APPROVED",
        "source_references": (
            EmployerSourceReference(
                source_name="ACRA Bizfile",
                source_organization="Accounting and Corporate Regulatory Authority Singapore",
                source_reference="https://www.tis.bizfile.gov.sg/uen/196800306E",
                collected_at=PILOT_TIMESTAMP,
            ),
        ),
        "locations": (
            EmployerLocation(
                city="Singapore",
                state_or_region="Marina Bay Financial Centre",
                country_code="SG",
                location_type=EmployerLocationType.HEADQUARTERS,
                verification_status=EmployerVerificationStatus.VERIFIED,
                verification_source=EmployerSourceReference(
                    source_name="ACRA Business Register",
                    source_organization="ACRA",
                    source_reference="https://www.tis.bizfile.gov.sg/uen/196800306E",
                    collected_at=PILOT_TIMESTAMP,
                ),
                verified_at=PILOT_TIMESTAMP,
            ),
        ),
        "verification_status": EmployerVerificationStatus.VERIFIED,
        "verified_at": PILOT_TIMESTAMP,
    },
    {
        "company_id": "comp_in_infosys",
        "company_name": "Infosys Limited",
        "headquarters_country": "IN",
        "headquarters_country_code": "IN",
        "platform_market": "IN",
        "jurisdiction": "India",
        "company_category": EmployerCategory.INDIAN_HEADQUARTERED,
        "industry": "IT Services, Consulting & Business Solutions",
        "official_website": "https://www.infosys.com",
        "operating_markets": (
            MarketId.IN,
            MarketId.US,
            MarketId.UK,
            MarketId.AU,
            MarketId.SG,
        ),
        "statutory_authority": "MCA",
        "statutory_identifier": "L85110KA1981PLC013115",
        "headcount_value": 317240,
        "headcount_band": None,
        "headcount_basis": "SEBI BRSR Audited Total",
        "headcount_scope": "GLOBAL_AUDITED_TOTAL",
        "observation_date": "2024-03-31",
        "source_license": "Statutory Public Regulatory Disclosure",
        "attribution_requirement": "Source: Ministry of Corporate Affairs / SEBI BRSR Annual Regulatory Filings",
        "publication_status": "APPROVED",
        "source_references": (
            EmployerSourceReference(
                source_name="Ministry of Corporate Affairs",
                source_organization="Ministry of Corporate Affairs India",
                source_reference="https://www.mca.gov.in/mcafoportal/companyLLPMasterData.do?cin=L85110KA1981PLC013115",
                collected_at=PILOT_TIMESTAMP,
            ),
        ),
        "locations": (
            EmployerLocation(
                city="Bengaluru",
                state_or_region="Karnataka",
                country_code="IN",
                location_type=EmployerLocationType.HEADQUARTERS,
                verification_status=EmployerVerificationStatus.VERIFIED,
                verification_source=EmployerSourceReference(
                    source_name="MCA Master Data",
                    source_organization="Ministry of Corporate Affairs",
                    source_reference="https://www.mca.gov.in/mcafoportal/companyLLPMasterData.do?cin=L85110KA1981PLC013115",
                    collected_at=PILOT_TIMESTAMP,
                ),
                verified_at=PILOT_TIMESTAMP,
            ),
        ),
        "verification_status": EmployerVerificationStatus.VERIFIED,
        "verified_at": PILOT_TIMESTAMP,
    },
]


def build_candidate_profiles() -> tuple[EmployerProfile, ...]:
    """Constructs and validates the 5 canonical candidate profiles using EmployerProfile schema."""
    profiles: list[EmployerProfile] = []
    for spec in PILOT_COHORT_SPECS:
        profile = EmployerProfile(
            company_id=spec["company_id"],
            company_name=spec["company_name"],
            headquarters_country=spec["headquarters_country"],
            headquarters_country_code=spec.get("headquarters_country_code"),
            platform_market=spec.get("platform_market"),
            jurisdiction=spec.get("jurisdiction"),
            company_category=spec["company_category"],
            industry=spec.get("industry"),
            official_website=spec.get("official_website"),
            operating_markets=spec.get("operating_markets", ()),
            source_references=spec["source_references"],
            locations=spec.get("locations", ()),
            verification_status=spec["verification_status"],
            verified_at=spec["verified_at"],
            statutory_identifier=spec.get("statutory_identifier"),
            statutory_authority=spec.get("statutory_authority"),
            headcount_value=spec.get("headcount_value"),
            headcount_band=spec.get("headcount_band"),
            headcount_basis=spec.get("headcount_basis"),
            headcount_scope=spec.get("headcount_scope"),
            observation_date=spec.get("observation_date"),
            source_license=spec.get("source_license"),
            attribution_requirement=spec.get("attribution_requirement"),
            publication_status=spec.get("publication_status", "APPROVED"),
        )
        profiles.append(profile)
    return tuple(profiles)


def validate_candidate_batch(profiles: Sequence[EmployerProfile]) -> dict:
    """Performs strict pre-flight validation on candidate profiles."""
    if len(profiles) != 5:
        raise ValueError(f"Pilot cohort must contain exactly 5 candidates, got {len(profiles)}")

    ids = [p.company_id for p in profiles]
    if len(set(ids)) != len(ids):
        raise ValueError("Candidate profiles contain duplicate company_ids")

    # Verify timestamps
    for p in profiles:
        if p.verified_at is None or p.verified_at.utcoffset() is None:
            raise ValueError(f"Profile {p.company_id} missing timezone-aware verified_at")
        for ref in p.source_references:
            if ref.collected_at is None or ref.collected_at.utcoffset() is None:
                raise ValueError(f"Source ref for {p.company_id} missing timezone-aware collected_at")

    # Validate against entity resolver
    resolver = EmployerEntityResolver(registered_employers=profiles)
    resolution_audit = []
    for spec in PILOT_COHORT_SPECS:
        cid = spec["company_id"]
        cname = spec["company_name"]
        mkt = spec["headquarters_country"]
        stat_id = spec["statutory_identifier"]
        auth = spec["statutory_authority"]

        req = EmployerResolutionRequest(
            candidate_name=cname,
            market_id=mkt,
            statutory_identifier=stat_id,
            statutory_authority=auth,
        )
        res = resolver.resolve(req)
        if res.resolved_company_id != cid:
            raise ValueError(
                f"Resolver verification failed for {cid}: expected {cid}, got {res.resolved_company_id}"
            )
        if res.resolution_match_type != ResolutionMatchType.EXACT_IDENTIFIER_MATCH:
            raise ValueError(
                f"Resolver match type failed for {cid}: expected EXACT_IDENTIFIER_MATCH, got {res.resolution_match_type}"
            )
        if res.review_status != EntityReviewStatus.AUTOMATICALLY_RESOLVED:
            raise ValueError(
                f"Resolver review status failed for {cid}: expected AUTOMATICALLY_RESOLVED, got {res.review_status}"
            )

        resolution_audit.append({
            "company_id": cid,
            "statutory_id": stat_id,
            "statutory_authority": auth,
            "match_type": str(res.resolution_match_type),
            "review_status": str(res.review_status),
        })

    return {
        "status": "VALIDATED",
        "candidates_count": len(profiles),
        "candidate_ids": ids,
        "resolution_audit": resolution_audit,
    }


def serialize_profiles(profiles: Sequence[EmployerProfile]) -> bytes:
    """
    Serializes profiles deterministically to raw UTF-8 bytes with explicit UNIX LF line endings.
    This guarantees platform-independent cryptographic SHA-256 digests.
    """
    raw = [p.model_dump(mode="json") for p in profiles]
    text = json.dumps(raw, indent=2, sort_keys=True)
    # Enforce pure UNIX line feeds (\n) regardless of host OS
    text_lf = text.replace("\r\n", "\n") + "\n"
    return text_lf.encode("utf-8")


def compute_manifest_sha256(content: bytes) -> str:
    """Computes SHA-256 hash of exact serialized bytes."""
    return hashlib.sha256(content).hexdigest()


def write_seed_file_atomic(path: Path, data: bytes) -> None:
    """Writes bytes atomically via a temporary file in the same directory."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(".tmp")
    with open(temp_path, "wb") as f:
        f.write(data)
    os.replace(temp_path, path)


def build_manifest_dict(
    profiles: Sequence[EmployerProfile],
    seed_bytes: bytes,
    seed_filename: str = "staging_employers.json",
) -> dict:
    """Constructs the certified seed manifest dictionary."""
    sha256 = compute_manifest_sha256(seed_bytes)
    evidence_refs = []
    for p in profiles:
        for s in p.source_references:
            evidence_refs.append({
                "company_id": p.company_id,
                "source_name": s.source_name,
                "source_organization": s.source_organization,
                "source_reference": str(s.source_reference),
                "statutory_id": p.statutory_identifier,
                "statutory_authority": p.statutory_authority,
            })

    return {
        "environment": "staging",
        "seed_version": "1.0.0",
        "seed_file": seed_filename,
        "seed_sha256": sha256,
        "record_count": len(profiles),
        "record_ids": [p.company_id for p in profiles],
        "created_at": PILOT_TIMESTAMP.isoformat(),
        "evidence_references": evidence_refs,
    }


def run_dry_run() -> dict:
    """Executes pre-flight dry-run validation without writing to disk or mutating state."""
    profiles = build_candidate_profiles()
    val_report = validate_candidate_batch(profiles)
    serialized_bytes = serialize_profiles(profiles)
    sha256 = compute_manifest_sha256(serialized_bytes)

    return {
        "mode": "DRY_RUN",
        "status": "PASS",
        "candidates_count": len(profiles),
        "payload_sha256": sha256,
        "validation_report": val_report,
    }


def run_execute(
    seed_paths: Sequence[Path] | None = None,
    manifest_path: Path | None = None,
) -> dict:
    """
    Executes staging ingestion:
    - Validates batch against Pydantic schema and entity resolver.
    - Writes seed files atomically using binary mode with explicit LF.
    - Generates and writes companion seed manifest.
    - Updates in-memory registry for current process.
    """
    targets = list(seed_paths) if seed_paths is not None else [PRIMARY_SEED_PATH]
    target_manifest = manifest_path if manifest_path is not None else MANIFEST_PATH

    profiles = build_candidate_profiles()
    val_report = validate_candidate_batch(profiles)
    serialized_bytes = serialize_profiles(profiles)
    sha256 = compute_manifest_sha256(serialized_bytes)

    # Write seed files atomically
    for path in targets:
        write_seed_file_atomic(path, serialized_bytes)

    # Write companion manifest atomically
    manifest_dict = build_manifest_dict(profiles, serialized_bytes, seed_filename=targets[0].name)
    manifest_bytes = (json.dumps(manifest_dict, indent=2, sort_keys=True) + "\n").encode("utf-8")
    write_seed_file_atomic(target_manifest, manifest_bytes)

    # Update in-memory registry
    set_registry(EmployerRegistry(profiles))

    # Emit audit events
    audit_events = []
    now_iso = datetime.now(timezone.utc).isoformat()
    for spec in PILOT_COHORT_SPECS:
        event = {
            "timestamp": now_iso,
            "event": "EMPLOYER_STAGING_INGESTION",
            "environment": "staging",
            "company_id": spec["company_id"],
            "company_name": spec["company_name"],
            "statutory_id": spec["statutory_identifier"],
            "statutory_authority": spec["statutory_authority"],
            "jurisdiction": spec["jurisdiction"],
            "sha256": sha256,
        }
        audit_events.append(event)
        logger.info("[AUDIT EVENT] %s", json.dumps(event))

    return {
        "mode": "EXECUTE",
        "status": "SUCCESS",
        "records_written": len(profiles),
        "seed_paths": [str(p) for p in targets],
        "manifest_path": str(target_manifest),
        "payload_sha256": sha256,
        "audit_events_count": len(audit_events),
    }


def run_rollback(
    seed_paths: Sequence[Path] | None = None,
    manifest_path: Path | None = None,
) -> dict:
    """Executes staging rollback: unlinks target seed files and resets in-memory registry."""
    targets = list(seed_paths) if seed_paths is not None else [PRIMARY_SEED_PATH]
    target_manifest = manifest_path if manifest_path is not None else MANIFEST_PATH

    files_removed = 0
    for path in targets:
        if path.is_file():
            path.unlink()
            files_removed += 1

    if target_manifest.is_file():
        target_manifest.unlink()
        files_removed += 1

    reset_registry()

    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": "EMPLOYER_STAGING_ROLLBACK",
        "environment": "staging",
        "files_removed": files_removed,
        "registry_count": 0,
    }
    logger.info("[AUDIT EVENT] %s", json.dumps(event))

    return {
        "mode": "ROLLBACK",
        "status": "SUCCESS",
        "files_removed": files_removed,
        "current_registry_count": 0,
    }


def run_status(
    seed_paths: Sequence[Path] | None = None,
    manifest_path: Path | None = None,
) -> dict:
    """Inspects staging employer registry status on disk and in memory."""
    targets = list(seed_paths) if seed_paths is not None else [PRIMARY_SEED_PATH]
    target_manifest = manifest_path if manifest_path is not None else MANIFEST_PATH

    primary = targets[0]
    file_exists = primary.is_file()
    file_count = 0
    file_sha256 = None

    if file_exists:
        try:
            with open(primary, "rb") as f:
                content = f.read()
            data = json.loads(content.decode("utf-8"))
            file_count = len(data)
            file_sha256 = hashlib.sha256(content).hexdigest()
        except Exception as exc:
            logger.error("Error reading seed file %s: %s", primary, exc)

    manifest_exists = target_manifest.is_file()
    manifest_sha256 = None
    if manifest_exists:
        try:
            with open(target_manifest, "r", encoding="utf-8") as f:
                mdata = json.load(f)
            manifest_sha256 = mdata.get("seed_sha256")
        except Exception:
            pass

    reg = get_active_registry()
    in_memory_count = len(reg.list())

    return {
        "mode": "STATUS",
        "seed_file_path": str(primary),
        "seed_file_exists": file_exists,
        "seed_file_records": file_count,
        "seed_file_sha256": file_sha256,
        "manifest_path": str(target_manifest),
        "manifest_exists": manifest_exists,
        "manifest_sha256": manifest_sha256,
        "checksum_verified": bool(file_sha256 and manifest_sha256 and file_sha256 == manifest_sha256),
        "in_memory_registry_count": in_memory_count,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="JOBINTEL Staging Employer Pilot Ingestion Runner")
    parser.add_argument("--env", required=True, choices=["staging", "production"])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true", help="Validate candidates and preview hash")
    group.add_argument("--execute", action="store_true", help="Execute staging ingestion")
    group.add_argument("--status", action="store_true", help="Check status of staging registry")
    group.add_argument("--rollback", action="store_true", help="Roll back staging ingestion")

    args = parser.parse_args()

    # STRICT PRODUCTION GUARDRAIL
    if args.env == "production":
        print(
            "CRITICAL SECURITY VIOLATION: Production ingestion is strictly prohibited in Sprint 3B.3.3.4.6. "
            "Production remains FROZEN. Exiting.",
            file=sys.stderr,
        )
        return 1

    if args.dry_run:
        res = run_dry_run()
        print(json.dumps(res, indent=2))
        return 0
    elif args.execute:
        res = run_execute()
        print(json.dumps(res, indent=2))
        return 0
    elif args.status:
        res = run_status()
        print(json.dumps(res, indent=2))
        return 0
    elif args.rollback:
        res = run_rollback()
        print(json.dumps(res, indent=2))
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
