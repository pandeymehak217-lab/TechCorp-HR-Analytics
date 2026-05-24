# TechCorp HR Analytics — Attrition, Performance and Agile Metrics

Author: Mehak Pandey
Email : pandeymehak.217@gmail.com
Tools : SQL, Python, R, Power BI
Period: 2020 - 2024

---

## Project Overview

TechCorp HR Analytics is a workforce intelligence project covering employee
attrition prediction, performance management, Agile sprint tracking using
Jira-style data, and training ROI analysis. This project demonstrates the
full data analyst toolkit that HR-tech, IT services, and consulting companies
test in their analyst interviews.

The project includes a logistic regression model in R that predicts attrition
probability, chi-square and t-test hypothesis testing, Power BI dashboards
with 12 DAX measures, and SQL-based attrition risk scoring.

---

## Dataset

| Table | Rows | Description |
|-------|------|-------------|
| employees | 2,000 | Demographics, salary, satisfaction, performance |
| departments | 10 | Budget, headcount target, location |
| performance | 7,058 | Annual reviews, KPI scores, promotions |
| attrition | 389 | Exit details, reasons, replacement cost |
| training | 3,000 | Training type, score, cost, certification |
| jira_sprints | 200 | Sprint velocity, completion, bugs, team size |

Attrition Rate: 19.4% | Avg Salary: Rs 9.76 Lakh | Total Sprints: 200

---

## Project Structure

```
hr-analytics/
|
|-- data/
|   |-- employees.csv
|   |-- departments.csv
|   |-- performance.csv
|   |-- attrition.csv
|   |-- training.csv
|   |-- jira_sprints.csv
|
|-- sql/
|   |-- hr_analysis.sql           (20+ queries, 6 sections)
|
|-- python/
|   |-- analysis.py               (stats, charts, Excel)
|
|-- r_analysis/
|   |-- hr_statistics.R           (R stats, logistic regression, ggplot2)
|
|-- powerbi/
|   |-- POWERBI_GUIDE.md          (12 DAX measures, 4 dashboard pages)
|
|-- outputs/
|   |-- hr_dashboard.png
|   |-- TechCorp_HR_Report.xlsx
|
|-- generate_data.py
|-- run_queries.py
|-- README.md
```

---

## SQL Analysis (20+ Queries, 6 Sections)

Section 1 - Workforce Overview: headcount, gender diversity, age group analysis

Section 2 - Attrition Analysis:
- Attrition reasons with financial impact and RANK()
- Early attrition cost analysis (0-6, 7-12, 13-24 months)
- Attrition risk scoring model using CASE-based scoring
- Year-wise trend with LAG() and YoY change by department

Section 3 - Performance: KPI scores, promotion rates, high performers at risk

Section 4 - Agile/Jira Metrics:
- Sprint velocity trend by department with LAG()
- Sprint health scorecard flagging underperforming sprints
- Team productivity vs attrition impact correlation

Section 5 - Training ROI: completion rates, cost vs score, trained vs untrained comparison

Section 6 - Executive Dashboard: single-query KPI summary, department health matrix

---

## R Statistical Analysis

Descriptive Statistics
Mean, standard deviation, coefficient of variation for salary, tenure,
satisfaction, performance across all departments.

Chi-Square Test
Null hypothesis: Attrition is independent of job satisfaction.
Result: chi2 = 6.74, p = 0.15 — not significant at 95% confidence level.
Interpretation: Job satisfaction alone does not predict attrition;
it acts together with salary and overtime.

Welch T-Test
Null hypothesis: Salary is equal for employees who left vs stayed.
Result: t = -1.05, p = 0.29 — not significant.
Interpretation: Attrition is not purely salary-driven at TechCorp.
Growth opportunities and satisfaction are stronger predictors.

Logistic Regression
Predicted attrition probability using 6 predictors.
Key coefficients: overtime_hours_weekly (positive, significant),
num_companies_worked (positive, significant),
job_satisfaction (negative, significant).

ANOVA
Salary differs significantly across departments (F-test, p < 0.05).
Tukey HSD post-hoc confirms Engineering vs HR pay gap is widest.

Visualizations
ggplot2 charts: attrition by department, salary distribution,
sprint velocity trend, correlation heatmap saved as PNG files.

---

## Power BI Dashboard (4 Pages, 12 DAX Measures)

Page 1 - Workforce Overview: headcount, gender, salary by department
Page 2 - Attrition Deep Dive: gauge, risk table, attrition by reason
Page 3 - Performance and Training: KPI scores, training ROI matrix
Page 4 - Agile Metrics: sprint velocity, completion, bug tracking

Key DAX Measures: Attrition Rate %, Gender Pay Gap %, High Risk Employees,
Training Completion Rate, Avg Sprint Velocity, Attrition Cost vs Budget.

Full setup guide in powerbi/POWERBI_GUIDE.md

---

## Key Business Findings

Sales department has the highest attrition at 27.3%, driven mainly by
Better Opportunity and Higher Salary as exit reasons. Replacement cost
for this department alone exceeds Rs 45 Lakh annually.

Employees who work more than 15 overtime hours weekly are 3x more likely
to leave within 12 months. This is the strongest single predictor found
in the logistic regression model.

Engineering sprint velocity has improved by 12% from 2020 to 2024,
while Data Analytics sprints show the highest completion rate at 84%.
Sprints with more than 5 blocked days have a 40% lower completion rate.

Agile training has the highest completion rate at 83% and the highest
post-training performance improvement. Technical skills training has
the highest cost but lowest completion rate, suggesting delivery issues.

High-performing employees with job satisfaction of 2 or below represent
the most critical retention risk. 18 such employees are currently active
and should be prioritized for salary review and career development plans.

---

## How to Run

```bash
pip3 install duckdb pandas numpy matplotlib scipy xlsxwriter
python3 generate_data.py
python3 run_queries.py
python3 python/analysis.py
```

For R analysis (install R and RStudio first):
Open r_analysis/hr_statistics.R in RStudio and run section by section.

For Power BI: follow powerbi/POWERBI_GUIDE.md

---

## SQL Concepts Used

Attrition risk scoring with multi-condition CASE WHEN,
LAG() for year-over-year attrition trends,
RANK() and PERCENT_RANK() for performance ranking,
PARTITION BY for department-level metrics,
multi-table CTEs joining 6 tables,
HAVING for filtering aggregated performance,
window functions for running totals and moving averages

---

## R Concepts Used

Logistic regression with glm() and binomial family,
One-way ANOVA with TukeyHSD post-hoc,
Welch T-test for independent samples,
Chi-square test for categorical independence,
Pearson correlation matrix with corrplot,
ggplot2 visualizations with custom color themes

---

About
Mehak Pandey — Fresher Data Analyst
Email: pandeymehak.217@gmail.com
Dataset is synthetically generated to simulate real corporate HR data.
