# TechCorp HR Analytics

This project came from a specific gap I noticed in my portfolio. The first
four projects were all about customers, transactions, and revenue. I had
not touched anything related to people data or organizational analytics.
HR analytics keeps coming up in job descriptions — not just at HR-tech
companies but at IT services firms, consulting companies, and any large
organization that has a people analytics team.

I also wanted to learn R. I had been putting it off because Python was
enough for most things but R is specifically strong for statistical
modelling and the HR domain is full of questions that need proper
hypothesis testing not just descriptive analysis.

---

## What I Built

Workforce analytics across 6 tables covering attrition prediction,
performance management, Agile sprint tracking using Jira-style data,
and training ROI. SQL for the business queries, Python for charts and
Excel output, and R for the statistical analysis including logistic
regression.

The Jira sprint data was something I added specifically because Agile
metrics show up in a lot of analyst job descriptions and I had never
worked with that kind of data before.

---

## Dataset

| Table | Rows | What it contains |
|-------|------|-----------------|
| employees | 2,000 | Salary, satisfaction scores, overtime, tenure |
| departments | 10 | Budget, headcount target, location |
| performance | 7,058 | Annual KPI reviews, promotions, ratings |
| attrition | 389 | Exit reasons, tenure at exit, replacement cost |
| training | 3,000 | Type, completion status, score, cost |
| jira_sprints | 200 | Velocity, completion rate, bugs, blocked days |

Attrition rate came out at 19.4 percent.
Average salary across the company is Rs 9.76 Lakh.
200 sprint records across Engineering, Product, and Data Analytics.

---

## Folder Structure

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
|   |-- hr_analysis.sql
|
|-- python/
|   |-- analysis.py
|
|-- r_analysis/
|   |-- hr_statistics.R
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

## SQL Work

Six sections. The attrition risk scoring model in Section 2 is the
most interesting SQL in this project. Instead of just counting who
left I built a scoring system that assigns points based on job
satisfaction level, overtime hours, salary bracket, tenure, number
of previous companies, and distance from office. Each factor adds
to a total risk score and the output labels each active employee
as High Risk, Medium Risk, or Low Risk.

The Jira sprint queries track velocity trend by department using
LAG across years and flag underperforming sprints using a health
scoring logic based on completion rate, bugs found, and blocked
days. I had not written SQL on this type of operational data before
and it required thinking differently about what the grain of the
table is.

The trained versus untrained comparison in Section 5 uses a LEFT JOIN
to classify employees as trained or not and then compares average
performance rating, satisfaction score, attrition rate, and salary
hike between the two groups.

---

## R Statistical Analysis

This is the part I spent the most time learning from scratch.

Chi-square test on attrition versus job satisfaction came out
not significant at p = 0.15. That means job satisfaction alone
does not predict attrition. It has to act in combination with
other factors. This is actually a more interesting finding than
if it had been significant.

Welch T-test comparing salary between employees who left and
those who stayed also came out not significant at p = 0.29.
Attrition at this company is not primarily salary-driven.
People are leaving for other reasons.

Logistic regression using six predictors identified overtime
hours per week, number of previous companies, and job
satisfaction as the three significant predictors of attrition.
Overtime was the strongest positive predictor — more overtime
means higher probability of leaving.

One-way ANOVA confirmed salary differs significantly across
departments. Tukey HSD post-hoc showed the Engineering versus
HR pay gap is the widest. That is not surprising but the test
confirms it is statistically real and not just a sample artifact.

All visualizations are done in ggplot2 with a consistent
red-yellow-green color scheme.

---

## What I Found

Sales has the highest attrition at 27.3 percent. The replacement
cost for that department alone is over Rs 45 Lakh per year based
on the exit data.

Employees working more than 15 overtime hours weekly are roughly
3x more likely to leave within 12 months. This was the clearest
signal in the logistic regression.

Engineering sprint velocity improved 12 percent from 2020 to 2024.
Sprints with more than 5 blocked days have a 40 percent lower
completion rate which makes intuitive sense but it is useful to
see it in the data.

Agile training has the highest completion rate at 83 percent and
the strongest link to performance improvement. Technical skills
training costs the most but has the lowest completion rate.

---

## How To Run

```bash
pip3 install duckdb pandas numpy matplotlib scipy xlsxwriter
python3 generate_data.py
python3 run_queries.py
python3 python/analysis.py
```

For R — install R and RStudio, then open r_analysis/hr_statistics.R
and run it section by section. Each section has comments explaining
what the test is doing and how to interpret the output.

---

## What I Would Do Differently

The logistic regression model is trained and evaluated on the same
dataset which is not proper machine learning practice. I should split
into training and test sets and report accuracy, precision, and recall
on the held-out test set.

The Jira data is also simplified. Real sprint data has story point
estimates versus actuals, individual contributor velocity, and
dependency tracking between teams. That granularity would make the
Agile analysis much richer.

---

## What I Learned

Learning R from scratch for this project was harder than I expected.
The syntax is different enough from Python that I kept making mistakes
with how functions are called and how data frames work. The glm()
function for logistic regression took me a while to understand —
specifically what the binomial family and logit link actually mean
and why you exponentiate the coefficients to get odds ratios.

The statistical test results that came back not significant were
actually more interesting to interpret than significant ones would
have been. A p-value of 0.15 does not mean satisfaction does not
matter. It means satisfaction alone is not sufficient to predict
attrition. That nuance is something I would not have understood
without running the test myself.

Writing the attrition risk scoring model in SQL taught me that
you can encode business logic directly into queries. The scoring
model is essentially a decision tree implemented in CASE WHEN.
It is not as sophisticated as a machine learning model but it
is interpretable and easy for a non-technical manager to review
and adjust.

---

Mehak Pandey
pandeymehak.217@gmail.com
