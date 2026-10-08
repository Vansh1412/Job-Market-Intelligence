-- sql/india/top_skills_by_role.sql
-- Most demanded normalized skills grouped by standardized role category.
-- Joins normalized job_skills bridge table with job_postings.

SELECT
    jp.role_category,
    js.skill,
    COUNT(*) AS demand_count
FROM job_skills js
JOIN job_postings jp ON js.job_id = jp.job_id
GROUP BY jp.role_category, js.skill
ORDER BY jp.role_category, demand_count DESC;
