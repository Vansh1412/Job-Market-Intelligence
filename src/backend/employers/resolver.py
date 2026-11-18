from __future__ import annotations

import re
from typing import Sequence
from difflib import SequenceMatcher

from src.backend.employers.registry import get_employers
from src.backend.schemas.employer import (
    EmployerProfile,
    EmployerResolutionRequest,
    EmployerResolutionResponse,
    EntityMatchCandidate,
    EntityReviewStatus,
    ResolutionMatchType,
)

LEGAL_SUFFIXES = {
    "ltd", "limited", "pvt ltd", "private limited", "inc", "incorporated",
    "llc", "corp", "corporation", "plc", "pty ltd", "proprietary limited",
    "pte ltd", "gmbh", "sa", "srl", "bv", "nv", "co", "company"
}

SUBSIDIARY_MARKERS = {
    "india", "uk", "usa", "us", "australia", "au", "singapore", "sg",
    "ireland", "europe", "asia",
    "services", "technologies", "solutions", "software", "international",
    "holdings", "operations", "consulting", "rnd"
}

# Authoritative statutory registry mappings and supported jurisdictions
AUTHORITY_MAP = {
    "SEC": ("SEC", "US"),
    "US SEC": ("SEC", "US"),
    "EDGAR": ("SEC", "US"),
    "SEC EDGAR": ("SEC", "US"),
    "COMPANIES HOUSE": ("COMPANIES_HOUSE", "UK"),
    "UK COMPANIES HOUSE": ("COMPANIES_HOUSE", "UK"),
    "CRN": ("COMPANIES_HOUSE", "UK"),
    "MCA": ("MCA", "IN"),
    "MINISTRY OF CORPORATE AFFAIRS": ("MCA", "IN"),
    "ROC": ("MCA", "IN"),
    "ACRA": ("ACRA", "SG"),
    "ACCOUNTING AND CORPORATE REGULATORY AUTHORITY": ("ACRA", "SG"),
    "ASIC": ("ASIC", "AU"),
    "ABR": ("ASIC", "AU"),
    "AUSTRALIAN BUSINESS REGISTER": ("ASIC", "AU"),
    "AUSTRALIAN SECURITIES AND INVESTMENTS COMMISSION": ("ASIC", "AU"),
}


def normalize_entity_name(raw_name: str) -> str:
    cleaned = raw_name.lower().strip()
    cleaned = re.sub(r"[^\w\s]", " ", cleaned)
    tokens = [t for t in cleaned.split() if t]
    
    # Strip known trailing legal suffixes
    joined = " ".join(tokens)
    for suffix in sorted(LEGAL_SUFFIXES, key=len, reverse=True):
        if joined.endswith(f" {suffix}") or joined == suffix:
            joined = joined[:-len(suffix)].strip()
            break
    return joined


def extract_core_brand(normalized_name: str) -> str:
    tokens = normalized_name.split()
    non_marker_tokens = [t for t in tokens if t not in SUBSIDIARY_MARKERS]
    if non_marker_tokens:
        return non_marker_tokens[0]
    return tokens[0] if tokens else ""


