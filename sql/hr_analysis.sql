-- ================================================================
-- TechCorp HR Analytics — Attrition and Workforce Analysis
-- Author      : Mehak Pandey
-- Email       : pandeymehak.217@gmail.com
-- Tools       : SQL, Power BI, R
-- Dataset     : 6 tables | 2,000 employees | 2020-2024
-- Topics      : Attrition, Performance, Agile/Scrum,
--               Training ROI, Workforce Planning
-- ================================================================

-- ----------------------------------------------------------------
-- SECTION 1: WORKFORCE OVERVIEW
-- ----------------------------------------------------------------

-- 1.1 Headcount by department with salary stats
SELECT
    department,
    COUNT(*)                                    AS headcount,
    COUNT(CASE WHEN attrition=1 THEN 1 END)     AS left_count,
    ROUND(COUNT(CASE WHEN attrition=1 THEN 1 END)*100.0/COUNT(*),2) AS attrition_rate,
    ROUND(AVG(annual_salary)/100000,2)          AS avg_salary_lakh,
    ROUND(MIN(annual_salary)/100000,2)          AS min_salary_lakh,
    ROUND(MAX(annual_salary)/100000,2)          AS max_salary_lakh,
    ROUND(AVG(tenure_months),1)                 AS avg_tenure_months,
    ROUND(AVG(performance_rating),2)            AS avg_performance
FROM employees
GROUP BY department
ORDER BY headcount DESC;


-- 1.2 Gender diversity analysis by department
SELECT
    department,
    COUNT(*)                                                    AS total,
    COUNT(CASE WHEN gender='Male'   THEN 1 END)                AS male,
    COUNT(CASE WHEN gender='Female' THEN 1 END)                AS female,
    ROUND(COUNT(CASE WHEN gender='Female' THEN 1 END)*100.0/COUNT(*),1) AS female_pct,
    ROUND(AVG(CASE WHEN gender='Male'   THEN annual_salary END)/100000,2) AS avg_male_salary_lakh,
    ROUND(AVG(CASE WHEN gender='Female' THEN annual_salary END)/100000,2) AS avg_female_salary_lakh,
    -- Gender pay gap
    ROUND((AVG(CASE WHEN gender='Male' THEN annual_salary END)
          - AVG(CASE WHEN gender='Female' THEN annual_salary END))
          / AVG(annual_salary) * 100, 2)                       AS gender_pay_gap_pct
FROM employees
GROUP BY department
ORDER BY female_pct DESC;


-- 1.3 Age group distribution and attrition pattern
SELECT
    CASE
        WHEN age < 25 THEN 'Under 25'
        WHEN age < 30 THEN '25-29'
        WHEN age < 35 THEN '30-34'
        WHEN age < 40 THEN '35-39'
        WHEN age < 45 THEN '40-44'
        ELSE               '45+'
    END AS age_group,
    COUNT(*)                                                    AS employees,
    COUNT(CASE WHEN attrition=1 THEN 1 END)                    AS left_count,
    ROUND(COUNT(CASE WHEN attrition=1 THEN 1 END)*100.0/COUNT(*),2) AS attrition_rate,
    ROUND(AVG(annual_salary)/100000,2)                         AS avg_salary_lakh,
    ROUND(AVG(job_satisfaction),2)                             AS avg_satisfaction
FROM employees
GROUP BY 1
ORDER BY age_group;


-- ----------------------------------------------------------------
-- SECTION 2: ATTRITION ANALYSIS
-- ----------------------------------------------------------------

-- 2.1 Attrition reasons and financial impact
SELECT
    primary_reason,
    COUNT(*)                                        AS attritions,
    ROUND(COUNT(*)*100.0/SUM(COUNT(*)) OVER(),2)   AS pct_of_total,
    ROUND(AVG(annual_salary)/100000,2)             AS avg_salary_lakh,
    ROUND(AVG(tenure_months),1)                    AS avg_tenure_months,
    ROUND(SUM(replacement_cost_lakh),1)            AS total_replacement_cost_lakh,
    ROUND(AVG(replacement_cost_lakh),1)            AS avg_replacement_cost_lakh,
    RANK() OVER (ORDER BY COUNT(*) DESC)           AS reason_rank
