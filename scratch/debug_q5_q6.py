"""
Debug Query 5 and Query 6 comparison between SQL and Pandas.
"""
import sqlite3
import pandas as pd
import numpy as np

postings_df = pd.read_parquet("data/processed/india/india_job_postings.parquet")
skills_df = pd.read_parquet("data/processed/india/india_job_skills.parquet")

conn = sqlite3.connect(":memory:")
postings_df.to_sql("job_postings", conn, index=False, if_exists="replace")
skills_df.to_sql("job_skills", conn, index=False, if_exists="replace")

# Query 5
with open("sql/india/salary_by_city_analyst.sql") as f:
    sql_q5 = pd.read_sql_query(f.read(), conn)

sal_analysts = postings_df[
    postings_df["salary_lpa"].notnull() &
    (postings_df["currency"] == "INR") &
    postings_df["role_category"].isin(["Data Analyst", "Business Analyst"])
]
py_q5 = sal_analysts.groupby("city")["salary_lpa"].agg(
    num_postings_with_salary="count",
    avg_salary_lpa="mean"
).reset_index()
py_q5 = py_q5[py_q5["num_postings_with_salary"] >= 3]
py_q5["avg_salary_lpa"] = py_q5["avg_salary_lpa"].round(2)
py_q5 = py_q5.sort_values("avg_salary_lpa", ascending=False).reset_index(drop=True)

print("--- QUERY 5 SQL ---")
print(sql_q5)
print("\n--- QUERY 5 PANDAS ---")
print(py_q5)

# Check differences in Q5
print("\nQ5 cities equal?", sql_q5["city"].tolist() == py_q5["city"].tolist())
print("Q5 num_postings equal?", sql_q5["num_postings_with_salary"].tolist() == py_q5["num_postings_with_salary"].tolist())
print("Q5 avg_salary_lpa equal?", np.allclose(sql_q5["avg_salary_lpa"], py_q5["avg_salary_lpa"]))

# Query 6
with open("sql/india/top_skills_by_role.sql") as f:
    sql_q6 = pd.read_sql_query(f.read(), conn)

joined = pd.merge(skills_df, postings_df[["job_id", "role_category"]], on="job_id", how="inner")
py_q6 = joined.groupby(["role_category", "skill"]).size().reset_index(name="demand_count")
py_q6 = py_q6.sort_values(["role_category", "demand_count"], ascending=[True, False]).reset_index(drop=True)

print("\n--- QUERY 6 SHAPES ---")
print("SQL Q6 shape:", sql_q6.shape)
print("Pandas Q6 shape:", py_q6.shape)
print("\nSQL Q6 head:")
print(sql_q6.head(10))
print("\nPandas Q6 head:")
print(py_q6.head(10))
