from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient

from src.backend.main import app
from src.backend.employers.resolver import EmployerEntityResolver, parse_statutory_token
from src.backend.schemas.employer import (
    EmployerCategory,
    EmployerProfile,
    EmployerResolutionRequest,
    EmployerSourceReference,
    EmployerVerificationStatus,
    EntityReviewStatus,
    ResolutionMatchType,
)
from src.backend.schemas.market import MarketId

client = TestClient(app)

NOW = datetime(2025, 1, 15, tzinfo=timezone.utc)


def make_mock_employer(
    company_id: str,
    company_name: str,
    country: str,
    source_name: str,
    source_org: str,
    source_ref: str,
    category: EmployerCategory = EmployerCategory.OTHER_INTERNATIONAL,
) -> EmployerProfile:
    market_enum = MarketId(country)
    return EmployerProfile(
        company_id=company_id,
        company_name=company_name,
        headquarters_country=country,
        company_category=EmployerCategory.INDIAN_HEADQUARTERED if country == "IN" else category,
        operating_markets=(market_enum,),
        source_references=(
            EmployerSourceReference(
                source_name=source_name,
                source_organization=source_org,
                source_reference=source_ref,
                collected_at=NOW,
            ),
        ),
        verification_status=EmployerVerificationStatus.VERIFIED,
        verified_at=NOW,
    )


# ---------------------------------------------------------------------------
# Section 5.E Required Test Suite: 27 Adversarial & Contract Tests
# ---------------------------------------------------------------------------

# 1. Exact valid SEC CIK match
def test_01_exact_valid_sec_cik_match():
    emp = make_mock_employer(
        "alphabet-inc",
        "Alphabet Inc",
        "US",
        "SEC EDGAR 10-K",
        "US SEC",
        "https://www.sec.gov/edgar/CIK0001652044",
    )
    resolver = EmployerEntityResolver([emp])
    req = EmployerResolutionRequest(
        candidate_name="Alphabet Inc.",
        market_id="US",
        statutory_identifier="CIK0001652044",
        statutory_authority="SEC",
    )
    res = resolver.resolve(req)
    assert res.resolution_match_type == ResolutionMatchType.EXACT_IDENTIFIER_MATCH
    assert res.resolved_company_id == "alphabet-inc"
    assert res.review_status == EntityReviewStatus.AUTOMATICALLY_RESOLVED
    assert len(res.candidates) == 1
    assert res.candidates[0].requires_human_approval is False


# 2. Exact valid UK Companies House CRN match
def test_02_exact_valid_uk_crn_match():
    emp = make_mock_employer(
        "deepmind-tech",
        "DeepMind Technologies Limited",
        "UK",
        "Companies House",
        "UK Companies House",
        "https://find-and-update.company-information.service.gov.uk/company/07386357",
    )
    resolver = EmployerEntityResolver([emp])
    req = EmployerResolutionRequest(
        candidate_name="DeepMind Technologies Limited",
        market_id="UK",
        statutory_identifier="07386357",
        statutory_authority="Companies House",
    )
    res = resolver.resolve(req)
    assert res.resolution_match_type == ResolutionMatchType.EXACT_IDENTIFIER_MATCH
    assert res.resolved_company_id == "deepmind-tech"
    assert res.review_status == EntityReviewStatus.AUTOMATICALLY_RESOLVED
    assert res.candidates[0].requires_human_approval is False


# 3. Exact valid Indian CIN match
def test_03_exact_valid_indian_cin_match():
    emp = make_mock_employer(
        "infosys-limited",
        "Infosys Limited",
        "IN",
        "MCA Registry",
        "MCA",
        "https://www.mca.gov.in/company/L72200KA1981PLC013115",
    )
    resolver = EmployerEntityResolver([emp])
    req = EmployerResolutionRequest(
        candidate_name="Infosys Limited",
        market_id="IN",
        statutory_identifier="L72200KA1981PLC013115",
        statutory_authority="MCA",
    )
    res = resolver.resolve(req)
    assert res.resolution_match_type == ResolutionMatchType.EXACT_IDENTIFIER_MATCH
    assert res.resolved_company_id == "infosys-limited"
    assert res.review_status == EntityReviewStatus.AUTOMATICALLY_RESOLVED
    assert res.candidates[0].requires_human_approval is False


