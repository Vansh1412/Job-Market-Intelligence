# JOBINTEL 2.0 — SPRINT 3A
## Canonical Occupation Architecture: Taxonomy, Classification Mapping & Interoperability Design

**Date:** November 16, 2026  
**Sprint:** 3A  
**Status:** Approved Architectural Standard (`JOBINTEL-S3A-ARCH-001`)  
**Author:** Principal Data Architect, Backend Architect, Occupational Taxonomy Researcher  

---

## 1. Architectural Philosophy & The Interoperability Layer

Labour market policies, vocational certifications, educational standards, and statutory responsibilities differ profoundly between nations. Previous attempts to homogenize occupations across countries by collapsing them into a single global taxonomy inevitably destroyed critical local fidelity:
- An "IT Business Analyst" in the UK (SOC `2133`) requires distinct certifications and roles compared to a US "Computer Systems Analyst" (SOC `15-1211`).
- Australia’s newly introduced OSCA 2024 splits software engineers (`261313`) from developer programmers (`261312`) and analyst programmers (`261311`), while US SOC `15-1252` merges them into a single "Software Developers" unit group.
- Singapore's SSOC 2024 explicitly creates dedicated unit codes for AI/ML Engineers (`25131`) and Cloud Architects (`25124`), whereas older systems scatter them across general software developer codes.

### Core Architectural Axiom
```
┌────────────────────────────────────────────────────────────────────────┐
│                        CANONICAL OCCUPATION LAYER                      │
│                  (Interoperable Career Concepts)                       │
│    - Global Career Concept (e.g. Software Engineer, Data Scientist)    │
│    - Does NOT replace national standards                               │
│    - Governs multi-market query routing & semantic exploration         │
└──────────────────┬──────────────────────────────────┬──────────────────┘
                   │                                  │
                   ▼ (Canonical Mappings)             ▼
┌───────────────────────────────────────┐  ┌─────────────────────────────┐
│      NATIONAL OCCUPATION RECORD       │  │ NATIONAL OCCUPATION RECORD  │
│          UK SOC 2020: 2134            │  │      US SOC 2018: 15-1252   │
│  "Programmers and software dev prof"  │  │     "Software Developers"   │
└──────────────────┬────────────────────┘  └─────────────┬───────────────┘
                   │                                     │
                   └─────────── Direct Crosswalk ────────┘
                          (Evidence-Backed Bilateral)
```

**Rule:** National occupation classifications remain authoritative within their respective jurisdictions. The canonical occupation layer is an interoperability layer, not a replacement for national standards.

---

## 2. The Three Core Entity Domains

### 2.1 Classification System (`ClassificationSystem`)
Represents a specific official national or international classification standard and edition.
- **Key Attributes:**
  - `classification_id`: Unique immutable identifier (e.g., `UK_SOC_2020`, `US_SOC_2018`, `AU_OSCA_2024`, `AU_ANZSCO_2022`, `SG_SSOC_2024`, `IN_NCO_2015`, `INT_ISCO_08`).
  - `market_id`: Jurisdiction identifier (`IN`, `US`, `UK`, `AU`, `SG`, or `INT`).
  - `official_title`: Official full name of the standard.
  - `version_edition`: Edition year or revision label.
  - `issuing_authority`: Government agency responsible for maintenance.
  - `code_format`: Regex pattern enforcing structural code validity.
  - `hierarchy_levels`: Tuple of hierarchical tier labels (e.g. `("Major", "Sub-Major", "Minor", "Unit Group")`).
  - `is_active`: Boolean indicating whether this is the prevailing current standard in the jurisdiction.
  - `source_reference`: Official URL or publication citation.

### 2.2 National Occupation Record (`NationalOccupation`)
Represents an individual occupation or occupational unit group within a specific classification system.
- **Key Attributes:**
  - `occupation_id`: Fully qualified global composite ID (e.g., `UK_SOC_2020:2134`, `US_SOC_2018:15-1252`).
  - `classification_id`: Foreign key reference to `ClassificationSystem`.
  - `market_id`: Jurisdiction identifier.
  - `occupation_code`: Official code string (e.g., `2134`, `15-1252`, `261313`, `25121`).
  - `occupation_title`: Official title verbatim from the issuing authority.
  - `official_definition`: Authoritative scope note or group description.
  - `tasks`: Tuple of typical duties and responsibilities.
  - `entry_qualifications`: Documented education, apprenticeship, or licensing requirements.
  - `hierarchy_level`: Hierarchy depth (e.g. `Unit Group`, `Detailed Occupation`).
  - `parent_code`: Parent grouping code (e.g., Minor Group code).
  - `is_leaf`: Boolean indicating whether this is the most granular codable unit.
  - `alternate_titles`: Tuple of official coding index aliases.