FROM attrition
GROUP BY primary_reason
ORDER BY attritions DESC;


-- 2.2 Early attrition — employees who left within 12 months
-- This is the most expensive attrition type
WITH early_att AS (
    SELECT
        e.department,
        e.role,
        e.education,
        e.annual_salary,
        e.tenure_months,
        e.job_satisfaction,
        e.overtime_hours_weekly,
        a.primary_reason,
        a.replacement_cost_lakh,
        CASE WHEN e.tenure_months <= 6  THEN '0-6 months'
             WHEN e.tenure_months <= 12 THEN '7-12 months'
             WHEN e.tenure_months <= 24 THEN '13-24 months'
             ELSE '24+ months'
        END AS tenure_band
    FROM employees e
    JOIN attrition a ON e.emp_id = a.emp_id
)
SELECT
    tenure_band,
    COUNT(*)                                        AS attritions,
    ROUND(AVG(annual_salary)/100000,2)             AS avg_salary_lakh,
    ROUND(AVG(job_satisfaction),2)                 AS avg_satisfaction,
    ROUND(AVG(overtime_hours_weekly),1)            AS avg_overtime_hrs,
    ROUND(SUM(replacement_cost_lakh),1)            AS total_cost_lakh,
    ROUND(AVG(replacement_cost_lakh),1)            AS avg_cost_lakh
FROM early_att
GROUP BY tenure_band
ORDER BY tenure_band;


-- 2.3 Attrition risk scoring model
-- Predicts which employees are most likely to leave
SELECT
    emp_id,
    emp_name,
    department,
    role,
    annual_salary,
    tenure_months,
    job_satisfaction,
    work_life_balance,
    overtime_hours_weekly,
    distance_from_office,
    num_companies_worked,
    -- Risk score calculation (higher = more likely to leave)
    (CASE WHEN job_satisfaction     <= 2 THEN 25
          WHEN job_satisfaction     <= 3 THEN 10
          ELSE 0 END) +
    (CASE WHEN work_life_balance    <= 2 THEN 20
          WHEN work_life_balance    <= 3 THEN 8
          ELSE 0 END) +
    (CASE WHEN overtime_hours_weekly > 15 THEN 20
          WHEN overtime_hours_weekly > 10 THEN 10
          ELSE 0 END) +
    (CASE WHEN annual_salary < 600000     THEN 20
          WHEN annual_salary < 900000     THEN 10
          ELSE 0 END) +
    (CASE WHEN tenure_months < 12         THEN 15
          WHEN tenure_months < 24         THEN 8
          ELSE 0 END) +
    (CASE WHEN num_companies_worked > 5   THEN 10
          WHEN num_companies_worked > 3   THEN 5
          ELSE 0 END) +
    (CASE WHEN distance_from_office > 30  THEN 10
          ELSE 0 END)                                 AS attrition_risk_score,
    CASE
        WHEN (CASE WHEN job_satisfaction<=2 THEN 25 WHEN job_satisfaction<=3 THEN 10 ELSE 0 END +
              CASE WHEN work_life_balance<=2 THEN 20 WHEN work_life_balance<=3 THEN 8 ELSE 0 END +
              CASE WHEN overtime_hours_weekly>15 THEN 20 WHEN overtime_hours_weekly>10 THEN 10 ELSE 0 END +
              CASE WHEN annual_salary<600000 THEN 20 WHEN annual_salary<900000 THEN 10 ELSE 0 END +
              CASE WHEN tenure_months<12 THEN 15 WHEN tenure_months<24 THEN 8 ELSE 0 END +
              CASE WHEN num_companies_worked>5 THEN 10 WHEN num_companies_worked>3 THEN 5 ELSE 0 END +
              CASE WHEN distance_from_office>30 THEN 10 ELSE 0 END) >= 60 THEN 'High Risk'
        WHEN (CASE WHEN job_satisfaction<=2 THEN 25 WHEN job_satisfaction<=3 THEN 10 ELSE 0 END +
              CASE WHEN work_life_balance<=2 THEN 20 WHEN work_life_balance<=3 THEN 8 ELSE 0 END +
              CASE WHEN overtime_hours_weekly>15 THEN 20 WHEN overtime_hours_weekly>10 THEN 10 ELSE 0 END +
              CASE WHEN annual_salary<600000 THEN 20 WHEN annual_salary<900000 THEN 10 ELSE 0 END +
              CASE WHEN tenure_months<12 THEN 15 WHEN tenure_months<24 THEN 8 ELSE 0 END +
              CASE WHEN num_companies_worked>5 THEN 10 WHEN num_companies_worked>3 THEN 5 ELSE 0 END +
              CASE WHEN distance_from_office>30 THEN 10 ELSE 0 END) >= 35 THEN 'Medium Risk'
        ELSE 'Low Risk'
    END AS risk_label,
    attrition AS actually_left