# 4. Exact valid Singapore UEN match
def test_04_exact_valid_singapore_uen_match():
    emp = make_mock_employer(
        "grab-holdings",
        "Grab Holdings Ltd",
        "SG",
        "ACRA BizFile",
        "ACRA",
        "https://www.tis.bizfile.gov.sg/company/201812345M",
    )
    resolver = EmployerEntityResolver([emp])
    req = EmployerResolutionRequest(
        candidate_name="Grab Holdings Ltd",
        market_id="SG",
        statutory_identifier="201812345M",
        statutory_authority="ACRA",
    )
    res = resolver.resolve(req)
    assert res.resolution_match_type == ResolutionMatchType.EXACT_IDENTIFIER_MATCH
    assert res.resolved_company_id == "grab-holdings"
    assert res.review_status == EntityReviewStatus.AUTOMATICALLY_RESOLVED


# 5. Exact valid Australian ABN match
def test_05_exact_valid_australian_abn_match():
    emp = make_mock_employer(
        "atlassian-pty-ltd",
        "Atlassian Pty Ltd",
        "AU",
        "ABR Registry",
        "ASIC",
        "https://abr.business.gov.au/ABN/View?id=53102443916",
    )
    resolver = EmployerEntityResolver([emp])
    req = EmployerResolutionRequest(
        candidate_name="Atlassian Pty Ltd",
        market_id="AU",
        statutory_identifier="53102443916",
        statutory_authority="ASIC",
    )
    res = resolver.resolve(req)
    assert res.resolution_match_type == ResolutionMatchType.EXACT_IDENTIFIER_MATCH
    assert res.resolved_company_id == "atlassian-pty-ltd"
    assert res.review_status == EntityReviewStatus.AUTOMATICALLY_RESOLVED


# 6. Partial identifier rejection (0001 or SEC must NOT match CIK0001652044)
def test_06_partial_identifier_rejection():
    emp = make_mock_employer(
        "alphabet-inc",
        "Alphabet Inc",
        "US",
        "SEC EDGAR",
        "US SEC",
        "https://www.sec.gov/edgar/CIK0001652044",
    )
    resolver = EmployerEntityResolver([emp])

    # Case A: Partial number "0001"
    req_partial = EmployerResolutionRequest(
        candidate_name="Apex Corp",
        market_id="US",
        statutory_identifier="0001",
    )
    res_partial = resolver.resolve(req_partial)
    assert res_partial.resolved_company_id is None
    assert res_partial.resolution_match_type != ResolutionMatchType.EXACT_IDENTIFIER_MATCH

    # Case B: String "SEC"
    req_sec = EmployerResolutionRequest(
        candidate_name="Securities Research Corp",
        market_id="US",
        statutory_identifier="SEC",
    )
    res_sec = resolver.resolve(req_sec)
    assert res_sec.resolved_company_id is None
    assert res_sec.resolution_match_type != ResolutionMatchType.EXACT_IDENTIFIER_MATCH


# 7. Short identifier rejection (< 4 characters)
def test_07_short_identifier_rejection():
    assert parse_statutory_token("12") is None
    assert parse_statutory_token("SEC") is None
    assert parse_statutory_token("1") is None
    assert parse_statutory_token("   ") is None


# 8. Substring collision protection (identifier in unrelated blog URL must not match)
def test_08_substring_collision_protection():
    emp = make_mock_employer(
        "tech-blog-inc",
        "Tech Blog Inc",
        "UK",
        "Tech Article",
        "Hacker News",
        "https://news.ycombinator.com/item?id=07386357",
    )
    resolver = EmployerEntityResolver([emp])
    req = EmployerResolutionRequest(
        candidate_name="Acme Systems Limited",
        market_id="UK",
        statutory_identifier="07386357",
        statutory_authority="Companies House",
    )
    res = resolver.resolve(req)
    assert res.resolved_company_id is None
    assert res.resolution_match_type != ResolutionMatchType.EXACT_IDENTIFIER_MATCH


