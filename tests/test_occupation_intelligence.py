from __future__ import annotations

from decimal import Decimal
import pytest
from fastapi.testclient import TestClient

from src.backend.main import app
from src.backend.schemas.occupation import (
    CanonicalOccupation,
    ClassificationId,
    ClassificationSystem,
    MappingMethodology,
    NationalOccupation,
    OccupationMapping,
    RelationshipType,
    ReviewStatus,
    TargetType,
)
from src.backend.services.occupation_service import (
    CanonicalOccupationNotFoundError,
    ClassificationNotFoundError,
    OccupationNotFoundError,
    get_occupation_service,
)

client = TestClient(app)


# =============================================================================
# 1. SCHEMA & CONTRACT TESTS
# =============================================================================

def test_classification_system_valid():
    cls_sys = ClassificationSystem(
        classification_id="UK_SOC_2020",
        market_id="UK",
        official_title="UK Standard Occupational Classification 2020",
        version_edition="2020 Volume 1",
        issuing_authority="Office for National Statistics",
        code_format=r"^\d{4}$",
        hierarchy_levels=("Major Group", "Sub-Major Group", "Minor Group", "Unit Group"),
        is_active=True,
        source_reference="https://www.ons.gov.uk/methodology",
        license_attribution="Open Government Licence v3.0",
    )
    assert cls_sys.classification_id == "UK_SOC_2020"
    assert cls_sys.market_id == "UK"


def test_national_occupation_id_prefix_validation():
    with pytest.raises(ValueError, match="occupation_id must start with"):
        NationalOccupation(
            occupation_id="INVALID_PREFIX:2134",
            classification_id="UK_SOC_2020",
            market_id="UK",
            occupation_code="2134",
            occupation_title="Programmers",
            official_definition="Test definition with sufficient length",
            hierarchy_level="Unit Group",
        )


def test_confidence_policy_enforcement_synthetic_1_0():
    # Synthetic 1.0 is strictly forbidden for non-VERIFIED_OFFICIAL
    with pytest.raises(ValueError, match="confidence_score of 1.0 is strictly reserved"):
        OccupationMapping(
            mapping_id="map_invalid_1",
            source_occupation_id="UK_SOC_2020:2134",
            target_occupation_id="US_SOC_2018:15-1252",
            target_type=TargetType.NATIONAL,
            relationship_type=RelationshipType.EXACT_MATCH,
            confidence_score=Decimal("1.0"),
            review_status=ReviewStatus.DERIVED_HIGH_CONFIDENCE,  # Invalid pairing
            methodology=MappingMethodology.EXPERT_ASSESSMENT,
            evidence_sources=("https://example.com",),
            notes_and_limitations="Test note",
            reviewer="Reviewer",
            effective_date="2026-11-16",
            created_at="2026-11-16T10:00:00Z",
        )


def test_confidence_policy_enforcement_unmapped_must_be_zero():
    with pytest.raises(ValueError, match="UNMAPPED or REJECTED mappings must have confidence_score 0.0"):
        OccupationMapping(
            mapping_id="map_invalid_2",
            source_occupation_id="UK_SOC_2020:2134",
            target_occupation_id="US_SOC_2018:15-1252",
            target_type=TargetType.NATIONAL,
            relationship_type=RelationshipType.NO_SUPPORTED_MAPPING,
            confidence_score=Decimal("0.5"),  # Invalid
            review_status=ReviewStatus.UNMAPPED,
            methodology=MappingMethodology.EXPERT_ASSESSMENT,
            evidence_sources=("https://example.com",),
            notes_and_limitations="Test note",
            reviewer="Reviewer",
            effective_date="2026-11-16",
            created_at="2026-11-16T10:00:00Z",
        )


# =============================================================================
# 2. SERVICE & REGISTRY TESTS
# =============================================================================

def test_occupation_service_classifications():
    service = get_occupation_service()
    classifications = service.get_classifications()
    assert len(classifications) >= 8

    class_ids = {c.classification_id for c in classifications}
    expected_ids = {
        "UK_SOC_2020",
        "US_SOC_2018",
        "AU_OSCA_2024",
        "AU_ANZSCO_2022",
        "SG_SSOC_2024",
        "SG_SSOC_2020",
        "IN_NCO_2015",
        "INT_ISCO_08",
    }
    assert expected_ids.issubset(class_ids)

    # Filter by market
    uk_class = service.get_classifications(market_id="UK")
    assert len(uk_class) == 1
    assert uk_class[0].classification_id == "UK_SOC_2020"

    # Specific retrieval
    us_class = service.get_classification("US_SOC_2018")
    assert us_class.market_id == "US"
    assert us_class.issuing_authority.startswith("Bureau of Labor Statistics")

    with pytest.raises(ClassificationNotFoundError):
        service.get_classification("NONEXISTENT_CLASSIFICATION")