FROM employees
WHERE attrition = 0
ORDER BY attrition_risk_score DESC
LIMIT 25;


-- 2.4 Year-wise attrition trend
SELECT
    EXTRACT(YEAR FROM CAST(left_date AS DATE)) AS attrition_year,
    department,
    COUNT(*)                                   AS attritions,
    ROUND(AVG(tenure_months),1)               AS avg_tenure,
    ROUND(AVG(annual_salary)/100000,2)        AS avg_salary_lakh,
    ROUND(SUM(replacement_cost_lakh),1)       AS total_replacement_cost,
    LAG(COUNT(*)) OVER (
        PARTITION BY department
        ORDER BY EXTRACT(YEAR FROM CAST(left_date AS DATE))
    ) AS prev_year_attritions,
    COUNT(*) - LAG(COUNT(*)) OVER (
        PARTITION BY department
        ORDER BY EXTRACT(YEAR FROM CAST(left_date AS DATE))
    ) AS yoy_change
FROM attrition
WHERE left_date IS NOT NULL
GROUP BY EXTRACT(YEAR FROM CAST(left_date AS DATE)), department
ORDER BY attrition_year, attritions DESC;


-- ----------------------------------------------------------------
-- SECTION 3: PERFORMANCE ANALYSIS
-- ----------------------------------------------------------------

-- 3.1 Performance distribution by department
SELECT
    department,
    COUNT(*)                                                     AS reviews,
    ROUND(AVG(kpi_score),2)                                     AS avg_kpi,
    ROUND(AVG(goal_completion_pct),1)                           AS avg_goal_completion,
    ROUND(AVG(manager_rating),2)                                AS avg_manager_rating,
    ROUND(AVG(increment_pct),2)                                 AS avg_increment_pct,
    COUNT(CASE WHEN promotion_flag=1 THEN 1 END)                AS promotions,
    ROUND(COUNT(CASE WHEN promotion_flag=1 THEN 1 END)*100.0
          /COUNT(*),2)                                          AS promotion_rate,
    RANK() OVER (ORDER BY AVG(kpi_score) DESC)                  AS performance_rank
FROM performance
GROUP BY department
ORDER BY avg_kpi DESC;


-- 3.2 High performers who are at attrition risk
-- The most critical segment for HR to retain
WITH high_perf AS (
    SELECT emp_id, AVG(kpi_score) AS avg_kpi,
           MAX(promotion_flag) AS ever_promoted
    FROM performance
    GROUP BY emp_id
    HAVING AVG(kpi_score) >= 4.0
),
risk_employees AS (
    SELECT e.emp_id, e.emp_name, e.department, e.role,
           e.annual_salary, e.job_satisfaction, e.tenure_months,
           e.overtime_hours_weekly, e.attrition,
           hp.avg_kpi, hp.ever_promoted
    FROM employees e
    JOIN high_perf hp ON e.emp_id = hp.emp_id
    WHERE e.job_satisfaction <= 3
      AND e.attrition = 0
)
SELECT *,
    RANK() OVER (ORDER BY avg_kpi DESC, annual_salary DESC) AS priority_rank