def parse_statutory_token(
    raw_identifier: str,
    authority_hint: str | None = None,
    market_hint: str | None = None,
) -> tuple[str, str] | None:
    """
    Deterministically parses and normalizes a candidate or source statutory identifier.
    Returns (authority_family, normalized_exact_token) or None if invalid/malformed.
    Strictly prohibits partial substring matching.
    """
    clean = raw_identifier.strip().upper()
    if not clean or len(clean) < 4:
        return None

    # Resolve expected authority family from authority hint or market hint
    auth_family_expected = None
    if authority_hint:
        auth_entry = AUTHORITY_MAP.get(authority_hint.upper().strip())
        if auth_entry:
            auth_family_expected = auth_entry[0]
        else:
            hint_upper = authority_hint.upper().strip()
            if "SEC" in hint_upper or "EDGAR" in hint_upper:
                auth_family_expected = "SEC"
            elif "COMPANIES" in hint_upper or "CRN" in hint_upper:
                auth_family_expected = "COMPANIES_HOUSE"
            elif "MCA" in hint_upper or "ROC" in hint_upper:
                auth_family_expected = "MCA"
            elif "ACRA" in hint_upper:
                auth_family_expected = "ACRA"
            elif "ASIC" in hint_upper or "ABR" in hint_upper:
                auth_family_expected = "ASIC"

    market_norm = market_hint.upper().strip() if market_hint else None

    # Check for malformed characters (must be valid identifier or URL)
    if not re.match(r"^[A-Z0-9_\-\.\:\/\?\=\&\#\s]+$", clean):
        return None

    # 1. India MCA CIN: 21 characters (L/U + 5 digits + 2 state letters + 4 year digits + 3 entity letters + 6 digits)
    cin_match = re.search(r"([LU][0-9]{5}[A-Z]{2}[0-9]{4}[A-Z]{3}[0-9]{6})", clean)
    if cin_match:
        if auth_family_expected and auth_family_expected != "MCA":
            return None  # Conflicting authority
        return ("MCA", cin_match.group(1))

    # 2. Singapore ACRA UEN: 9 or 10 characters
    # e.g., 201812345M or T12LL1234A
    uen_match = re.search(r"(?:^|[^\w])([0-9]{8,9}[A-Z]|[TSR][0-9]{2}[A-Z]{2}[0-9]{4}[A-Z])(?:$|[^\w])", clean)
    if uen_match:
        token = uen_match.group(1)
        if auth_family_expected and auth_family_expected != "ACRA":
            return None  # Conflicting authority
        if auth_family_expected == "ACRA" or market_norm == "SG" or not clean.isdigit():
            return ("ACRA", token)

    # 3. Australia ABN (11 digits) or ACN (9 digits)
    abn_match = re.search(r"(?:ABN[=/:\s]*|^)([0-9]{11})$", clean)
    if not abn_match:
        abn_match = re.search(r"[?&]ID=([0-9]{11})", clean)
    if not abn_match and clean.startswith("ABN"):
        abn_match = re.search(r"([0-9]{11})", clean)
    if abn_match:
        if auth_family_expected and auth_family_expected != "ASIC":
            return None  # Conflicting authority
        return ("ASIC", abn_match.group(1))

    acn_match = re.search(r"(?:ACN[=/:\s]*|^)([0-9]{9})$", clean)
    if acn_match and (auth_family_expected == "ASIC" or market_norm == "AU"):
        return ("ASIC", acn_match.group(1))

    # 4. Explicit SEC CIK (US): Prefixed with CIK, or from sec.gov URL
    cik_explicit = re.search(r"(?:CIK[=/:\s]+|^CIK)0*([0-9]{4,10})$", clean)
    if not cik_explicit:
        cik_explicit = re.search(r"SEC\.GOV/.*CIK0*([0-9]{4,10})", clean)
    if not cik_explicit and clean.startswith("CIK") and re.match(r"^CIK0*([0-9]{4,10})$", clean):
        cik_explicit = re.match(r"^CIK0*([0-9]{4,10})$", clean)
    if cik_explicit:
        if auth_family_expected and auth_family_expected != "SEC":
            return None  # Conflicting authority
        digits = cik_explicit.group(1)
        return ("SEC", f"{int(digits):010d}")

    # 5. UK Companies House CRN: 8 characters (8 digits or 2 letters + 6 digits)
    crn_explicit = re.search(r"(?:CRN[=/:\s]+|^CRN)([0-9]{8}|[A-Z]{2}[0-9]{6})$", clean)
    if not crn_explicit:
        crn_explicit = re.search(r"COMPANY/([0-9]{8}|[A-Z]{2}[0-9]{6})", clean)
    if crn_explicit:
        if auth_family_expected and auth_family_expected != "COMPANIES_HOUSE":
            return None  # Conflicting authority
        return ("COMPANIES_HOUSE", crn_explicit.group(1))

    # 6. Authority-driven or Market-driven numeric resolution:
    # If authority or market indicates UK:
    if auth_family_expected == "COMPANIES_HOUSE" or market_norm == "UK":
        if re.match(r"^([0-9]{8}|[A-Z]{2}[0-9]{6})$", clean):
            return ("COMPANIES_HOUSE", clean)

    # If authority or market indicates US:
    if auth_family_expected == "SEC" or market_norm == "US":
        if re.match(r"^[0-9]{4,10}$", clean):
            return ("SEC", f"{int(clean):010d}")

    # If standalone 8-digit or 8-char UK CRN format without conflicting authority
    if re.match(r"^[A-Z]{2}[0-9]{6}$", clean) and auth_family_expected in (None, "COMPANIES_HOUSE"):
        return ("COMPANIES_HOUSE", clean)

    if re.match(r"^[0-9]{8}$", clean) and auth_family_expected in (None, "COMPANIES_HOUSE") and market_norm in (None, "UK"):
        return ("COMPANIES_HOUSE", clean)

    # Fallback for structured generic identifier if >= 6 alphanumeric characters without wildcards
    if len(clean) >= 6 and re.match(r"^[A-Z0-9_-]+$", clean) and not clean.isdigit():
        auth_family = auth_family_expected or "GENERIC"
        return (auth_family, clean)

    return None


