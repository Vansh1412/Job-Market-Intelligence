from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Sequence

# Standard English stop words commonly found in occupational task definitions
STOP_WORDS = frozenset({
    "a", "about", "above", "across", "after", "again", "against", "all", "almost", "along",
    "also", "although", "always", "am", "among", "an", "and", "another", "any", "are", "as",
    "at", "be", "because", "been", "before", "being", "between", "both", "but", "by", "can",
    "could", "did", "do", "does", "doing", "down", "during", "each", "either", "enough", "etc",
    "even", "every", "for", "from", "further", "had", "has", "have", "having", "he", "her",
    "here", "hers", "herself", "him", "himself", "his", "how", "if", "in", "into", "is", "it",
    "its", "itself", "just", "may", "me", "might", "more", "most", "must", "my", "myself", "no",
    "nor", "not", "of", "off", "on", "once", "only", "or", "other", "our", "ours", "ourselves",
    "out", "over", "own", "same", "she", "should", "so", "some", "such", "than", "that", "the",
    "their", "theirs", "them", "themselves", "then", "there", "these", "they", "this", "those",
    "through", "to", "too", "under", "until", "up", "very", "was", "we", "were", "what", "when",
    "where", "which", "while", "who", "whom", "why", "will", "with", "would", "you", "your",
    "yours", "yourself", "yourselves"
})


def normalize_text_to_tokens(text: str) -> list[str]:
    """Tokenizes, lowercases, strips punctuation, and removes common stop words."""
    cleaned = re.sub(r"[^\w\s]", " ", text.lower())
    tokens = [t for t in cleaned.split() if len(t) > 2 and t not in STOP_WORDS]
    return tokens


def normalize_tasks(tasks: Sequence[str]) -> list[str]:
    """Normalizes an entire sequence of task descriptions into a combined token list."""
    combined = " ".join(tasks)
    return normalize_text_to_tokens(combined)


def calculate_jaccard_similarity(tokens_a: Sequence[str], tokens_b: Sequence[str]) -> float:
    """Calculates Jaccard similarity coefficient between two token sequences: |A ∩ B| / |A ∪ B|."""
    set_a = set(tokens_a)
    set_b = set(tokens_b)
    if not set_a and not set_b:
        return 1.0
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    return round(intersection / union, 4)


class TfidfModel:
    """Lightweight, deterministic TF-IDF model built with Python standard library."""

    def __init__(self, corpus: Sequence[Sequence[str]]) -> None:
        self.doc_count = len(corpus)
        self.df: Counter[str] = Counter()
        for doc in corpus:
            unique_terms = set(doc)
            for term in unique_terms:
                self.df[term] += 1
        # Inverse document frequency with smoothing: log((1 + N) / (1 + df)) + 1
        self.idf: dict[str, float] = {}
        for term, freq in self.df.items():
            self.idf[term] = math.log((1 + self.doc_count) / (1 + freq)) + 1.0

    def vectorize(self, tokens: Sequence[str]) -> dict[str, float]:
        """Calculates normalized TF-IDF vector for a document."""
        if not tokens:
            return {}
        tf = Counter(tokens)
        doc_len = len(tokens)
        vector: dict[str, float] = {}
        for term, count in tf.items():
            idf_val = self.idf.get(term, math.log(1 + self.doc_count) + 1.0)
            vector[term] = (count / doc_len) * idf_val
        # L2 normalization
        norm = math.sqrt(sum(val * val for val in vector.values()))
        if norm > 0:
            for term in vector:
                vector[term] = vector[term] / norm
        return vector

    def cosine_similarity(self, tokens_a: Sequence[str], tokens_b: Sequence[str]) -> float:
        """Calculates cosine similarity between two documents' TF-IDF vectors."""
        vec_a = self.vectorize(tokens_a)
        vec_b = self.vectorize(tokens_b)
        if not vec_a or not vec_b:
            return 0.0
        # Dot product
        common_terms = set(vec_a.keys()).intersection(vec_b.keys())
        dot_product = sum(vec_a[t] * vec_b[t] for t in common_terms)
        return round(max(0.0, min(1.0, dot_product)), 4)


@dataclass(frozen=True)
class TaskSimilarityResult:
    source_id: str
    target_id: str
    source_task_count: int
    target_task_count: int
    jaccard_similarity: float
    tfidf_cosine_similarity: float
    metric_type: str = "UNSUPERVISED_LEXICAL_SIMILARITY"
    calibration_status: str = "UNEMPIRICAL_HEURISTIC_SEPARATE_METRIC"
    limitations: str = (
        "Unsupervised lexical overlap metric based on word frequencies. "
        "Does NOT constitute empirical probability or calibrated confidence of occupational interchangeability."
    )