FROM risk_employees
ORDER BY priority_rank
LIMIT 20;


-- ----------------------------------------------------------------
-- SECTION 4: AGILE / SCRUM / JIRA METRICS
-- ----------------------------------------------------------------

-- 4.1 Sprint velocity trend by department
SELECT
    department,
    sprint_year,
    COUNT(*)                                    AS sprints_completed,
    ROUND(AVG(velocity),1)                     AS avg_velocity,
    ROUND(AVG(completion_rate),1)              AS avg_completion_rate,
    ROUND(AVG(bugs_found),1)                   AS avg_bugs_found,
    ROUND(AVG(bugs_fixed)/NULLIF(AVG(bugs_found),0)*100,1) AS bug_fix_rate,
    ROUND(AVG(retrospective_score),2)          AS avg_retro_score,
    ROUND(AVG(blocked_days),1)                 AS avg_blocked_days,
    -- Velocity trend
    LAG(ROUND(AVG(velocity),1)) OVER (
        PARTITION BY department ORDER BY sprint_year
    ) AS prev_year_velocity,
    ROUND(AVG(velocity) - LAG(AVG(velocity)) OVER (
        PARTITION BY department ORDER BY sprint_year
    ), 1) AS velocity_change
FROM jira_sprints
WHERE sprint_status = 'Completed'
GROUP BY department, sprint_year
ORDER BY department, sprint_year;


-- 4.2 Sprint health scorecard
-- Flags underperforming sprints
SELECT
    sprint_id,
    sprint_name,
    department,
    start_date,
    planned_points,
    completed_points,
    completion_rate,
    velocity,
    bugs_found,
    bugs_fixed,
    team_size,
    retrospective_score,
    blocked_days,
    -- Sprint health score
    CASE
        WHEN completion_rate >= 90
         AND bugs_found <= 5
         AND blocked_days <= 1  THEN 'Healthy'
        WHEN completion_rate >= 70
         AND bugs_found <= 10   THEN 'Moderate'
        ELSE                         'Needs Improvement'
    END AS sprint_health,
    -- Points per team member
    ROUND(completed_points / NULLIF(team_size,0), 1) AS points_per_member
FROM jira_sprints
WHERE sprint_status = 'Completed'
ORDER BY completion_rate DESC;


-- 4.3 Team productivity: sprint points vs attrition impact
WITH dept_attrition AS (
    SELECT department,
           COUNT(*) AS attrition_count,
           ROUND(AVG(tenure_months),1) AS avg_tenure_at_exit
    FROM attrition
    GROUP BY department
),
dept_velocity AS (
    SELECT department,
           ROUND(AVG(velocity),1) AS avg_velocity,
           ROUND(AVG(completion_rate),1) AS avg_completion
    FROM jira_sprints WHERE sprint_status='Completed'
    GROUP BY department
)
SELECT
    dv.department,
    dv.avg_velocity,
    dv.avg_completion,
    COALESCE(da.attrition_count, 0)     AS total_attritions,
    COALESCE(da.avg_tenure_at_exit, 0)  AS avg_tenure_at_exit,
    -- Hypothesis: higher attrition correlates with lower velocity
    CASE WHEN da.attrition_count > 50 AND dv.avg_velocity < 50
         THEN 'High attrition impacting velocity'
         WHEN da.attrition_count > 30
         THEN 'Moderate risk'
         ELSE 'Stable team'
    END AS team_stability
FROM dept_velocity dv
LEFT JOIN dept_attrition da ON dv.department = da.department
ORDER BY dv.avg_velocity DESC;


-- ----------------------------------------------------------------
-- SECTION 5: TRAINING ROI ANALYSIS
-- ----------------------------------------------------------------