# 9. Wrong statutory authority (MCA passed with SEC CIK format)
def test_09_wrong_statutory_authority_conflict():
    token = parse_statutory_token("CIK0001652044", authority_hint="MCA")
    assert token is None

    emp = make_mock_employer(
        "alphabet-inc",
        "Alphabet Inc",
        "US",
        "SEC EDGAR",
        "US SEC",
        "https://www.sec.gov/edgar/CIK0001652044",
    )
    resolver = EmployerEntityResolver([emp])
    req = EmployerResolutionRequest(
        candidate_name="Alphabet Inc",
        market_id="US",
        statutory_identifier="CIK0001652044",
        statutory_authority="MCA",
    )
    res = resolver.resolve(req)
    # Authority conflict suppresses exact statutory resolution
    assert res.resolution_match_type != ResolutionMatchType.EXACT_IDENTIFIER_MATCH


# 10. Wrong jurisdiction (SG market passed with US SEC CIK)
def test_10_wrong_jurisdiction_conflict():
    emp = make_mock_employer(
        "alphabet-inc",
        "Alphabet Inc",
        "US",
        "SEC EDGAR",
        "US SEC",
        "https://www.sec.gov/edgar/CIK0001652044",
    )
    resolver = EmployerEntityResolver([emp])
    req = EmployerResolutionRequest(
        candidate_name="Alphabet Singapore Pte Ltd",
        market_id="SG",
        statutory_identifier="CIK0001652044",
    )
    res = resolver.resolve(req)
    assert res.resolved_company_id is None
    assert res.review_status == EntityReviewStatus.MANUAL_REVIEW_REQUIRED


# 11. Missing authority safe fallback
def test_11_missing_authority_safe_fallback():
    emp = make_mock_employer(
        "alphabet-inc",
        "Alphabet Inc",
        "US",
        "SEC EDGAR",
        "US SEC",
        "https://www.sec.gov/edgar/CIK0001652044",
    )
    resolver = EmployerEntityResolver([emp])

    # Unambiguous CIK prefix with compatible market resolves
    req_us = EmployerResolutionRequest(
        candidate_name="Alphabet Inc",
        market_id="US",
        statutory_identifier="CIK0001652044",
        statutory_authority=None,
    )
    res_us = resolver.resolve(req_us)
    assert res_us.resolution_match_type == ResolutionMatchType.EXACT_IDENTIFIER_MATCH
    assert res_us.resolved_company_id == "alphabet-inc"

    # Conflicting market does NOT resolve
    req_uk = EmployerResolutionRequest(
        candidate_name="Alphabet UK",
        market_id="UK",
        statutory_identifier="CIK0001652044",
        statutory_authority=None,
    )
    res_uk = resolver.resolve(req_uk)
    assert res_uk.resolved_company_id is None


# 12. Conflicting authority rejection (identifier claims UK CRN but references SEC EDGAR)
def test_12_conflicting_authority_rejection():
    token = parse_statutory_token(
        "https://www.sec.gov/edgar/CIK0001652044",
        authority_hint="UK Companies House",
    )
    assert token is None


# 13. Google India candidate with Google LLC CIK (Must NOT collapse to Google LLC)
def test_13_google_india_with_google_llc_cik():
    parent_emp = make_mock_employer(
        "google-llc",
        "Google LLC",
        "US",
        "SEC EDGAR",
        "US SEC",
        "https://www.sec.gov/edgar/CIK0001652044",
    )
    resolver = EmployerEntityResolver([parent_emp])
    req = EmployerResolutionRequest(
        candidate_name="Google India Private Limited",
        market_id="IN",
        statutory_identifier="CIK0001652044",
    )
    res = resolver.resolve(req)
    assert res.resolution_match_type == ResolutionMatchType.AMBIGUOUS_CANDIDATE
    assert res.resolved_company_id is None
    assert res.review_status == EntityReviewStatus.MANUAL_REVIEW_REQUIRED
    assert len(res.candidates) == 1
    assert res.candidates[0].is_subsidiary_relationship is True
    assert res.candidates[0].requires_human_approval is True


