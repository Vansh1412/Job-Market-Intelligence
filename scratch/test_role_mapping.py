"""
Prototype and validate deterministic role classification.
"""
import pandas as pd
import re

DATA_PATH = "data/raw/india/indian-job-market-dataset-2025.xlsx"
df = pd.read_excel(DATA_PATH)

def classify_role(title_raw, tags_raw=""):
    title = str(title_raw).lower().strip()
    tags = str(tags_raw).lower().strip() if pd.notnull(tags_raw) else ""
    
    # 1. AI / ML Engineer (Check before general Data Scientist / Software)
    if re.search(r'\b(ai\s*/\s*ml|machine\s*learning|deep\s*learning|nlp|computer\s*vision|llm|generative\s*ai|genai|artificial\s*intelligence|mlops|prompt\s*engineer)\b', title):
        return "AI / ML Engineer", True
        
    # 2. Data Scientist
    if re.search(r'\b(data\s*scientist|lead\s*data\s*scientist|principal\s*data\s*scientist|applied\s*scientist|research\s*scientist)\b', title):
        return "Data Scientist", True

    # 3. Data Engineer
    if re.search(r'\b(data\s*engineer|big\s*data|etl\s*developer|data\s*pipeline|pyspark\s*developer|databricks|snowflake\s*developer|data\s*warehouse|dwh)\b', title):
        return "Data Engineer", True

    # 4. Data Analyst (distinguish from business analyst)
    if re.search(r'\b(data\s*analyst|analytics\s*consultant|reporting\s*analyst|bi\s*analyst|business\s*intelligence\s*analyst|tableau\s*analyst|power\s*bi\s*analyst|quantitative\s*analyst)\b', title):
        return "Data Analyst", True

    # 5. Business Analyst
    if re.search(r'\b(business\s*analyst|ba\b|functional\s*analyst|it\s*business\s*analyst|product\s*analyst|systems\s*analyst|system\s*analyst)\b', title):
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

    # 13. Backend / Software Development Engineer
    # Include Application Developer, Application Lead, Java Developer, Python Developer, Software Engineer, C++ Developer, etc.
    if re.search(r'\b(backend|back\s*end|software\s*engineer|software\s*developer|sde\b|application\s*developer|application\s*lead|developer\s*-\s*l[1-3]|software\s*development|java\s*developer|python\s*developer|\.net\s*developer|c#\s*developer|c\+\+\s*developer|php\s*developer|golang\s*developer|ruby\s*developer|android\s*developer|ios\s*developer|mobile\s*developer|systems\s*engineer|technical\s*lead|tech\s*lead|solutions?\s*architect|enterprise\s*architect)\b', title):
        return "Software Engineer", True

    # 14. Other Technology (SAP, ERP, IT Support, Network Engineer, Salesforce, etc.)
    if re.search(r'\b(sap\b|salesforce|erp\b|it\s*support|application\s*support|technical\s*support|network\s*engineer|sysadmin|systems?\s*administrator|it\s*executive|hardware\s*engineer|telecom\s*engineer|embedded\s*engineer|firmware)\b', title):
        return "Other Technology", True

    # Contextual check: if title has "engineer" or "developer" or "programmer"
    if re.search(r'\b(engineer|developer|programmer|architect)\b', title):
        # Exclude civil/mechanical/chemical/electrical site engineers if clearly non-tech
        if re.search(r'\b(civil|mechanical|site|construction|structural|chemical|electrical|hvac|piping)\b', title):
            return "Non-Tech", False
        return "Other Technology", True

    # If title wasn't caught, check if strong tech tags indicate it's tech
    # But for analytical role grouping, default to Non-Tech
    return "Non-Tech", False

roles = []
is_tech = []
for t, s in zip(df["title"], df["tagsAndSkills"]):
    r, it = classify_role(t, s)
    roles.append(r)
    is_tech.append(it)

df["role_category"] = roles
df["is_tech_role"] = is_tech

print("--- FULL CORPUS ROLE BREAKDOWN ---")
print(df["role_category"].value_counts())
print(f"\nTech count: {sum(is_tech):,} ({sum(is_tech)/len(df)*100:.2f}%)")
print(f"Non-Tech count: {len(df)-sum(is_tech):,} ({(len(df)-sum(is_tech))/len(df)*100:.2f}%)")

# Within disclosed INR salary cohort
min_sal = pd.to_numeric(df["minimumSalary"], errors="coerce")
max_sal = pd.to_numeric(df["maximumSalary"], errors="coerce")
sal_mask = (df["currency"] == "INR") & min_sal.notnull() & max_sal.notnull() & (min_sal > 0) & (max_sal >= min_sal)
sal_df = df[sal_mask]

print("\n--- SALARY-DISCLOSED INR COHORT ROLE BREAKDOWN (N = " f"{len(sal_df):,}) ---")
print(sal_df["role_category"].value_counts())
tech_sal_count = sal_df["is_tech_role"].sum()
print(f"\nTech in salary cohort: {tech_sal_count:,} ({tech_sal_count/len(sal_df)*100:.2f}%)")
print(f"Non-Tech in salary cohort: {len(sal_df)-tech_sal_count:,} ({(len(sal_df)-tech_sal_count)/len(sal_df)*100:.2f}%)")