-- 5.1 Training effectiveness by type
SELECT
    training_type,
    COUNT(*)                                    AS sessions,
    COUNT(DISTINCT emp_id)                      AS employees_trained,
    ROUND(AVG(duration_hours),1)               AS avg_duration_hrs,
    ROUND(AVG(score),1)                        AS avg_score,
    ROUND(AVG(cost_per_person),0)              AS avg_cost_per_person,
    SUM(cost_per_person)                       AS total_training_cost,
    COUNT(CASE WHEN certification=1 THEN 1 END) AS certifications_earned,
    ROUND(COUNT(CASE WHEN completion_status='Completed' THEN 1 END)
          *100.0/COUNT(*),1)                   AS completion_rate
FROM training
GROUP BY training_type
ORDER BY employees_trained DESC;


-- 5.2 Trained vs untrained employee performance comparison
WITH trained_emps AS (
    SELECT DISTINCT emp_id FROM training
    WHERE completion_status = 'Completed'
),
perf_comparison AS (
    SELECT
        e.emp_id,
        e.department,
        CASE WHEN t.emp_id IS NOT NULL THEN 'Trained' ELSE 'Not Trained' END AS training_status,
        e.performance_rating,
        e.job_satisfaction,
        e.attrition,
        e.salary_hike_pct
    FROM employees e
    LEFT JOIN trained_emps t ON e.emp_id = t.emp_id
)
SELECT
    training_status,
    COUNT(*)                                    AS employees,
    ROUND(AVG(performance_rating),2)           AS avg_performance,
    ROUND(AVG(job_satisfaction),2)             AS avg_satisfaction,
    ROUND(AVG(attrition)*100,2)               AS attrition_rate_pct,
    ROUND(AVG(salary_hike_pct),2)             AS avg_salary_hike
FROM perf_comparison
GROUP BY training_status;


-- ----------------------------------------------------------------
-- SECTION 6: EXECUTIVE HR DASHBOARD
-- ----------------------------------------------------------------

-- 6.1 HR KPI summary
SELECT
    (SELECT COUNT(*) FROM employees)                            AS total_employees,
    (SELECT COUNT(*) FROM employees WHERE attrition=0)         AS active_employees,
    (SELECT ROUND(AVG(attrition)*100,2) FROM employees)        AS overall_attrition_rate,
    (SELECT ROUND(AVG(annual_salary)/100000,2) FROM employees) AS avg_salary_lakh,
    (SELECT ROUND(AVG(performance_rating),2) FROM employees)   AS avg_performance_rating,
    (SELECT ROUND(AVG(job_satisfaction),2) FROM employees)     AS avg_job_satisfaction,
    (SELECT ROUND(SUM(replacement_cost_lakh),0) FROM attrition) AS total_attrition_cost_lakh,
    (SELECT ROUND(AVG(velocity),1) FROM jira_sprints
     WHERE sprint_status='Completed')                          AS avg_sprint_velocity,
    (SELECT ROUND(AVG(completion_rate),1) FROM jira_sprints
     WHERE sprint_status='Completed')                          AS avg_sprint_completion,
    (SELECT COUNT(*) FROM training
     WHERE completion_status='Completed')                      AS training_completions;


-- 6.2 Department health matrix
SELECT
    e.department,
    COUNT(DISTINCT e.emp_id)                                    AS headcount,
    ROUND(AVG(e.annual_salary)/100000,2)                       AS avg_salary_lakh,
    ROUND(AVG(e.attrition)*100,2)                              AS attrition_rate,
    ROUND(AVG(e.job_satisfaction),2)                           AS avg_satisfaction,
    ROUND(AVG(e.performance_rating),2)                         AS avg_performance,
    ROUND(AVG(e.overtime_hours_weekly),1)                      AS avg_overtime,
    COALESCE(ROUND(AVG(js.completion_rate),1),0)               AS avg_sprint_completion,
    -- Department health score (higher is better)
    ROUND(
        AVG(e.job_satisfaction) * 10 +
        AVG(e.performance_rating) * 10 +
        (1 - AVG(e.attrition)) * 30 +
        (1 - AVG(e.overtime_hours_weekly)/20.0) * 20,
    1) AS health_score
FROM employees e
LEFT JOIN jira_sprints js ON e.department = js.department
GROUP BY e.department
ORDER BY health_score DESC;
