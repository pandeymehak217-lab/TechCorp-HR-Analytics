# TechCorp HR Analytics — Power BI Dashboard Guide
# Author: Mehak Pandey | pandeymehak.217@gmail.com

---

## STEP 1: IMPORT DATA

In Power BI Desktop or app.powerbi.com:

1. Get Data > Text/CSV
2. Import all 6 files from hr_project/data/:
   - employees.csv
   - departments.csv
   - performance.csv
   - attrition.csv
   - training.csv
   - jira_sprints.csv

---

## STEP 2: BUILD RELATIONSHIPS (Model View)

Connect these tables:

employees.emp_id       -> attrition.emp_id       (1 to 1)
employees.emp_id       -> performance.emp_id      (1 to Many)
employees.emp_id       -> training.emp_id         (1 to Many)
employees.dept_id      -> departments.dept_id     (Many to 1)
employees.department   -> jira_sprints.department (Many to Many)

---

## STEP 3: DAX MEASURES

Copy each measure into Power BI (Modeling > New Measure):

Total Employees
= COUNTROWS(employees)

Active Employees
= CALCULATE(COUNTROWS(employees), employees[attrition] = 0)

Attrition Rate %
= DIVIDE(
    CALCULATE(COUNTROWS(employees), employees[attrition] = 1),
    COUNTROWS(employees)
) * 100

Avg Salary (Lakh)
= ROUND(AVERAGE(employees[annual_salary]) / 100000, 2)

Total Attrition Cost (Lakh)
= SUM(attrition[replacement_cost_lakh])

Avg Job Satisfaction
= AVERAGE(employees[job_satisfaction])

Avg Performance Rating
= AVERAGE(employees[performance_rating])

Avg Sprint Velocity
= CALCULATE(
    AVERAGE(jira_sprints[velocity]),
    jira_sprints[sprint_status] = "Completed"
)

Avg Sprint Completion %
= CALCULATE(
    AVERAGE(jira_sprints[completion_rate]),
    jira_sprints[sprint_status] = "Completed"
)

Training Completion Rate
= DIVIDE(
    CALCULATE(COUNTROWS(training),
              training[completion_status] = "Completed"),
    COUNTROWS(training)
) * 100

High Risk Employees
= CALCULATE(
    COUNTROWS(employees),
    employees[job_satisfaction] <= 2,
    employees[overtime_hours_weekly] > 15,
    employees[attrition] = 0
)

Gender Pay Gap %
= DIVIDE(
    CALCULATE(AVERAGE(employees[annual_salary]),
              employees[gender] = "Male") -
    CALCULATE(AVERAGE(employees[annual_salary]),
              employees[gender] = "Female"),
    AVERAGE(employees[annual_salary])
) * 100

Attrition Cost vs Budget
= DIVIDE([Total Attrition Cost (Lakh)],
         SUM(departments[budget_lakh])) * 100

---

## STEP 4: PAGE 1 — WORKFORCE OVERVIEW

Add these visuals on Page 1:

KPI Cards (top row):
- Total Employees
- Active Employees
- Attrition Rate %
- Avg Salary (Lakh)
- Avg Performance Rating

Bar Chart — Headcount by Department:
- X-axis: department
- Y-axis: Total Employees
- Color: Attrition Rate % (Red-Yellow-Green conditional)

Donut Chart — Gender Split:
- Legend: gender
- Values: Total Employees

Treemap — Role Distribution:
- Group: department
- Subgroup: role
- Values: Count of employees

Slicer (top):
- Department
- Gender
- City

---

## STEP 5: PAGE 2 — ATTRITION DEEP DIVE

Gauge — Attrition Rate:
- Value: Attrition Rate %
- Target: 15 (industry benchmark)
- Color: Red if above 15

Bar Chart — Attrition by Department:
- Conditional color formatting:
  > 25% = Red (#C0392B)
  15-25% = Yellow (#F39C12)
  < 15% = Green (#27AE60)

Funnel — Attrition Reasons:
- Category: primary_reason from attrition table
- Values: Count of attrition_id

Scatter Plot — Salary vs Satisfaction:
- X: avg job_satisfaction
- Y: avg annual_salary
- Size: headcount
- Color: attrition rate (Red high, Green low)

Table — Top 10 At-Risk Employees:
- emp_name, department, role
- annual_salary, job_satisfaction, overtime_hours_weekly
- Conditional format: job_satisfaction red if <= 2

Line Chart — Attrition Trend by Year:
- X: year from left_date
- Y: count of attritions
- Legend: department

---

## STEP 6: PAGE 3 — PERFORMANCE AND TRAINING

Column Chart — KPI Score by Department:
- X: department
- Y: avg kpi_score from performance table
- Reference line at 3.5 (target)
- Color: Green above 3.5, Red below

Matrix Table — Performance Rating Distribution:
- Rows: department
- Columns: performance_rating (1-5)
- Values: Count
- Conditional format cells

Bar Chart — Training Completion by Type:
- X: training_type
- Y: Training Completion Rate %
- Sort descending

Scatter — Training Cost vs Score:
- X: avg cost_per_person
- Y: avg score
- Size: count of sessions
- Labels: training_type

Card — Total Training Cost:
= SUMX(training, training[cost_per_person])

---

## STEP 7: PAGE 4 — AGILE / JIRA METRICS

Line Chart — Sprint Velocity Trend:
- X: sprint_year
- Y: avg velocity
- Legend: department
- This is your Agile story for recruiters

Column Chart — Sprint Completion Rate:
- X: department
- Y: avg completion_rate
- Reference line at 80% (target)
- Red if below 80, Green if above

Gauge — Avg Sprint Completion:
- Value: Avg Sprint Completion %
- Target: 85

Table — Sprint Health Scorecard:
- sprint_name, department, completion_rate
- velocity, bugs_found, retrospective_score
- Conditional format:
  completion_rate > 90 = Green background
  completion_rate 70-90 = Yellow background
  < 70 = Red background

Bar — Bug Found vs Fixed by Department:
- Clustered bar: bugs_found and bugs_fixed
- Color: Red for found, Green for fixed

---

## STEP 8: COLOR THEME

Apply consistently across all pages:

Primary Red    : #C0392B
Primary Yellow : #F39C12
Primary Green  : #27AE60
Background     : #FFFFFF
Dark Text      : #2C3E50
Light Gray     : #F5F6FA
Card Border    : #BDC3C7

Font: Segoe UI (Power BI default, closest to Arial)

To set theme:
View > Themes > Customize current theme
Set font to Segoe UI, colors as above, save as TechCorp_HR_Theme.json

---

## STEP 9: SAVE AND PUBLISH

1. File > Save As > TechCorp_HR_Dashboard.pbix
   Location: ~/hr_project/powerbi/

2. Publish to Power BI Service:
   Home > Publish > Select workspace

3. Export as PDF for resume:
   File > Export > Export to PDF

4. Get shareable link:
   In Power BI Service > Share > Copy link
   Add to GitHub README and LinkedIn post

---

## RESUME TALKING POINTS FOR THIS DASHBOARD

"Built a 4-page Power BI dashboard for HR analytics covering
workforce overview, attrition risk scoring, training ROI,
and Agile sprint metrics. Used 10 DAX measures including
Gender Pay Gap %, Attrition Cost vs Budget, and High Risk
Employee count. Applied conditional formatting with
Red-Yellow-Green traffic light system across all visuals."
