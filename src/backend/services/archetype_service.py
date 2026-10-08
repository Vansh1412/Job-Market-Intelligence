"""
JobIntel Archetype Inference Service
====================================
Production service executing real-time archetype classification for USA and India.
Consumes frozen PCA and K-Means artifacts via ModelRegistry.
Guarantees zero-skill fallback handling and verified Hungarian cluster-to-archetype mapping.
"""

from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd

from src.backend.models.model_registry import get_model_registry

# -----------------------------------------------------------------------------
# USA FROZEN ARCHETYPE TAXONOMY (k=7)
# -----------------------------------------------------------------------------
USA_ARCHETYPE_LOOKUP = {
    0: {
        "archetype_id": "USA_ARC_0",
        "code": "FOUND_TECH",
        "name": "Foundational & Broad Technical Roles",
        "definition": "A heterogeneous residual cluster dominated by low-skill-count postings and foundational IT/software roles.",
        "color": "#F97316",
        "typical_mae": 37194.0,
        "rel_error": 22.16,
        "typical_salary": 167850.0,
        "key_skills": ["SQL", "Python", "Java", "Linux", "Git"],
    },
    1: {
        "archetype_id": "USA_ARC_1",
        "code": "DEVOPS_PLAT",
        "name": "DevOps & Cloud Infrastructure Engineering",
        "definition": "Specialized platform, container orchestration, and CI/CD infrastructure roles.",
        "color": "#06B6D4",
        "typical_mae": 37887.0,
        "rel_error": 19.38,
        "typical_salary": 195500.0,
        "key_skills": ["Kubernetes", "Docker", "Terraform", "AWS", "CI/CD"],
    },
    2: {
        "archetype_id": "USA_ARC_2",
        "code": "WEB_FRONT",
        "name": "Frontend & Modern Web Application Engineering",
        "definition": "Client-side interfaces, responsive frameworks, and full-stack web application development.",
        "color": "#EC4899",
        "typical_mae": 33932.0,
        "rel_error": 20.20,
        "typical_salary": 168000.0,
        "key_skills": ["React", "TypeScript", "JavaScript", "HTML/CSS", "Next.js"],
    },
    3: {
        "archetype_id": "USA_ARC_3",
        "code": "CLOUD_ARCH",
        "name": "Multi-Cloud & Enterprise Cloud Architecture",
        "definition": "Enterprise cloud engineering across AWS, Azure, and distributed architectures.",
        "color": "#14B8A6",
        "typical_mae": 46098.0,
        "rel_error": 20.69,
        "typical_salary": 222800.0,
        "key_skills": ["AWS", "Azure", "Cloud Architecture", "GCP", "Security"],
    },
    4: {
        "archetype_id": "USA_ARC_4",
        "code": "DATA_BI",
        "name": "Data Engineering & Business Analytics",
        "definition": "Data warehousing, ETL pipelines, SQL analytics, and BI reporting systems.",
        "color": "#F59E0B",
        "typical_mae": 36142.0,
        "rel_error": 21.65,
        "typical_salary": 166900.0,
        "key_skills": ["SQL", "Snowflake", "dbt", "Airflow", "Tableau"],
    },
    5: {
        "archetype_id": "USA_ARC_5",
        "code": "AI_ML",
        "name": "AI / Machine Learning & LLM Engineering",
        "definition": "Deep learning, predictive modeling, NLP, and modern generative AI frameworks.",
        "color": "#8B5CF6",
        "typical_mae": 27002.0,
        "rel_error": 14.42,
        "typical_salary": 187250.0,
        "key_skills": ["PyTorch", "TensorFlow", "Python", "LLMs", "Scikit-Learn"],
    },
    6: {
        "archetype_id": "USA_ARC_6",
        "code": "SYS_ENG",
        "name": "Systems & Core Backend Engineering",
        "definition": "Low-level systems programming, embedded firmware, Linux kernel, and C/C++ backend engines.",
        "color": "#10B981",
        "typical_mae": 34850.0,
        "rel_error": 20.37,
        "typical_salary": 171100.0,
        "key_skills": ["C++", "C", "Linux", "Rust", "Embedded Systems"],
    },
}

# -----------------------------------------------------------------------------
# INDIA FROZEN ARCHETYPE TAXONOMY (k=6)
# Verified mapping from K-Means cluster index to salary-ranked archetype ID
# -----------------------------------------------------------------------------
INDIA_CLUSTER_TO_ARCHETYPE_ID = {
    4: "IND_ARC_01",
    2: "IND_ARC_02",
    3: "IND_ARC_03",
    5: "IND_ARC_04",
    0: "IND_ARC_05",
    1: "IND_ARC_06",
}

