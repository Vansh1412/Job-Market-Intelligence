# 03. TypeScript & Pydantic Reconciliation Report

## 1. Reconciliation Overview

A comprehensive, field-by-field AST and schema comparison was performed between backend Pydantic models (`src/backend/schemas/employer.py`) and frontend TypeScript definitions (`frontend/src/types.ts`).

- **Total Pydantic Models Evaluated**: 6
- **Total TypeScript Interfaces Evaluated**: 6
- **Total Fields Compared**: 39
- **Matching Fields**: 39 (100% parity)
- **Mismatches / Omissions**: 0
- **Total Enums Evaluated**: 5
- **Matching Enum Values**: 21 / 21 (100% parity)

---

## 2. Enum Reconciliation Matrix

| Enum Name | Pydantic Values (`src/backend/schemas/employer.py`) | TypeScript Values (`frontend/src/types.ts`) | Parity Status |
|---|---|---|---|
| `EmployerCategory` | `ENTERPRISE`, `MID_MARKET`, `SMB`, `STARTUP` | `'ENTERPRISE'`, `'MID_MARKET'`, `'SMB'`, `'STARTUP'` | **100% MATCH** |
| `EmployerVerificationStatus` | `UNVERIFIED`, `PENDING_REVIEW`, `VERIFIED_STATUTORY`, `REJECTED` | `'UNVERIFIED'`, `'PENDING_REVIEW'`, `'VERIFIED_STATUTORY'`, `'REJECTED'` | **100% MATCH** |
| `EmployerLocationType` | `HEADQUARTERS`, `REGIONAL_OFFICE`, `BRANCH`, `REMOTE_HUB` | `'HEADQUARTERS'`, `'REGIONAL_OFFICE'`, `'BRANCH'`, `'REMOTE_HUB'` | **100% MATCH** |
| `ResolutionMatchType` | `EXACT_STATUTORY`, `CANONICAL_NAME`, `FUZZY_NAME`, `ALIAS_MATCH`, `NO_MATCH` | `'EXACT_STATUTORY'`, `'CANONICAL_NAME'`, `'FUZZY_NAME'`, `'ALIAS_MATCH'`, `'NO_MATCH'` | **100% MATCH** |
| `EntityReviewStatus` | `AUTO_VERIFIED`, `MANUAL_REVIEW_REQUIRED`, `CONFIRMED_DISTINCT`, `REJECTED` | `'AUTO_VERIFIED'`, `'MANUAL_REVIEW_REQUIRED'`, `'CONFIRMED_DISTINCT'`, `'REJECTED'` | **100% MATCH** |

---

## 3. Detailed Model Field-by-Field Matrix

### Model 1: `EmployerSourceReference` (6 fields)
| Field | Pydantic Type | TypeScript Type | Nullable | Parity |
|---|---|---|---|---|
| `source_name` | `str` | `string` | No | Match |
| `source_type` | `str` | `string` | No | Match |
| `source_url` | `Optional[str] = None` | `string \| null` | Yes | Match |
| `retrieved_at` | `datetime` | `string` (ISO 8601) | No | Match |
| `record_id` | `Optional[str] = None` | `string \| null` | Yes | Match |
| `source_hash` | `Optional[str] = None` | `string \| null` | Yes | Match |

### Model 2: `EmployerLocation` (6 fields)
| Field | Pydantic Type | TypeScript Type | Nullable | Parity |
|---|---|---|---|---|
| `country_code` | `str` | `string` | No | Match |
| `location_type` | `EmployerLocationType` | `EmployerLocationType` | No | Match |
| `city` | `Optional[str] = None` | `string \| null` | Yes | Match |
| `state_province` | `Optional[str] = None` | `string \| null` | Yes | Match |
| `postal_code` | `Optional[str] = None` | `string \| null` | Yes | Match |
| `address_line` | `Optional[str] = None` | `string \| null` | Yes | Match |

### Model 3: `EmployerProfile` (8 fields)
| Field | Pydantic Type | TypeScript Type | Nullable | Parity |
|---|---|---|---|---|
| `company_id` | `str` | `string` | No | Match |
| `canonical_name` | `str` | `string` | No | Match |
| `category` | `EmployerCategory` | `EmployerCategory` | No | Match |
| `verification_status` | `EmployerVerificationStatus` | `EmployerVerificationStatus` | No | Match |
| `statutory_identifiers` | `Dict[str, str]` | `Record<string, string>` | No | Match |
| `locations` | `List[EmployerLocation]` | `EmployerLocation[]` | No | Match |
| `source_references` | `List[EmployerSourceReference]` | `EmployerSourceReference[]` | No | Match |
| `created_at` | `datetime` | `string` (ISO 8601) | No | Match |

### Model 4: `EntityMatchCandidate` (4 fields)
| Field | Pydantic Type | TypeScript Type | Nullable | Parity |
|---|---|---|---|---|
| `company_id` | `str` | `string` | No | Match |
| `canonical_name` | `str` | `string` | No | Match |
| `similarity_score` | `float` | `number` | No | Match |
| `match_reasons` | `List[str]` | `string[]` | No | Match |

### Model 5: `EmployerResolutionRequest` (6 fields)
| Field | Pydantic Type | TypeScript Type | Nullable | Parity |
|---|---|---|---|---|
| `candidate_name` | `str` | `string` | No | Match |
| `country_code` | `Optional[str] = None` | `string \| null` | Yes | Match |
| `statutory_identifier` | `Optional[str] = None` | `string \| null` | Yes | Match |
| `context_metadata` | `Optional[Dict[str, Any]] = None` | `Record<string, any> \| null` | Yes | Match |
| `fuzzy_threshold` | `Optional[float] = 0.85` | `number \| null` | Yes | Match |
| `max_candidates` | `Optional[int] = 5` | `number \| null` | Yes | Match |

### Model 6: `EmployerResolutionResponse` (9 fields)
| Field | Pydantic Type | TypeScript Type | Nullable | Parity |
|---|---|---|---|---|
| `match_type` | `ResolutionMatchType` | `ResolutionMatchType` | No | Match |
| `resolved_company_id` | `Optional[str] = None` | `string \| null` | Yes | Match |
| `resolved_canonical_name` | `Optional[str] = None` | `string \| null` | Yes | Match |
| `similarity_score` | `float` | `number` | No | Match |
| `review_status` | `EntityReviewStatus` | `EntityReviewStatus` | No | Match |
| `candidates` | `List[EntityMatchCandidate]` | `EntityMatchCandidate[]` | No | Match |
| `provenance_notes` | `List[str]` | `string[]` | No | Match |
| `warnings` | `List[str]` | `string[]` | No | Match |
| `resolved_profile` | `Optional[EmployerProfile] = None` | `EmployerProfile \| null` | Yes | Match |

---

## 4. Critical Nullable Semantics Verification

1. **`resolved_company_id`**:
   - Backend: `Optional[str] = None`. Set to `None` on `NO_MATCH` or ambiguous collision.
   - Frontend: `string | null`. The frontend checks `result.resolved_company_id === null` to display warning badges and disallow fake navigation to nonexistent company detail routes.
2. **`candidates`**:
   - Backend: `List[EntityMatchCandidate] = Field(default_factory=list)`. Never `None`; always an array.
   - Frontend: `EntityMatchCandidate[]`. The frontend handles empty arrays gracefully without throwing `.map()` errors.
3. **Optional Parameters in Requests**:
   - In `EmployerResolutionRequest`, `statutory_identifier` and `country_code` are properly omitted or passed as `null` if empty strings are input by the user, adhering strictly to Pydantic validation rules.
