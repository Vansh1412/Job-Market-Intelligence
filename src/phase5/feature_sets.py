"""
Phase 5: Feature Set Construction (A, B, C)
===========================================
INT234 Predictive Analytics — Job Market Intelligence

Constructs the three mandatory comparative feature sets:
- Feature Set A: Original explicit metadata + 82 binary skills
- Feature Set B: Original explicit metadata + 15 fold-safe PCA components
- Feature Set C: Original explicit metadata + 82 binary skills + 7 fold-safe Archetype one-hot indicators
"""

import numpy as np
import pandas as pd
from src.phase5.preprocessing import (
    MetadataTransformer,
    FoldSafeSkillPCA,
    FoldSafeArchetypeTransformer,
)


class FeatureSetBuilder:
    """
    Builds Feature Sets A, B, and C with strict training-partition fitting.
    Guarantees zero data leakage across folds.
    """
    def __init__(self, metadata_cols, tech_skills):
        self.metadata_cols = metadata_cols
        self.tech_skills = tech_skills

    def build_feature_set_A(self, X_train, X_val=None):
        """
        Feature Set A: Original Explicit Features
        - Metadata (One-Hot seniority, role_family, city_clean + is_remote, num_skills)
        - 82 binary technical skill indicators
        """
        meta_transformer = MetadataTransformer().fit(X_train[self.metadata_cols])
        meta_train = meta_transformer.transform(X_train[self.metadata_cols])

        skills_train = X_train[self.tech_skills].values.astype(np.float32)
        X_train_A = np.hstack([meta_train, skills_train])

        feature_names = meta_transformer.get_feature_names_out() + self.tech_skills

        if X_val is not None:
            meta_val = meta_transformer.transform(X_val[self.metadata_cols])
            skills_val = X_val[self.tech_skills].values.astype(np.float32)
            X_val_A = np.hstack([meta_val, skills_val])
            return X_train_A, X_val_A, feature_names, meta_transformer

        return X_train_A, feature_names, meta_transformer

    def build_feature_set_B(self, X_train, X_val=None):
        """
        Feature Set B: PCA Dimensionality Reduction
        - Metadata (One-Hot seniority, role_family, city_clean + is_remote, num_skills)
        - 15 Continuous Principal Components fitted STRICTLY on X_train[tech_skills]
        """
        meta_transformer = MetadataTransformer().fit(X_train[self.metadata_cols])
        meta_train = meta_transformer.transform(X_train[self.metadata_cols])

        pca_transformer = FoldSafeSkillPCA().fit(X_train[self.tech_skills])
        pca_train = pca_transformer.transform(X_train[self.tech_skills])

        X_train_B = np.hstack([meta_train, pca_train])
        feature_names = meta_transformer.get_feature_names_out() + pca_transformer.get_feature_names_out()

        if X_val is not None:
            meta_val = meta_transformer.transform(X_val[self.metadata_cols])
            pca_val = pca_transformer.transform(X_val[self.tech_skills])
            X_val_B = np.hstack([meta_val, pca_val])
            return X_train_B, X_val_B, feature_names, (meta_transformer, pca_transformer)

        return X_train_B, feature_names, (meta_transformer, pca_transformer)

    def build_feature_set_C(self, X_train, X_val=None):
        """
        Feature Set C: Archetype-Augmented Feature Set
        - Full Feature Set A (Metadata + 82 binary skills)
        - 7 One-Hot Archetype Indicators generated via fold-fitted PCA and K-Means(k=7)
        """
        meta_transformer = MetadataTransformer().fit(X_train[self.metadata_cols])
        meta_train = meta_transformer.transform(X_train[self.metadata_cols])

        skills_train = X_train[self.tech_skills].values.astype(np.float32)

        # Fit PCA and K-Means strictly on training partition
        pca_transformer = FoldSafeSkillPCA().fit(skills_train)
        pca_train = pca_transformer.transform(skills_train)

        kmeans_transformer = FoldSafeArchetypeTransformer().fit(pca_train)
        archetypes_train = kmeans_transformer.transform(pca_train)

        X_train_C = np.hstack([meta_train, skills_train, archetypes_train])
        feature_names = (
            meta_transformer.get_feature_names_out()
            + self.tech_skills
            + kmeans_transformer.get_feature_names_out()
        )

        transformers = (meta_transformer, pca_transformer, kmeans_transformer)

        if X_val is not None:
            meta_val = meta_transformer.transform(X_val[self.metadata_cols])
            skills_val = X_val[self.tech_skills].values.astype(np.float32)
            pca_val = pca_transformer.transform(skills_val)
            archetypes_val = kmeans_transformer.transform(pca_val)

            X_val_C = np.hstack([meta_val, skills_val, archetypes_val])
            return X_train_C, X_val_C, feature_names, transformers

        return X_train_C, feature_names, transformers
