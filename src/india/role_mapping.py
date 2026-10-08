"""
Deterministic Role Classification & Tech Classification Module for JobIntel India.
Provides auditable, ordered regular expression matching from job titles to standardized role families.
"""

import re
import pandas as pd
from typing import Tuple

# Candidate standard role families
ROLE_FAMILIES = [
    "AI / ML Engineer",
    "Data Scientist",
    "Data Engineer",
    "Data Analyst",
    "Business Analyst",
    "Database Administrator",
    "Cloud / DevOps",
    "Cybersecurity",
    "Full Stack Developer",
    "Frontend Developer",
    "QA / Testing",
    "Product / Program Manager",
    "Software Engineer",
    "Other Technology",
    "Non-Tech"
]

def classify_role(title_raw: str, tags_raw: str = "") -> Tuple[str, bool]:
    """
    Classifies a raw job title into a deterministic role family and tech indicator.
    
    Returns:
        (normalized_role, is_tech_role)
    """
    if pd.isnull(title_raw):
        return "Non-Tech", False
        
    title = str(title_raw).lower().strip()
    
    # 1. AI / ML Engineer (Highest precedence within AI/Data)
    if re.search(r'\b(ai\s*/\s*ml|machine\s*learning|deep\s*learning|nlp|computer\s*vision|llm|generative\s*ai|genai|artificial\s*intelligence|mlops|prompt\s*engineer)\b', title):
        return "AI / ML Engineer", True
        
    # 2. Data Scientist
    if re.search(r'\b(data\s*scientist|lead\s*data\s*scientist|principal\s*data\s*scientist|applied\s*scientist|research\s*scientist)\b', title):
        return "Data Scientist", True

    # 3. Data Engineer
    if re.search(r'\b(data\s*engineer|big\s*data|etl\s*developer|data\s*pipeline|pyspark\s*developer|databricks|snowflake\s*developer|data\s*warehouse|dwh)\b', title):
        return "Data Engineer", True

    # 4. Data Analyst (Distinguished from Business Analyst)
    if re.search(r'\b(data\s*analyst|analytics\s*consultant|reporting\s*analyst|bi\s*analyst|business\s*intelligence\s*analyst|tableau\s*analyst|power\s*bi\s*analyst|quantitative\s*analyst)\b', title):
        return "Data Analyst", True

    # 5. Business Analyst
    if re.search(r'\b(business\s*analyst|functional\s*analyst|it\s*business\s*analyst|product\s*analyst|systems\s*analyst|system\s*analyst)\b', title):
        return "Business Analyst", True

    # 6. Database Administrator / Engineer
    if re.search(r'\b(database\s*administrator|dba\b|sql\s*developer|database\s*engineer|database\s*developer|oracle\s*developer|pl/?sql)\b', title):
        return "Database Administrator", True

    # 7. Cloud / DevOps Engineer
    if re.search(r'\b(devops|cloud\s*engineer|site\s*reliability|sre\b|aws\s*engineer|azure\s*engineer|cloud\s*architect|infrastructure\s*engineer|platform\s*engineer|kubernetes\s*engineer|cloud\s*administrator)\b', title):
        return "Cloud / DevOps", True

    # 8. Cybersecurity / InfoSec
    if re.search(r'\b(cyber\s*security|information\s*security|infosec|security\s*engineer|soc\s*analyst|penetration\s*tester|security\s*architect|network\s*security)\b', title):
        return "Cybersecurity", True

    # 9. Full Stack Developer
    if re.search(r'\b(full\s*stack|fullstack|mean\s*stack|mern\s*stack)\b', title):
        return "Full Stack Developer", True

    # 10. Frontend / Web Developer
    if re.search(r'\b(frontend|front\s*end|ui\s*/\s*ux\s*developer|ui\s*developer|web\s*developer|react\s*developer|angular\s*developer|vue\s*developer|javascript\s*developer)\b', title):
        return "Frontend Developer", True

    # 11. QA / Test Engineer
    if re.search(r'\b(qa\b|quality\s*assurance|tester|test\s*engineer|sdet|automation\s*test|software\s*testing|testing\s*engineer|manual\s*tester)\b', title):
        return "QA / Testing", True

    # 12. Product / Technical Program Manager
    if re.search(r'\b(product\s*manager|product\s*owner|technical\s*program\s*manager|tpm\b|scrum\s*master|agile\s*coach)\b', title):
        return "Product / Program Manager", True

    # 13. Software Engineer (Backend, Core Development, Application Developer, Leads)
    if re.search(r'\b(backend|back\s*end|software\s*engineer|software\s*developer|sde\b|application\s*developer|application\s*lead|developer\s*-\s*l[1-3]|software\s*development|java\s*developer|python\s*developer|\.net\s*developer|c#\s*developer|c\+\+\s*developer|php\s*developer|golang\s*developer|ruby\s*developer|android\s*developer|ios\s*developer|mobile\s*developer|systems\s*engineer|technical\s*lead|tech\s*lead|solutions?\s*architect|enterprise\s*architect)\b', title):
        return "Software Engineer", True

    # 14. Other Technology (SAP, ERP, IT Support, Network Engineer, Salesforce, etc.)
    if re.search(r'\b(sap\b|salesforce|erp\b|it\s*support|application\s*support|technical\s*support|network\s*engineer|sysadmin|systems?\s*administrator|it\s*executive|hardware\s*engineer|telecom\s*engineer|embedded\s*engineer|firmware)\b', title):
        return "Other Technology", True

    # Broad contextual check: check for generic engineer / developer / programmer
    if re.search(r'\b(engineer|developer|programmer|architect)\b', title):
        # Exclude non-tech engineering
        if re.search(r'\b(civil|mechanical|site|construction|structural|chemical|electrical|hvac|piping|automobile|production)\b', title):
            return "Non-Tech", False
        return "Other Technology", True

    return "Non-Tech", False


def apply_role_classification(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies role classification to a dataframe containing 'title' and optional 'tagsAndSkills'.
    Adds 'normalized_role' and 'is_tech_role' columns.
    """
    roles = []
    is_tech = []
    tags_col = "tagsAndSkills" if "tagsAndSkills" in df.columns else None
    
    for idx, row in df.iterrows():
        t = row["title"]
        s = row[tags_col] if tags_col else ""
        role, tech = classify_role(t, s)
        roles.append(role)
        is_tech.append(tech)
        
    df["normalized_role"] = roles
    df["is_tech_role"] = is_tech
    return df