# 14. Subsidiary candidate with parent identifier
def test_14_subsidiary_candidate_with_parent_identifier():
    msft_parent = make_mock_employer(
        "microsoft-corp",
        "Microsoft Corporation",
        "US",
        "SEC EDGAR",
        "US SEC",
        "https://www.sec.gov/edgar/CIK0000789019",
    )
    resolver = EmployerEntityResolver([msft_parent])
    req = EmployerResolutionRequest(
        candidate_name="Microsoft India R&D Pvt Ltd",
        market_id="IN",
        statutory_identifier="CIK0000789019",
    )
    res = resolver.resolve(req)
    assert res.resolved_company_id is None
    assert res.review_status == EntityReviewStatus.MANUAL_REVIEW_REQUIRED
    assert res.candidates[0].is_subsidiary_relationship is True
    assert res.candidates[0].requires_human_approval is True


# 15. Parent candidate with subsidiary identifier
def test_15_parent_candidate_with_subsidiary_identifier():
    parent_emp = make_mock_employer(
        "alphabet-inc",
        "Alphabet Inc",
        "US",
        "SEC EDGAR",
        "US SEC",
        "https://www.sec.gov/edgar/CIK0001652044",
    )
    resolver = EmployerEntityResolver([parent_emp])
    # Candidate claims parent name, but passes an Indian subsidiary CIN
    req = EmployerResolutionRequest(
        candidate_name="Alphabet Inc",
        market_id="US",
        statutory_identifier="U72900KA2003PTC033028",
        statutory_authority="MCA",
    )
    res = resolver.resolve(req)
    assert res.resolved_company_id is None
    assert res.review_status == EntityReviewStatus.MANUAL_REVIEW_REQUIRED


# 16. Same brand, different legal entities across markets
def test_16_same_brand_different_legal_entities_across_markets():
    amazon_us = make_mock_employer(
        "amazon-com-inc",
        "Amazon.com Inc",
        "US",
        "SEC EDGAR",
        "US SEC",
        "https://www.sec.gov/edgar/CIK0001018724",
    )
    resolver = EmployerEntityResolver([amazon_us])
    req = EmployerResolutionRequest(
        candidate_name="Amazon UK Services Ltd",
        market_id="UK",
    )
    res = resolver.resolve(req)
    assert res.resolved_company_id is None
    assert res.review_status == EntityReviewStatus.MANUAL_REVIEW_REQUIRED
    assert res.candidates[0].is_subsidiary_relationship is True


# 17. Foreign subsidiary vs. domestic parent entity
def test_17_foreign_subsidiary_vs_domestic_parent_entity():
    apple_us = make_mock_employer(
        "apple-inc",
        "Apple Inc",
        "US",
        "SEC EDGAR",
        "US SEC",
        "https://www.sec.gov/edgar/CIK0000320193",
    )
    resolver = EmployerEntityResolver([apple_us])
    req = EmployerResolutionRequest(
        candidate_name="Apple Operations International Ltd",
        market_id="UK",
    )
    res = resolver.resolve(req)
    assert res.resolved_company_id is None
    assert res.review_status == EntityReviewStatus.MANUAL_REVIEW_REQUIRED


# 18. Conflicting legal names and identifiers (Acme Scam Corp with Alphabet CIK)
def test_18_conflicting_legal_names_and_identifiers():
    alpha = make_mock_employer(
        "alphabet-inc",
        "Alphabet Inc",
        "US",
        "SEC EDGAR",
        "US SEC",
        "https://www.sec.gov/edgar/CIK0001652044",
    )
    resolver = EmployerEntityResolver([alpha])
    req = EmployerResolutionRequest(
        candidate_name="Acme Scam Corp",
        market_id="US",
        statutory_identifier="CIK0001652044",
    )
    res = resolver.resolve(req)
    # Must NOT auto-resolve to Alphabet Inc despite matching CIK
    assert res.resolved_company_id is None
    assert res.review_status == EntityReviewStatus.MANUAL_REVIEW_REQUIRED
    assert res.resolution_match_type == ResolutionMatchType.AMBIGUOUS_CANDIDATE


