from __future__ import annotations

import json
import logging
import os
from decimal import Decimal
from pathlib import Path
from typing import Any

from src.backend.schemas.occupation import (
    CanonicalOccupation,
    ClassificationSystem,
    ConcordanceCoverageStats,
    CrossMarketComparisonResult,
    CrossMarketMatchItem,
    NationalOccupation,
    OccupationMapping,
    RelationshipType,
    ReviewStatus,
    TargetType,
    TaskSimilarityPayload,
)
from src.backend.services.task_similarity import (
    TfidfModel,
    calculate_jaccard_similarity,
    normalize_tasks,
)

logger = logging.getLogger("jobintel.occupation_service")

DEFAULT_OCCUPATIONS_DIR = Path(__file__).resolve().parent.parent / "data" / "occupations"


class OccupationNotFoundError(Exception):
    pass


class ClassificationNotFoundError(Exception):
    pass


class CanonicalOccupationNotFoundError(Exception):
    pass


class OccupationService:
    def __init__(self, data_dir: Path | str | None = None) -> None:
        self.data_dir = Path(data_dir) if data_dir else DEFAULT_OCCUPATIONS_DIR
        self._classifications: dict[str, ClassificationSystem] = {}
        self._classifications_by_market: dict[str, list[ClassificationSystem]] = {}
        self._national_occupations: dict[str, NationalOccupation] = {}
        self._occupations_by_classification: dict[str, list[NationalOccupation]] = {}
        self._occupations_by_market: dict[str, list[NationalOccupation]] = {}
        self._canonical_occupations: dict[str, CanonicalOccupation] = {}
        self._mappings_by_source: dict[str, list[OccupationMapping]] = {}
        self._mappings_by_target: dict[str, list[OccupationMapping]] = {}
        self._tfidf_model: TfidfModel | None = None
        self._load_and_validate()

    def _load_and_validate(self) -> None:
        """Loads and strictly validates all JSON occupation datasets against Pydantic models."""
        classifications_path = self.data_dir / "classifications.json"
        canonical_path = self.data_dir / "canonical_occupations.json"
        national_path = self.data_dir / "national_occupations.json"
        mappings_path = self.data_dir / "mappings.json"

        if not classifications_path.exists():
            raise FileNotFoundError(f"Missing classifications registry at {classifications_path}")
        if not canonical_path.exists():
            raise FileNotFoundError(f"Missing canonical registry at {canonical_path}")
        if not national_path.exists():
            raise FileNotFoundError(f"Missing national occupations registry at {national_path}")
        if not mappings_path.exists():
            raise FileNotFoundError(f"Missing mappings registry at {mappings_path}")

        # 1. Classifications
        with open(classifications_path, "r", encoding="utf-8") as f:
            raw_classifications = json.load(f)
        for raw in raw_classifications:
            item = ClassificationSystem.model_validate(raw)
            self._classifications[item.classification_id] = item
            self._classifications_by_market.setdefault(item.market_id, []).append(item)

        # 2. Canonical Occupations
        with open(canonical_path, "r", encoding="utf-8") as f:
            raw_canonical = json.load(f)
        for raw in raw_canonical:
            item = CanonicalOccupation.model_validate(raw)
            self._canonical_occupations[item.canonical_occupation_id] = item

        # 3. National Occupations
        with open(national_path, "r", encoding="utf-8") as f:
            raw_national = json.load(f)
        for raw in raw_national:
            item = NationalOccupation.model_validate(raw)
            if item.classification_id not in self._classifications:
                raise ValueError(f"Unknown classification_id '{item.classification_id}' in occupation {item.occupation_id}")
            self._national_occupations[item.occupation_id] = item
            self._occupations_by_classification.setdefault(item.classification_id, []).append(item)
            self._occupations_by_market.setdefault(item.market_id, []).append(item)

        # 4. Concordance Mappings
        with open(mappings_path, "r", encoding="utf-8") as f:
            raw_mappings = json.load(f)
        for raw in raw_mappings:
            item = OccupationMapping.model_validate(raw)
            if item.source_occupation_id not in self._national_occupations:
                raise ValueError(f"Unknown source_occupation_id '{item.source_occupation_id}' in mapping {item.mapping_id}")
            if item.target_type == TargetType.NATIONAL:
                if item.target_occupation_id not in self._national_occupations:
                    raise ValueError(f"Unknown target_occupation_id '{item.target_occupation_id}' in mapping {item.mapping_id}")
            elif item.target_type == TargetType.CANONICAL:
                if item.target_occupation_id not in self._canonical_occupations:
                    raise ValueError(f"Unknown target canonical_id '{item.target_occupation_id}' in mapping {item.mapping_id}")

            self._mappings_by_source.setdefault(item.source_occupation_id, []).append(item)
            self._mappings_by_target.setdefault(item.target_occupation_id, []).append(item)

        # 5. Initialize TF-IDF model on national occupation task descriptions
        corpus = [normalize_tasks(occ.tasks) for occ in self._national_occupations.values()]
        self._tfidf_model = TfidfModel(corpus)

        logger.info(
            "OccupationService initialized with %d classifications, %d national occupations, %d canonical concepts, %d mappings.",
            len(self._classifications),
            len(self._national_occupations),
            len(self._canonical_occupations),
            len(raw_mappings),
        )

    # -------------------------------------------------------------
    # Classification Queries
    # -------------------------------------------------------------

    def get_classifications(self, market_id: str | None = None) -> list[ClassificationSystem]:
        if market_id:
            return list(self._classifications_by_market.get(market_id.upper(), []))
        return list(self._classifications.values())

    def get_classification(self, classification_id: str) -> ClassificationSystem:
        if classification_id not in self._classifications:
            raise ClassificationNotFoundError(f"Classification '{classification_id}' not found.")
        return self._classifications[classification_id]

    # -------------------------------------------------------------
    # National Occupation Queries
    # -------------------------------------------------------------

    def get_occupations(
        self,
        classification_id: str,
        query: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[NationalOccupation], int]:
        all_occupations = self._occupations_by_classification.get(classification_id, [])
        if query:
            q = query.lower().strip()
            filtered = [
                occ for occ in all_occupations
                if q in occ.occupation_code.lower()
                or q in occ.occupation_title.lower()
                or any(q in alt.lower() for alt in occ.alternate_titles)
            ]
        else:
            filtered = all_occupations

        total = len(filtered)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        items = filtered[start_idx:end_idx]
        return items, total

    def get_occupation(self, occupation_id: str) -> NationalOccupation:
        if occupation_id not in self._national_occupations:
            raise OccupationNotFoundError(f"Occupation '{occupation_id}' not found.")
        return self._national_occupations[occupation_id]

    def search_occupations(
        self,
        query: str,
        market_id: str | None = None,
        classification_id: str | None = None,
        limit: int = 20,
    ) -> list[NationalOccupation]:
        q = query.lower().strip()
        candidates = list(self._national_occupations.values())
        if market_id:
            m = market_id.upper()
            candidates = [c for c in candidates if c.market_id == m]
        if classification_id:
            candidates = [c for c in candidates if c.classification_id == classification_id]

        if not q:
            return candidates[:limit]

        scored: list[tuple[int, NationalOccupation]] = []
        for occ in candidates:
            score = 0
            # 1. Exact code match
            if occ.occupation_code.lower() == q or occ.occupation_id.lower() == q:
                score += 100
            elif occ.occupation_code.lower().startswith(q):
                score += 50
            # 2. Title match
            if occ.occupation_title.lower() == q:
                score += 80
            elif q in occ.occupation_title.lower():
                score += 40
            # 3. Alternate titles match
            for alt in occ.alternate_titles:
                if alt.lower() == q:
                    score += 60
                    break
                elif q in alt.lower():
                    score += 25
                    break
            # 4. Definition search
            if q in occ.official_definition.lower():
                score += 10

            if score > 0:
                scored.append((score, occ))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:limit]]

    # -------------------------------------------------------------
    # Canonical Occupation Queries
    # -------------------------------------------------------------

    def get_canonical_occupations(self) -> list[CanonicalOccupation]:
        return list(self._canonical_occupations.values())

    def get_canonical_occupation(self, canonical_id: str) -> CanonicalOccupation:
        if canonical_id not in self._canonical_occupations:
            raise CanonicalOccupationNotFoundError(f"Canonical concept '{canonical_id}' not found.")
        return self._canonical_occupations[canonical_id]

    # -------------------------------------------------------------
    # Concordance & Cross-Market Comparison
    # -------------------------------------------------------------

    def get_mappings(self, occupation_id: str, target_market: str | None = None) -> list[OccupationMapping]:
        mappings = list(self._mappings_by_source.get(occupation_id, []))
        if target_market:
            tm = target_market.upper()
            filtered = []
            for m in mappings:
                if m.target_type == TargetType.NATIONAL:
                    target_occ = self._national_occupations.get(m.target_occupation_id)
                    if target_occ and target_occ.market_id == tm:
                        filtered.append(m)
                elif m.target_type == TargetType.CANONICAL and tm == "INT":
                    filtered.append(m)
            return filtered
        return mappings

    def compare_across_markets(
        self,
        source_occupation_id: str,
        target_market: str | None = None,
    ) -> CrossMarketComparisonResult:
        source_occ = self.get_occupation(source_occupation_id)
        source_market = source_occ.market_id

        # Direct national mappings from source
        direct_mappings = self._mappings_by_source.get(source_occupation_id, [])

        matches: list[CrossMarketMatchItem] = []
        covered_markets = {source_market}

        for m in direct_mappings:
            warning = None
            if m.confidence_score < Decimal("0.95") and m.confidence_score > Decimal("0.0"):
                warning = (
                    f"This comparison relies on an approximate concordance between {source_occ.occupation_title} "
                    f"({source_occ.occupation_code}) and target with evaluated confidence {int(m.confidence_score * 100)}%. "
                    f"Roles differ in specific tasks, scope, or qualifications."
                )

            if m.target_type == TargetType.NATIONAL:
                target_occ = self._national_occupations.get(m.target_occupation_id)
                if not target_occ:
                    continue
                if target_market and target_occ.market_id != target_market.upper():
                    continue

                # Unsupervised task lexical similarity (separate from heuristic confidence)
                similarity_score = None
                if self._tfidf_model:
                    tok_s = normalize_tasks(source_occ.tasks)
                    tok_t = normalize_tasks(target_occ.tasks)
                    similarity_score = self._tfidf_model.cosine_similarity(tok_s, tok_t)

                covered_markets.add(target_occ.market_id)
                matches.append(
                    CrossMarketMatchItem(
                        target_occupation=target_occ,
                        target_type=TargetType.NATIONAL,
                        target_market_id=target_occ.market_id,
                        relationship_type=m.relationship_type,
                        confidence_score=m.confidence_score,
                        review_status=m.review_status,
                        methodology=m.methodology,
                        evidence_sources=m.evidence_sources,
                        notes_and_limitations=m.notes_and_limitations,
                        approximation_warning=warning,
                        task_similarity=similarity_score,
                    )
                )
            elif m.target_type == TargetType.CANONICAL:
                canonical_concept = self._canonical_occupations.get(m.target_occupation_id)
                if not canonical_concept:
                    continue
                if target_market and target_market.upper() not in ("CANONICAL", "INT"):
                    continue

                # Lexical similarity against canonical core competencies
                similarity_score = None
                if self._tfidf_model:
                    tok_s = normalize_tasks(source_occ.tasks)
                    tok_t = normalize_tasks(canonical_concept.core_competencies)
                    similarity_score = self._tfidf_model.cosine_similarity(tok_s, tok_t)

                matches.append(
                    CrossMarketMatchItem(
                        target_occupation=canonical_concept,
                        target_type=TargetType.CANONICAL,
                        target_market_id="INT",
                        relationship_type=m.relationship_type,
                        confidence_score=m.confidence_score,
                        review_status=m.review_status,
                        methodology=m.methodology,
                        evidence_sources=m.evidence_sources,
                        notes_and_limitations=m.notes_and_limitations,
                        approximation_warning=warning,
                        task_similarity=similarity_score,
                    )
                )

        # 5 Target Jurisdictions in JOBINTEL
        all_markets = ["IN", "US", "UK", "AU", "SG"]
        unmapped = [m for m in all_markets if m not in covered_markets]

        return CrossMarketComparisonResult(
            source_occupation=source_occ,
            matches=tuple(matches),
            unmapped_markets=tuple(unmapped),
            total_matches=len(matches),
        )

    # -------------------------------------------------------------
    # Coverage & Quality Statistics
    # -------------------------------------------------------------

    def get_coverage_stats(self) -> ConcordanceCoverageStats:
        national_occs = [o for o in self._national_occupations.values() if o.market_id != "INT"]
        intl_occs = [o for o in self._national_occupations.values() if o.market_id == "INT"]

        all_mappings = [m for m_list in self._mappings_by_source.values() for m in m_list]

        source_ids = {m.source_occupation_id for m in all_mappings}
        target_nat_ids = {m.target_occupation_id for m in all_mappings if m.target_type == TargetType.NATIONAL}
        all_mapped_occ_ids = source_ids.union(target_nat_ids)

        mapped_nat = sum(1 for o in national_occs if o.occupation_id in all_mapped_occ_ids)
        unmapped_nat = max(0, len(national_occs) - mapped_nat)

        mapped_intl = sum(1 for o in intl_occs if o.occupation_id in all_mapped_occ_ids)
        unmapped_intl = max(0, len(intl_occs) - mapped_intl)

        total_canonical = len(self._canonical_occupations)
        linked_canonical_ids = {m.target_occupation_id for m in all_mappings if m.target_type == TargetType.CANONICAL}
        linked_canonical = len(linked_canonical_ids)
        unlinked_canonical = max(0, total_canonical - linked_canonical)

        from collections import Counter
        rel_counts = dict(Counter(m.relationship_type.value for m in all_mappings))
        status_counts = dict(Counter(m.review_status.value for m in all_mappings))

        official_count = sum(1 for m in all_mappings if m.review_status == ReviewStatus.VERIFIED_OFFICIAL)
        expert_count = len(all_mappings) - official_count

        return ConcordanceCoverageStats(
            total_national_occupations=len(national_occs),
            mapped_national_occupations=mapped_nat,
            unmapped_national_occupations=unmapped_nat,
            total_international_references=len(intl_occs),
            mapped_international_references=mapped_intl,
            unmapped_international_references=unmapped_intl,
            total_catalog_occupations=len(self._national_occupations),
            total_canonical_concepts=total_canonical,
            linked_canonical_concepts=linked_canonical,
            unlinked_canonical_concepts=unlinked_canonical,
            mappings_by_relationship=rel_counts,
            mappings_by_review_status=status_counts,
            official_mappings_count=official_count,
            expert_reviewed_mappings_count=expert_count,
            total_mappings=len(all_mappings),
        )

    def compute_task_similarity(self, source_id: str, target_id: str) -> TaskSimilarityPayload:
        source_occ = self.get_occupation(source_id)
        target_occ = self.get_occupation(target_id)

        tok_s = normalize_tasks(source_occ.tasks)
        tok_t = normalize_tasks(target_occ.tasks)

        jaccard = calculate_jaccard_similarity(tok_s, tok_t)
        tfidf_cos = self._tfidf_model.cosine_similarity(tok_s, tok_t) if self._tfidf_model else 0.0

        return TaskSimilarityPayload(
            source_id=source_occ.occupation_id,
            target_id=target_occ.occupation_id,
            source_title=source_occ.occupation_title,
            target_title=target_occ.occupation_title,
            source_task_count=len(source_occ.tasks),
            target_task_count=len(target_occ.tasks),
            jaccard_similarity=jaccard,
            tfidf_cosine_similarity=tfidf_cos,
        )


_DEFAULT_SERVICE: OccupationService | None = None


def get_occupation_service() -> OccupationService:
    global _DEFAULT_SERVICE
    if _DEFAULT_SERVICE is None:
        _DEFAULT_SERVICE = OccupationService()
    return _DEFAULT_SERVICE