def test_occupation_service_occupations_and_pagination():
    service = get_occupation_service()
    uk_occs, total = service.get_occupations("UK_SOC_2020", page=1, page_size=5)
    assert len(uk_occs) <= 5
    assert total >= 8
    assert all(o.classification_id == "UK_SOC_2020" for o in uk_occs)

    # Filter within classification
    filtered, f_total = service.get_occupations("UK_SOC_2020", query="cyber")
    assert f_total >= 1
    assert any("cyber" in o.occupation_title.lower() for o in filtered)


def test_occupation_service_search_scoring():
    service = get_occupation_service()
    # Search by code
    code_results = service.search_occupations("2134")
    assert len(code_results) >= 1
    assert code_results[0].occupation_code == "2134"

    # Search by title
    dev_results = service.search_occupations("Software Developer", limit=5)
    assert len(dev_results) >= 1
    assert any("Software Developer" in o.occupation_title for o in dev_results)

    # Search with market filter
    sg_results = service.search_occupations("Cyber", market_id="SG")
    assert len(sg_results) >= 1
    assert sg_results[0].market_id == "SG"


def test_occupation_service_canonical_and_cross_market():
    service = get_occupation_service()
    canonical_list = service.get_canonical_occupations()
    assert len(canonical_list) >= 12

    soft_eng = service.get_canonical_occupation("CAN_OCC_SOFTWARE_ENGINEER")
    assert soft_eng.preferred_title == "Software Engineer"
    assert len(soft_eng.core_competencies) >= 3

    with pytest.raises(CanonicalOccupationNotFoundError):
        service.get_canonical_occupation("CAN_OCC_NONEXISTENT")

    # Cross-Market Comparison from UK SOC 2134
    comparison = service.compare_across_markets("UK_SOC_2020:2134")
    assert comparison.source_occupation.occupation_code == "2134"
    assert comparison.total_matches >= 2

    # Verify approximation warning when confidence < 0.95
    us_match = next((m for m in comparison.matches if m.target_market_id == "US"), None)
    assert us_match is not None
    assert us_match.relationship_type == RelationshipType.CLOSE_MATCH
    assert us_match.confidence_score == Decimal("0.92")
    assert us_match.approximation_warning is not None
    assert "92%" in us_match.approximation_warning


# =============================================================================
# 3. FASTAPI API ROUTE TESTS
# =============================================================================

def test_api_list_classifications():
    res = client.get("/api/v1/occupations/classifications")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 8

    # Test root-mounted alias
    res_root = client.get("/v1/occupations/classifications")
    assert res_root.status_code == 200


def test_api_retrieve_classification():
    res = client.get("/api/v1/occupations/classifications/UK_SOC_2020")
    assert res.status_code == 200
    data = res.json()
    assert data["classification_id"] == "UK_SOC_2020"
    assert data["market_id"] == "UK"

    res_404 = client.get("/api/v1/occupations/classifications/UNKNOWN_CLASSIFICATION")
    assert res_404.status_code == 404


def test_api_list_occupations_by_classification():
    res = client.get("/api/v1/occupations/classifications/UK_SOC_2020/occupations?page=1&page_size=4")
    assert res.status_code == 200
    data = res.json()
    assert len(data["items"]) == 4
    assert data["page"] == 1
    assert data["page_size"] == 4
    assert data["total_count"] >= 8
    assert data["has_next"] is True


def test_api_search_occupations():
    res = client.get("/api/v1/occupations/search?q=Data%20Scientist")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert any("Data Scientist" in item["occupation_title"] for item in data)


def test_api_canonical_occupations():
    res = client.get("/api/v1/occupations/canonical")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 12

    res_single = client.get("/api/v1/occupations/canonical/CAN_OCC_DATA_SCIENTIST")
    assert res_single.status_code == 200
    assert res_single.json()["preferred_title"] == "Data Scientist"

    res_404 = client.get("/api/v1/occupations/canonical/CAN_OCC_UNKNOWN")
    assert res_404.status_code == 404