# 19. Whitespace-only or missing candidate name
def test_19_whitespace_only_or_missing_candidate_name():
    emp = make_mock_employer(
        "alphabet-inc",
        "Alphabet Inc",
        "US",
        "SEC EDGAR",
        "US SEC",
        "https://www.sec.gov/edgar/CIK0001652044",
    )
    resolver = EmployerEntityResolver([emp])
    req = EmployerResolutionRequest(candidate_name="   ", market_id="US")
    res = resolver.resolve(req)
    assert res.resolution_match_type == ResolutionMatchType.NO_MATCH
    assert res.resolved_company_id is None
    assert res.review_status == EntityReviewStatus.CONFIRMED_DISTINCT


# 20. Malformed statutory identifier handling
def test_20_malformed_statutory_identifier():
    emp = make_mock_employer(
        "alphabet-inc",
        "Alphabet Inc",
        "US",
        "SEC EDGAR",
        "US SEC",
        "https://www.sec.gov/edgar/CIK0001652044",
    )
    resolver = EmployerEntityResolver([emp])
    req = EmployerResolutionRequest(
        candidate_name="Unknown Entity",
        market_id="US",
        statutory_identifier="!@#$%^&*()_+=",
    )
    res = resolver.resolve(req)
    assert res.resolution_match_type == ResolutionMatchType.NO_MATCH
    assert res.resolved_company_id is None


# 21. Duplicate registry identifier handling — Comprehensive Adversarial Suite
def test_21_duplicate_registry_identifier_handling():
    url = "https://www.sec.gov/edgar/CIK0001652044"
    e1 = make_mock_employer("emp-1", "Alpha One Corp", "US", "SEC", "US SEC", url)
    e2 = make_mock_employer("emp-2", "Alpha Two Corp", "US", "SEC", "US SEC", url)

    # Invariant: Duplicate statutory identifiers belonging to distinct legal entities
    # MUST NEVER automatically resolve to either entity, regardless of candidate or list order.

    # 1. Forward list order [e1, e2], query Alpha One
    r_forward = EmployerEntityResolver([e1, e2])
    res_a1_f = r_forward.resolve(EmployerResolutionRequest(
        candidate_name="Alpha One Corp", market_id="US", statutory_identifier="CIK0001652044"
    ))
    assert res_a1_f.resolved_company_id is None
    assert res_a1_f.review_status == EntityReviewStatus.MANUAL_REVIEW_REQUIRED
    assert res_a1_f.resolution_match_type == ResolutionMatchType.AMBIGUOUS_CANDIDATE
    assert len(res_a1_f.candidates) == 2

    # 2. Forward list order [e1, e2], query Alpha Two
    res_a2_f = r_forward.resolve(EmployerResolutionRequest(
        candidate_name="Alpha Two Corp", market_id="US", statutory_identifier="CIK0001652044"
    ))
    assert res_a2_f.resolved_company_id is None
    assert res_a2_f.review_status == EntityReviewStatus.MANUAL_REVIEW_REQUIRED
    assert res_a2_f.resolution_match_type == ResolutionMatchType.AMBIGUOUS_CANDIDATE

    # 3. Reversed list order [e2, e1], query Alpha One (must produce identical un-resolved result)
    r_reverse = EmployerEntityResolver([e2, e1])
    res_a1_r = r_reverse.resolve(EmployerResolutionRequest(
        candidate_name="Alpha One Corp", market_id="US", statutory_identifier="CIK0001652044"
    ))
    assert res_a1_r.resolved_company_id is None
    assert res_a1_r.review_status == EntityReviewStatus.MANUAL_REVIEW_REQUIRED
    assert res_a1_r.resolution_match_type == ResolutionMatchType.AMBIGUOUS_CANDIDATE

    # 4. Reversed list order [e2, e1], query Alpha Two
    res_a2_r = r_reverse.resolve(EmployerResolutionRequest(
        candidate_name="Alpha Two Corp", market_id="US", statutory_identifier="CIK0001652044"
    ))
    assert res_a2_r.resolved_company_id is None
    assert res_a2_r.review_status == EntityReviewStatus.MANUAL_REVIEW_REQUIRED
    assert res_a2_r.resolution_match_type == ResolutionMatchType.AMBIGUOUS_CANDIDATE