### 2.3 Canonical Occupation Concept (`CanonicalOccupation`)
Represents a cross-jurisdictional, harmonized occupational archetype designed for international benchmarking and navigation.
- **Key Attributes:**
  - `canonical_occupation_id`: Stable identifier (e.g., `CAN_OCC_SOFTWARE_ENGINEER`, `CAN_OCC_DATA_SCIENTIST`).
  - `preferred_title`: Neutral, universally understood title.
  - `concept_family`: Broad occupational domain (e.g., `Software & Applications`, `Data & Analytics`, `Infrastructure & Cloud`, `Security & Privacy`, `Technology Leadership`).
  - `description`: Comprehensive cross-market definition synthesizing international commonalities while highlighting regional divergences.
  - `core_competencies`: Fundamental skills and knowledge required across all jurisdictions.
  - `status`: Lifecycle status (`ACTIVE`, `DEPRECATED`, `PROVISIONAL`).

---

## 3. The Relationship & Concordance Model

Concordance between occupations is modeled through explicit, directed `OccupationMapping` records.

### 3.1 Mapping Relationship Types
Every mapping record must possess an explicit relationship type with formal mathematical and semantic properties:

| Relationship Type | Semantic Definition | Mathematical Property | Inverse Relationship | Example |
| :--- | :--- | :--- | :--- | :--- |
| **`EXACT_MATCH`** | Occupational duties, primary responsibilities, and skill scope are substantially identical. | Bidirectional Equivalence | `EXACT_MATCH` | US SOC `15-1252` $\leftrightarrow$ AU OSCA `261313` |
| **`CLOSE_MATCH`** | High functional alignment; minor differences in terminology, credentialing, or reporting convention. | Bidirectional Similarity | `CLOSE_MATCH` | UK SOC `2134` $\leftrightarrow$ US SOC `15-1252` |
| **`BROADER_THAN`** | Source occupation is an aggregate category that encompasses multiple distinct target specializations. | Directed Asymmetry | `NARROWER_THAN` | ISCO-08 `2512` $\to$ SG SSOC `25125` (DevOps) |
| **`NARROWER_THAN`** | Source occupation is a specialized discipline subsumed within a broader target category. | Directed Asymmetry | `BROADER_THAN` | SG SSOC `25125` (DevOps) $\to$ ISCO-08 `2512` |
| **`PARTIAL_OVERLAP`** | Occupations share significant core competencies, but major duties or qualification paths diverge. | Non-transitive Overlap | `PARTIAL_OVERLAP` | UK SOC `2133` (Sys Designer) $\leftrightarrow$ US SOC `15-1211` |
| **`RELATED_BUT_DISTINCT`** | Cognate or adjacent professions that frequently interact but are not substitutable. | Non-substitutable Adjacency | `RELATED_BUT_DISTINCT` | Data Analyst $\leftrightarrow$ Business Analyst |
| **`NO_SUPPORTED_MAPPING`** | Specific to national context with no credible counterpart in the target jurisdiction. | Terminal Null | `NO_SUPPORTED_MAPPING` | Local civil service / country-unique trades |

### 3.2 Graph Consistency Invariants
1. **Symmetry Invariant:** If mapping $A \to B$ is `EXACT_MATCH`, the inverse mapping $B \to A$ must exist, must be `EXACT_MATCH`, and must possess identical confidence.
2. **Dual Asymmetry Invariant:** If mapping $A \to B$ is `BROADER_THAN`, the inverse mapping $B \to A$ must be `NARROWER_THAN`.
3. **Version Specificity:** All mappings must explicitly reference the source and target `classification_id` and version. Generic unversioned mappings are rejected.
4. **No Synthetic 1.00:** A confidence score of $1.00$ may only be assigned when an official government concordance table explicitly establishes direct correspondence. Derived mappings are capped at $0.95$.

---

## 4. Provenance & Audit Trail Schema

Every mapping record is required to embed complete provenance:
```python
class MappingProvenance(BaseModel):
    mapping_id: str
    source_classification_id: str
    source_occupation_code: str
    target_classification_id: str
    target_occupation_code: str
    relationship_type: RelationshipType
    methodology: MappingMethodology  # OFFICIAL_CROSSWALK, EXPERT_ASSESSMENT, CALIBRATED_TASK_OVERLAP
    confidence_score: Decimal        # Between 0.00 and 1.00
    review_status: ReviewStatus      # VERIFIED_OFFICIAL, VERIFIED_REVIEWED, DERIVED_HIGH_CONFIDENCE, etc.
    evidence_sources: tuple[str, ...]
    notes_and_limitations: str
    reviewer: str
    effective_date: str
    created_at: datetime
```

---

## 5. Storage & Query Strategy

1. **Lightweight, Versioned In-Memory Registries:**
   - Classification systems, national occupations, canonical concepts, and concordance mappings are stored as versioned, validated JSON registries located in `src/backend/data/occupations/`.
   - On application startup, the `OccupationRegistry` loads, parses, validates, and indexes these records into fast in-memory lookup graphs with $O(1)$ code lookups and $O(K)$ relationship traversals.
   - Zero external database dependencies (no PostgreSQL or Redis required), maintaining complete compliance with Render Free and Vercel limits.
2. **Deterministic Search & Ranking:**
   - Exact code match $\to$ Exact title match $\to$ Alternate title / alias match $\to$ Substring token match.
   - Preserves official titles vs. derived aliases.