def markets_compatible(m1: str | None, m2: str | None) -> bool:
    if not m1 or not m2:
        return True
    u1 = m1.upper().strip()
    u2 = m2.upper().strip()
    if u1 == u2:
        return True
    # UK platform market vs GB ISO-3166-1 alpha-2 equivalence
    if (u1 in ("UK", "GB")) and (u2 in ("UK", "GB")):
        return True
    return False


class EmployerEntityResolver:
    """
    Evidence-grounded, hardened corporate entity resolver for JOBINTEL 2.0.
    Enforces strict data governance:
    - Eliminates partial substring matching on statutory IDs.
    - Validates statutory authority compatibility against sovereign jurisdictions.
    - Strictly prevents collapsing subsidiaries into parents.
    - Enforces legal-name contradiction checks before granting automatic resolution.
    - Routes ambiguous cross-market or cross-tier entities to MANUAL_REVIEW_REQUIRED.
    """

    def __init__(self, registered_employers: Sequence[EmployerProfile] | None = None) -> None:
        self._employers = list(registered_employers) if registered_employers is not None else get_employers()

    def resolve(self, request: EmployerResolutionRequest) -> EmployerResolutionResponse:
        cand_name_raw = request.candidate_name.strip()
        if not cand_name_raw:
            return EmployerResolutionResponse(
                query_name=request.candidate_name,
                query_market_id=request.market_id,
                resolution_match_type=ResolutionMatchType.NO_MATCH,
                resolved_company_id=None,
                review_status=EntityReviewStatus.CONFIRMED_DISTINCT,
                candidates=(),
            )

        cand_name_norm = normalize_entity_name(cand_name_raw)
        cand_brand = extract_core_brand(cand_name_norm)
        cand_market = request.market_id.upper().strip() if request.market_id else None
        cand_auth_raw = request.statutory_authority.strip() if request.statutory_authority else None

        # Validate statutory authority compatibility if passed
        authority_jurisdiction = None
        if cand_auth_raw:
            auth_entry = AUTHORITY_MAP.get(cand_auth_raw.upper())
            if auth_entry:
                _, authority_jurisdiction = auth_entry
                # If market_id provided contradicts statutory authority jurisdiction, block statutory match
                if cand_market and cand_market != authority_jurisdiction:
                    pass  # Conflict detected; will invalidate statutory matching below

        # Parse candidate statutory identifier if provided
        cand_stat_parsed = None
        if request.statutory_identifier:
            cand_stat_parsed = parse_statutory_token(
                request.statutory_identifier,
                authority_hint=cand_auth_raw,
                market_hint=cand_market,
            )

        statutory_matches: list[tuple[EmployerProfile, float, bool]] = []
        fuzzy_candidates: list[EntityMatchCandidate] = []

        for emp in self._employers:
            emp_name_norm = normalize_entity_name(emp.company_name)
            emp_brand = extract_core_brand(emp_name_norm)
            emp_market = emp.headquarters_country.upper().strip()

            similarity = SequenceMatcher(None, cand_name_norm, emp_name_norm).ratio()
            brand_sim = SequenceMatcher(None, cand_brand, emp_brand).ratio() if (cand_brand and emp_brand) else 0.0
            has_shared_brand = bool(cand_brand and emp_brand and (cand_brand == emp_brand or brand_sim >= 0.85))
            is_cross_market = bool(cand_market and emp_market and not markets_compatible(cand_market, emp_market))

            # Check subsidiary markers in both candidate and target symmetrically
            cand_tokens = set(cand_name_norm.split())
            emp_tokens = set(emp_name_norm.split())
            cand_has_sub_marker = bool(cand_tokens.intersection(SUBSIDIARY_MARKERS))
            emp_has_sub_marker = bool(emp_tokens.intersection(SUBSIDIARY_MARKERS))
            subsidiary_indicated = is_cross_market or (cand_has_sub_marker != emp_has_sub_marker)

            # 1. Statutory Identifier Match Evaluation
            stat_match = False
            if cand_stat_parsed:
                cand_auth_family, cand_token = cand_stat_parsed

                # If statutory authority jurisdiction was specified, it must match emp_market
                if authority_jurisdiction and not markets_compatible(authority_jurisdiction, emp_market):
                    stat_match = False
                elif cand_market and not markets_compatible(cand_market, emp_market):
                    # Cross-jurisdiction identifier match requires manual review
                    stat_match = False
                else:
                    # Primary check: First-class statutory_identifier on EmployerProfile
                    if getattr(emp, "statutory_identifier", None):
                        ref_parsed = parse_statutory_token(
                            emp.statutory_identifier,
                            authority_hint=getattr(emp, "statutory_authority", None) or emp_market,
                            market_hint=emp_market,
                        )
                        if ref_parsed:
                            ref_auth_family, ref_token = ref_parsed
                            if cand_token == ref_token and (cand_auth_family == "GENERIC" or cand_auth_family == ref_auth_family):
                                stat_match = True

                    # Secondary fallback: parse statutory token from source_references URLs
                    if not stat_match:
                        for src in emp.source_references:
                            ref_parsed = parse_statutory_token(
                                str(src.source_reference),
                                authority_hint=src.source_organization,
                                market_hint=emp_market,
                            )
                            if ref_parsed:
                                ref_auth_family, ref_token = ref_parsed
                                if cand_token == ref_token and (cand_auth_family == "GENERIC" or cand_auth_family == ref_auth_family):
                                    stat_match = True
                                    break

            if stat_match:
                statutory_matches.append((emp, similarity, subsidiary_indicated))
            else:
                # 2. String Similarity / Heuristic Matching (when statutory match not found)
                if similarity >= 0.98 and not is_cross_market and not subsidiary_indicated:
                    fuzzy_candidates.append(EntityMatchCandidate(
                        target_company_id=emp.company_id,
                        target_company_name=emp.company_name,
                        target_market_id=emp_market,
                        match_type=ResolutionMatchType.STRONG_CANDIDATE_MATCH,
                        similarity_score=round(similarity, 4),
                        shared_brand_detected=has_shared_brand,
                        is_subsidiary_relationship=False,
                        evidence_summary=f"High normalized lexical similarity ({similarity:.2%}) in same jurisdiction ({emp_market}).",
                        review_status=EntityReviewStatus.MANUAL_REVIEW_REQUIRED,
                        requires_human_approval=True,
                    ))
                elif has_shared_brand or similarity >= 0.70:
                    is_sub = subsidiary_indicated
                    summary = (
                        f"Shared brand '{cand_brand}' detected. "
                        + ("Cross-market entity distinction: " if is_cross_market else "")
                        + ("Subsidiary relationship indicated. " if is_sub else "")
                        + "Automatic collapsing prohibited by governance."
                    )
                    fuzzy_candidates.append(EntityMatchCandidate(
                        target_company_id=emp.company_id,
                        target_company_name=emp.company_name,
                        target_market_id=emp_market,
                        match_type=ResolutionMatchType.AMBIGUOUS_CANDIDATE,
                        similarity_score=round(similarity, 4),
                        shared_brand_detected=has_shared_brand,
                        is_subsidiary_relationship=is_sub,
                        evidence_summary=summary,
                        review_status=EntityReviewStatus.MANUAL_REVIEW_REQUIRED,
                        requires_human_approval=True,
                    ))

        # ------------------------------------------------------------------
        # Post-Scan Decision Engine (Order-Independent & Collision-Safe)
        # ------------------------------------------------------------------

        # Deduplicate matching employers by company_id
        distinct_stat_ids = {emp.company_id for emp, _, _ in statutory_matches}

        # Case 1: Multiple distinct registered employers share the statutory token (COLLISION)
        if len(distinct_stat_ids) > 1:
            collision_candidates: list[EntityMatchCandidate] = []
            for emp, sim, sub_ind in statutory_matches:
                collision_candidates.append(EntityMatchCandidate(
                    target_company_id=emp.company_id,
                    target_company_name=emp.company_name,
                    target_market_id=emp.headquarters_country.upper().strip(),
                    match_type=ResolutionMatchType.AMBIGUOUS_CANDIDATE,
                    similarity_score=round(sim, 4),
                    shared_brand_detected=bool(
                        cand_brand and extract_core_brand(normalize_entity_name(emp.company_name)) == cand_brand
                    ),
                    is_subsidiary_relationship=sub_ind,
                    evidence_summary=(
                        f"Statutory identifier '{request.statutory_identifier}' is duplicated across "
                        f"{len(distinct_stat_ids)} distinct registered employers. Automatic resolution prohibited; manual review required."
                    ),
                    review_status=EntityReviewStatus.MANUAL_REVIEW_REQUIRED,
                    requires_human_approval=True,
                ))
            collision_candidates.sort(key=lambda c: c.similarity_score, reverse=True)
            return EmployerResolutionResponse(
                query_name=request.candidate_name,
                query_market_id=cand_market,
                resolution_match_type=ResolutionMatchType.AMBIGUOUS_CANDIDATE,
                resolved_company_id=None,
                review_status=EntityReviewStatus.MANUAL_REVIEW_REQUIRED,
                candidates=tuple(collision_candidates[:10]),
            )

        # Case 2: Exactly ONE distinct registered employer matches statutory token
        if len(distinct_stat_ids) == 1:
            emp, sim, sub_ind = statutory_matches[0]
            # Contradiction Check: If candidate name has subsidiary marker or divergent legal structure
            if sub_ind or sim < 0.60:
                summary = (
                    f"Statutory identifier matched {emp.company_name} ({emp.headquarters_country}), "
                    f"but candidate name '{cand_name_raw}' indicates a distinct legal entity, subsidiary, "
                    f"or cross-border affiliate. Automatic collapsing prohibited by JOBINTEL governance."
                )
                contradiction_cand = EntityMatchCandidate(
                    target_company_id=emp.company_id,
                    target_company_name=emp.company_name,
                    target_market_id=emp.headquarters_country.upper().strip(),
                    match_type=ResolutionMatchType.AMBIGUOUS_CANDIDATE,
                    similarity_score=round(sim, 4),  # True empirical similarity (no artificial clamping)
                    shared_brand_detected=bool(
                        cand_brand and extract_core_brand(normalize_entity_name(emp.company_name)) == cand_brand
                    ),
                    is_subsidiary_relationship=sub_ind,
                    evidence_summary=summary,
                    review_status=EntityReviewStatus.MANUAL_REVIEW_REQUIRED,
                    requires_human_approval=True,
                )
                return EmployerResolutionResponse(
                    query_name=request.candidate_name,
                    query_market_id=cand_market,
                    resolution_match_type=ResolutionMatchType.AMBIGUOUS_CANDIDATE,
                    resolved_company_id=None,
                    review_status=EntityReviewStatus.MANUAL_REVIEW_REQUIRED,
                    candidates=(contradiction_cand,),
                )
            else:
                # Authoritative Exact Statutory Match: Compatible identity, authority, and jurisdiction
                resolved_cand = EntityMatchCandidate(
                    target_company_id=emp.company_id,
                    target_company_name=emp.company_name,
                    target_market_id=emp.headquarters_country.upper().strip(),
                    match_type=ResolutionMatchType.EXACT_IDENTIFIER_MATCH,
                    similarity_score=1.0,
                    shared_brand_detected=False,
                    is_subsidiary_relationship=False,
                    evidence_summary=f"Exact statutory identifier verified with authoritative {emp.headquarters_country} corporate registry.",
                    review_status=EntityReviewStatus.AUTOMATICALLY_RESOLVED,
                    requires_human_approval=False,
                )
                return EmployerResolutionResponse(
                    query_name=request.candidate_name,
                    query_market_id=cand_market,
                    resolution_match_type=ResolutionMatchType.EXACT_IDENTIFIER_MATCH,
                    resolved_company_id=emp.company_id,
                    review_status=EntityReviewStatus.AUTOMATICALLY_RESOLVED,
                    candidates=(resolved_cand,),
                )

        # Case 3: Zero statutory matches -> fall back to string similarity / fuzzy candidates
        if not fuzzy_candidates:
            return EmployerResolutionResponse(
                query_name=request.candidate_name,
                query_market_id=cand_market,
                resolution_match_type=ResolutionMatchType.NO_MATCH,
                resolved_company_id=None,
                review_status=EntityReviewStatus.CONFIRMED_DISTINCT,
                candidates=(),
            )

        # Sort fuzzy candidates: strong matches first, then similarity descending
        fuzzy_candidates.sort(
            key=lambda c: (c.match_type == ResolutionMatchType.STRONG_CANDIDATE_MATCH, c.similarity_score),
            reverse=True,
        )
        top_cand = fuzzy_candidates[0]

        return EmployerResolutionResponse(
            query_name=request.candidate_name,
            query_market_id=cand_market,
            resolution_match_type=top_cand.match_type,
            resolved_company_id=None,  # Not auto-resolved; requires human review
            review_status=EntityReviewStatus.MANUAL_REVIEW_REQUIRED,
            candidates=tuple(fuzzy_candidates[:10]),
        )