def test_21b_duplicate_uk_crn_collision():
    url = "https://find-and-update.company-information.service.gov.uk/company/07386357"
    e1 = make_mock_employer("uk-1", "London Deep Tech Ltd", "UK", "Companies House", "UK Companies House", url)
    e2 = make_mock_employer("uk-2", "Oxford Deep Systems Ltd", "UK", "Companies House", "UK Companies House", url)
    resolver = EmployerEntityResolver([e1, e2])
    res = resolver.resolve(EmployerResolutionRequest(
        candidate_name="London Deep Tech Ltd", market_id="UK", statutory_identifier="07386357", statutory_authority="Companies House"
    ))
    assert res.resolved_company_id is None
    assert res.review_status == EntityReviewStatus.MANUAL_REVIEW_REQUIRED
    assert res.resolution_match_type == ResolutionMatchType.AMBIGUOUS_CANDIDATE
    assert len(res.candidates) == 2


def test_21c_duplicate_indian_cin_collision():
    url = "https://www.mca.gov.in/company/L72200KA1981PLC013115"
    e1 = make_mock_employer("in-1", "Infosys Technologies Ltd", "IN", "MCA", "MCA", url)
    e2 = make_mock_employer("in-2", "Infotech Bangalore Ltd", "IN", "MCA", "MCA", url)
    resolver = EmployerEntityResolver([e1, e2])
    res = resolver.resolve(EmployerResolutionRequest(
        candidate_name="Infosys Technologies Ltd", market_id="IN", statutory_identifier="L72200KA1981PLC013115", statutory_authority="MCA"
    ))
    assert res.resolved_company_id is None
    assert res.review_status == EntityReviewStatus.MANUAL_REVIEW_REQUIRED
    assert res.resolution_match_type == ResolutionMatchType.AMBIGUOUS_CANDIDATE


def test_21d_duplicate_singapore_uen_collision():
    url = "https://www.tis.bizfile.gov.sg/company/201812345M"
    e1 = make_mock_employer("sg-1", "Grab Mobility Pte Ltd", "SG", "ACRA", "ACRA", url)
    e2 = make_mock_employer("sg-2", "Grab Financial Pte Ltd", "SG", "ACRA", "ACRA", url)
    resolver = EmployerEntityResolver([e1, e2])
    res = resolver.resolve(EmployerResolutionRequest(
        candidate_name="Grab Mobility Pte Ltd", market_id="SG", statutory_identifier="201812345M", statutory_authority="ACRA"
    ))
    assert res.resolved_company_id is None
    assert res.review_status == EntityReviewStatus.MANUAL_REVIEW_REQUIRED
    assert res.resolution_match_type == ResolutionMatchType.AMBIGUOUS_CANDIDATE


def test_21e_duplicate_australia_abn_collision():
    url = "https://abr.business.gov.au/ABN/View?id=53102443916"
    e1 = make_mock_employer("au-1", "Atlassian Operations Pty Ltd", "AU", "ASIC", "ASIC", url)
    e2 = make_mock_employer("au-2", "Atlassian Cloud Services Pty Ltd", "AU", "ASIC", "ASIC", url)
    resolver = EmployerEntityResolver([e1, e2])
    res = resolver.resolve(EmployerResolutionRequest(
        candidate_name="Atlassian Operations Pty Ltd", market_id="AU", statutory_identifier="53102443916", statutory_authority="ASIC"
    ))
    assert res.resolved_company_id is None
    assert res.review_status == EntityReviewStatus.MANUAL_REVIEW_REQUIRED
    assert res.resolution_match_type == ResolutionMatchType.AMBIGUOUS_CANDIDATE