INDIA_ARCHETYPE_LOOKUP = {
    "IND_ARC_01": {
        "archetype_id": "IND_ARC_01",
        "raw_cluster_id": 4,
        "rank": 1,
        "name": "Big Data Engineering & Distributed Systems",
        "definition": "Distributed big data pipelines, large-scale data processing frameworks (Spark, Hadoop, Hive), and workflow orchestration (Airflow, Scala).",
        "color": "#1f77b4",  # Steel Blue
        "cohort_size": 198,
        "share_pct": 3.72,
        "median_salary_lpa": 20.0,
        "typical_mae_lpa": 1.60,
        "typical_rmse_lpa": 2.55,
        "relative_mae_pct": 7.99,
        "median_absolute_error_lpa": 0.84,
        "key_skills": ["Spark (99%)", "Scala (93%)", "Hadoop (81%)", "Python (64%)", "Airflow (59%)"],
    },
    "IND_ARC_02": {
        "archetype_id": "IND_ARC_02",
        "raw_cluster_id": 2,
        "rank": 2,
        "name": "Enterprise Java & Microservices Backend",
        "definition": "Enterprise backend architecture, Java ecosystems, Spring Boot microservices, and distributed service design, frequently extending to enterprise full-stack interfaces.",
        "color": "#ff7f0e",  # Amber Orange
        "cohort_size": 446,
        "share_pct": 8.38,
        "median_salary_lpa": 18.75,
        "typical_mae_lpa": 3.87,
        "typical_rmse_lpa": 5.81,
        "relative_mae_pct": 20.62,
        "median_absolute_error_lpa": 2.40,
        "key_skills": ["Java (94%)", "Spring Boot (85%)", "Microservices (70%)", "Hibernate (34%)", "SQL (32%)"],
    },
    "IND_ARC_03": {
        "archetype_id": "IND_ARC_03",
        "raw_cluster_id": 3,
        "rank": 3,
        "name": "Python, Cloud Data & Applied AI/ML",
        "definition": "Python-centric stack for analytical computing, machine learning, modern API services (FastAPI/Flask/Django), cloud databases, and generative AI systems.",
        "color": "#2ca02c",  # Emerald Green
        "cohort_size": 481,
        "share_pct": 9.04,
        "median_salary_lpa": 17.0,
        "typical_mae_lpa": 3.80,
        "typical_rmse_lpa": 5.43,
        "relative_mae_pct": 25.35,
        "median_absolute_error_lpa": 2.71,
        "key_skills": ["Python (98%)", "AWS (55%)", "SQL (49%)", "Machine Learning (27%)", "Azure (25%)"],
    },
    "IND_ARC_04": {
        "archetype_id": "IND_ARC_04",
        "raw_cluster_id": 5,
        "rank": 4,
        "name": "Full-Stack & Modern Application Engineering",
        "definition": "End-to-end software application lifecycle, modern web technologies (React, JavaScript, .NET), and relational data persistence.",
        "color": "#d62728",  # Crimson Red
        "cohort_size": 547,
        "share_pct": 10.28,
        "median_salary_lpa": 13.0,
        "typical_mae_lpa": 5.22,
        "typical_rmse_lpa": 7.79,
        "relative_mae_pct": 37.31,
        "median_absolute_error_lpa": 3.93,
        "key_skills": ["React (75%)", "JavaScript (74%)", "Node.js (52%)", "HTML/CSS (42%)", ".NET (23%)"],
    },
    "IND_ARC_05": {
        "archetype_id": "IND_ARC_05",
        "raw_cluster_id": 0,
        "rank": 5,
        "name": "Baseline & General Technology Stack",
        "definition": "Broad, heterogeneous market stratum characterized by diverse baseline technology roles, IT support, QA testing, and low-density or cross-functional skill requirements.",
        "color": "#9467bd",  # Purple
        "cohort_size": 3526,
        "share_pct": 66.24,
        "median_salary_lpa": 7.5,
        "typical_mae_lpa": 3.55,
        "typical_rmse_lpa": 6.00,
        "relative_mae_pct": 47.28,
        "median_absolute_error_lpa": 1.92,
        "key_skills": ["SQL (25%)", "Manual Testing (18%)", "IT Support (15%)", "Excel (12%)", "Core Tech (10%)"],
    },
    "IND_ARC_06": {
        "archetype_id": "IND_ARC_06",
        "raw_cluster_id": 1,
        "rank": 6,
        "name": "Enterprise ERP & SAP Functional Solutions",
        "definition": "Enterprise resource planning postings concentrated in SAP modules (FICO, MM), implementation consulting, functional testing, and enterprise certification.",
        "color": "#8c564b",  # Wood Brown
        "cohort_size": 125,
        "share_pct": 2.35,
        "median_salary_lpa": 3.625,
        "typical_mae_lpa": 1.06,
        "typical_rmse_lpa": 2.95,
        "relative_mae_pct": 29.26,
        "median_absolute_error_lpa": 0.06,
        "key_skills": ["SAP (97%)", "SAP FICO (33%)", "ABAP (27%)", "ERP Systems (25%)", "Consulting (20%)"],
    },
}