def test_api_compare_across_markets():
    res = client.get("/api/v1/occupations/compare?source_occupation_id=UK_SOC_2020:2134")
    assert res.status_code == 200
    data = res.json()
    assert data["source_occupation"]["occupation_id"] == "UK_SOC_2020:2134"
    assert len(data["matches"]) >= 2
    assert "US" in [m["target_market_id"] for m in data["matches"]]


def test_api_retrieve_occupation_detail_and_mappings():
    res = client.get("/api/v1/occupations/UK_SOC_2020:2134")
    assert res.status_code == 200
    data = res.json()
    assert data["occupation_code"] == "2134"
    assert "Programmers" in data["occupation_title"]
    assert len(data["tasks"]) >= 1

    res_maps = client.get("/api/v1/occupations/UK_SOC_2020:2134/mappings")
    assert res_maps.status_code == 200
    maps_data = res_maps.json()
    assert len(maps_data) >= 2

    res_404 = client.get("/api/v1/occupations/UK_SOC_2020:NONEXISTENT_CODE")
    assert res_404.status_code == 404


def test_api_concordance_coverage_stats():
    res = client.get("/api/v1/occupations/coverage")
    assert res.status_code == 200
    data = res.json()
    assert data["total_national_occupations"] == 30
    assert data["mapped_national_occupations"] == 30
    assert data["unmapped_national_occupations"] == 0
    assert data["total_canonical_concepts"] == 12
    assert data["linked_canonical_concepts"] == 11
    assert data["unlinked_canonical_concepts"] == 1
    assert data["total_mappings"] == 62
    assert data["official_mappings_count"] == 4
    assert data["expert_reviewed_mappings_count"] == 58


def test_api_task_similarity_endpoint():
    res = client.get("/api/v1/occupations/similarity?source_id=UK_SOC_2020:2134&target_id=US_SOC_2018:15-1252")
    assert res.status_code == 200
    data = res.json()
    assert data["source_id"] == "UK_SOC_2020:2134"
    assert data["target_id"] == "US_SOC_2018:15-1252"
    assert 0.0 <= data["jaccard_similarity"] <= 1.0
    assert 0.0 <= data["tfidf_cosine_similarity"] <= 1.0
    assert data["metric_type"] == "UNSUPERVISED_LEXICAL_SIMILARITY"
    assert "not constitute empirical probability" in data["limitations"].lower()


def test_occupation_task_provenance_tagging():
    res_uk = client.get("/api/v1/occupations/UK_SOC_2020:2134")
    assert res_uk.status_code == 200
    assert res_uk.json()["task_provenance"] == "OFFICIAL_VERBATIM"

    res_us = client.get("/api/v1/occupations/US_SOC_2018:15-1252")
    assert res_us.status_code == 200
    assert res_us.json()["task_provenance"] == "OFFICIALLY_DERIVED"

    res_au = client.get("/api/v1/occupations/AU_OSCA_2024:261313")
    assert res_au.status_code == 200
    assert res_au.json()["task_provenance"] == "JOBINTEL_CURATED"


def test_concordance_completion_and_canonical_activation():
    service = get_occupation_service()
    coverage = service.get_coverage_stats()
    assert coverage.total_mappings == 62
    assert coverage.mapped_national_occupations == 30
    assert coverage.unmapped_national_occupations == 0

    # Verify activated canonical concepts have mappings
    activated_concepts = [
        "CAN_OCC_DATABASE_ADMIN",
        "CAN_OCC_SYSTEMS_ANALYST",
        "CAN_OCC_NETWORK_ENGINEER",
        "CAN_OCC_IT_PROJECT_MGR",
    ]
    for can_id in activated_concepts:
        mappings = [m for m_list in service._mappings_by_source.values() for m in m_list if m.target_occupation_id == can_id]
        assert len(mappings) >= 1, f"Expected {can_id} to be linked to at least 1 national occupation"

    # Verify CAN_OCC_DATA_ENGINEER remains intentionally unmapped with 0 national links
    de_mappings = [m for m_list in service._mappings_by_source.values() for m in m_list if m.target_occupation_id == "CAN_OCC_DATA_ENGINEER"]
    assert len(de_mappings) == 0, "Expected CAN_OCC_DATA_ENGINEER to remain unlinked per defensibility standard"

