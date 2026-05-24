"""
TechCorp HR Analytics — Run SQL Queries
Author: Mehak Pandey | pandeymehak.217@gmail.com
"""
import duckdb, pandas as pd

BASE = '/Users/mehekpandey/hr_project/data'
con  = duckdb.connect()
for t in ['departments','employees','performance','attrition','training','jira_sprints']:
    con.execute(f"CREATE TABLE {t} AS SELECT * FROM read_csv_auto('{BASE}/{t}.csv')")

queries = {
"1. Workforce by Department": """
    SELECT department, COUNT(*) AS headcount,
           ROUND(AVG(attrition)*100,2) AS att_rate,
           ROUND(AVG(annual_salary)/100000,2) AS avg_sal_lakh,
           ROUND(AVG(job_satisfaction),2) AS avg_satisfaction
    FROM employees GROUP BY department ORDER BY headcount DESC
""",
"2. Attrition Reasons and Cost": """
    SELECT primary_reason, COUNT(*) AS attritions,
           ROUND(SUM(replacement_cost_lakh),1) AS total_cost_lakh,
           RANK() OVER (ORDER BY COUNT(*) DESC) AS rank
    FROM attrition GROUP BY primary_reason ORDER BY attritions DESC
""",
"3. Sprint Velocity by Department": """
    SELECT department, sprint_year,
           ROUND(AVG(velocity),1) AS avg_velocity,
           ROUND(AVG(completion_rate),1) AS avg_completion
    FROM jira_sprints WHERE sprint_status='Completed'
    GROUP BY department, sprint_year ORDER BY department, sprint_year
""",
"4. Training ROI": """
    SELECT training_type,
           ROUND(AVG(score),1) AS avg_score,
           ROUND(COUNT(CASE WHEN completion_status='Completed' THEN 1 END)*100.0/COUNT(*),1) AS comp_rate,
           ROUND(AVG(cost_per_person),0) AS avg_cost,
           COUNT(*) AS sessions
    FROM training GROUP BY training_type ORDER BY comp_rate DESC
""",
"5. HR KPI Summary": """
    SELECT COUNT(*) AS total_emp,
           COUNT(CASE WHEN attrition=0 THEN 1 END) AS active,
           ROUND(AVG(attrition)*100,2) AS att_rate_pct,
           ROUND(AVG(annual_salary)/100000,2) AS avg_sal_lakh,
           ROUND(AVG(performance_rating),2) AS avg_perf,
           (SELECT ROUND(SUM(replacement_cost_lakh),1) FROM attrition) AS total_att_cost_lakh
    FROM employees
""",
}

print("="*60)
print("  TechCorp HR Analytics — SQL Results")
print("  Author: Mehak Pandey | pandeymehak.217@gmail.com")
print("="*60)
for name, sql in queries.items():
    print(f"\n{'─'*60}\n  {name}\n{'─'*60}")
    print(con.execute(sql).df().to_string(index=False))
print("\n" + "="*60)
print("  All queries passed.")
print("="*60)
con.close()