def test_21f_randomized_registry_order_invariance():
    import random
    url = "https://www.sec.gov/edgar/CIK0001652044"
    employers = [
        make_mock_employer(f"emp-{i}", f"Company Entity {i}", "US", "SEC", "US SEC", url)
        for i in range(5)
    ]
    # Invariant: Across 10 random registry permutations, resolution is ALWAYS unresolved
    for seed in range(10):
        shuffled = list(employers)
        random.Random(seed).shuffle(shuffled)
        resolver = EmployerEntityResolver(shuffled)
        res = resolver.resolve(EmployerResolutionRequest(
            candidate_name="Company Entity 0", market_id="US", statutory_identifier="CIK0001652044"
        ))
        assert res.resolved_company_id is None
        assert res.review_status == EntityReviewStatus.MANUAL_REVIEW_REQUIRED
        assert res.resolution_match_type == ResolutionMatchType.AMBIGUOUS_CANDIDATE
        assert len(res.candidates) == 5
        for cand in res.candidates:
            assert cand.requires_human_approval is True
            assert cand.review_status == EntityReviewStatus.MANUAL_REVIEW_REQUIRED


# 22. Ambiguous fuzzy candidate routing
def test_22_ambiguous_fuzzy_candidate_routing():
    alpha = make_mock_employer(
        "alphabet-inc",
        "Alphabet Inc",
        "US",
        "SEC EDGAR",
        "US SEC",
        "https://www.sec.gov/edgar/CIK0001652044",
    )
    resolver = EmployerEntityResolver([alpha])
    req = EmployerResolutionRequest(
        candidate_name="Alphabeta Technologies",
        market_id="US",
    )
    res = resolver.resolve(req)
    assert res.resolution_match_type == ResolutionMatchType.AMBIGUOUS_CANDIDATE
    assert res.resolved_company_id is None
    assert res.review_status == EntityReviewStatus.MANUAL_REVIEW_REQUIRED


# 23. Manual-review status preservation
def test_23_manual_review_status_preservation():
    emp = make_mock_employer(
        "google-llc",
        "Google LLC",
        "US",
        "SEC EDGAR",
        "US SEC",
        "https://www.sec.gov/edgar/CIK0001652044",
    )
    resolver = EmployerEntityResolver([emp])
    req = EmployerResolutionRequest(
        candidate_name="Google India Private Limited",
        market_id="IN",
    )
    res = resolver.resolve(req)
    assert res.review_status == EntityReviewStatus.MANUAL_REVIEW_REQUIRED
    assert len(res.candidates) > 0
    for cand in res.candidates:
        assert cand.requires_human_approval is True
        assert cand.review_status == EntityReviewStatus.MANUAL_REVIEW_REQUIRED


# 24. No-match distinct entity behavior
def test_24_no_match_distinct_entity():
    emp = make_mock_employer(
        "google-llc",
        "Google LLC",
        "US",
        "SEC EDGAR",
        "US SEC",
        "https://www.sec.gov/edgar/CIK0001652044",
    )
    resolver = EmployerEntityResolver([emp])
    req = EmployerResolutionRequest(
        candidate_name="Bengaluru Artisan Bakery Ltd",
        market_id="IN",
    )
    res = resolver.resolve(req)
    assert res.resolution_match_type == ResolutionMatchType.NO_MATCH
    assert res.resolved_company_id is None
    assert res.review_status == EntityReviewStatus.CONFIRMED_DISTINCT
    assert len(res.candidates) == 0


# 25. Malformed request error handling via HTTP
def test_25_malformed_request_error_handling():
    res = client.post("/api/v1/employers/resolve", json={})
    assert res.status_code == 422


# 26. Existing pagination tests
def test_26_employer_pagination_endpoint():
    res = client.get("/api/v1/employers")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

    res_paginated = client.get("/api/v1/employers?limit=10&offset=0")
    assert res_paginated.status_code == 200
    assert isinstance(res_paginated.json(), list)

    res_invalid_high = client.get("/api/v1/employers?limit=100")
    assert res_invalid_high.status_code == 422

    res_invalid_low = client.get("/api/v1/employers?limit=0")
    assert res_invalid_low.status_code == 422

    res_invalid_offset = client.get("/api/v1/employers?offset=-1")
    assert res_invalid_offset.status_code == 422


# 27. Existing HTTP resolve endpoint test
def test_27_resolve_endpoint_via_http():
    payload = {
        "candidate_name": "Google India Private Limited",
        "market_id": "IN",
    }
    res = client.post("/api/v1/employers/resolve", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["query_name"] == "Google India Private Limited"
    assert "strict resolution policy" in data["governance_caveat"].lower()