class ArchetypeService:
    """
    Stateless service providing Archetype classification and taxonomic descriptions.
    """

    # -------------------------------------------------------------------------
    # USA ARCHETYPES
    # -------------------------------------------------------------------------
    @staticmethod
    def classify_usa_skills(skills_binary_row: np.ndarray, num_skills: int) -> Dict[str, Any]:
        """
        Classifies USA skills vector (1 x 82) into one of 7 archetypes.
        """
        if num_skills == 0 or np.sum(skills_binary_row) == 0:
            return {
                "archetype_id": "USA_ARC_UNASSIGNED",
                "code": "ZERO_SKILL",
                "name": "Archetype Unavailable (Zero Skills)",
                "definition": "The learned archetype taxonomy is defined for skill-bearing job postings. Add at least one technical skill to receive an archetype classification.",
                "color": "#64748B",
                "archetype_available": False,
                "typical_mae": 36380.64,
                "rel_error": 21.71,
                "cluster_id": -1,
            }

        registry = get_model_registry()
        scaler = registry.usa_archetype_scaler
        pca = registry.usa_archetype_pca
        kmeans = registry.usa_archetype_kmeans

        # Transform through frozen USA archetype pipeline
        scaled = scaler.transform(skills_binary_row)
        pca_coords = pca.transform(scaled)
        cluster_id = int(kmeans.predict(pca_coords)[0])

        arc_info = USA_ARCHETYPE_LOOKUP.get(cluster_id, USA_ARCHETYPE_LOOKUP[0]).copy()
        arc_info["archetype_available"] = True
        arc_info["cluster_id"] = cluster_id
        arc_info["pca_coordinates"] = [round(float(c), 4) for c in pca_coords[0][:3]]

        return arc_info

    @staticmethod
    def get_usa_archetypes() -> List[Dict[str, Any]]:
        """Return all 7 USA archetypes with full empirical profile details."""
        return list(USA_ARCHETYPE_LOOKUP.values())

    # -------------------------------------------------------------------------
    # INDIA ARCHETYPES
    # -------------------------------------------------------------------------
    @staticmethod
    def classify_india_skills(skills_binary_row: np.ndarray, num_skills: int) -> Dict[str, Any]:
        """
        Classifies India skills vector (1 x 284) into one of 6 archetypes.
        """
        if num_skills == 0 or np.sum(skills_binary_row) == 0:
            return {
                "archetype_id": "IND_ARC_UNASSIGNED",
                "code": "ZERO_SKILL",
                "name": "Archetype Unavailable (Zero Skills)",
                "definition": "The learned archetype taxonomy is defined for skill-bearing job postings. Add at least one technical skill to receive an archetype classification.",
                "color": "#64748B",
                "archetype_available": False,
                "typical_mae_lpa": 3.71,
                "typical_mae": 371472.0,
                "relative_mae_pct": 37.1,
                "cluster_id": -1,
                "rank": None,
            }

        registry = get_model_registry()
        pca = registry.india_archetype_pca
        kmeans = registry.india_archetype_kmeans

        # Project via frozen PCA (Centered Covariance PCA)
        pca_coords = pca.transform(skills_binary_row)
        raw_cluster_idx = int(kmeans.predict(pca_coords)[0])

        # Map via verified Hungarian assignment
        archetype_id = INDIA_CLUSTER_TO_ARCHETYPE_ID.get(raw_cluster_idx, "IND_ARC_05")
        arc_info = INDIA_ARCHETYPE_LOOKUP.get(archetype_id, INDIA_ARCHETYPE_LOOKUP["IND_ARC_05"]).copy()

        arc_info["archetype_available"] = True
        arc_info["cluster_id"] = raw_cluster_idx
        arc_info["pca_coordinates"] = [round(float(c), 4) for c in pca_coords[0][:3]]
        # Convert LPA MAE to INR for consistent currency fields
        arc_info["typical_mae"] = arc_info["typical_mae_lpa"] * 100000.0

        return arc_info

    @staticmethod
    def get_india_archetypes() -> List[Dict[str, Any]]:
        """Return all 6 India archetypes ordered by salary rank (1 to 6)."""
        return sorted(list(INDIA_ARCHETYPE_LOOKUP.values()), key=lambda x: x["rank"])
