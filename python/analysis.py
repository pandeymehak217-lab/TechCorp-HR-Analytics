"""
TechCorp HR Analytics — Python Analysis and Excel Report
Author : Mehak Pandey
Email  : pandeymehak.217@gmail.com
"""
import duckdb
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

BASE = '/Users/mehekpandey/hr_project/data'
OUT  = '/Users/mehekpandey/hr_project/outputs'

con = duckdb.connect()
for t in ['departments','employees','performance','attrition','training','jira_sprints']:
    con.execute(f"CREATE TABLE {t} AS SELECT * FROM read_csv_auto('{BASE}/{t}.csv')")

def q(sql): return con.execute(sql).df()

RED    = '#C0392B'
YELLOW = '#F39C12'
GREEN  = '#27AE60'
DARK   = '#2C3E50'
LIGHT  = '#F5F6FA'

# ── Queries ────────────────────────────────────────────────
kpi = q("""
    SELECT COUNT(*) AS total_emp,
           COUNT(CASE WHEN attrition=0 THEN 1 END) AS active,
           ROUND(AVG(attrition)*100,2) AS att_rate,
           ROUND(AVG(annual_salary)/100000,2) AS avg_sal_lakh,
           ROUND(AVG(performance_rating),2) AS avg_perf,
           ROUND(AVG(job_satisfaction),2) AS avg_sat
    FROM employees
""")

att_dept = q("""
    SELECT department,
           COUNT(*) AS headcount,
           SUM(attrition) AS left_count,
           ROUND(AVG(attrition)*100,2) AS att_rate,
           ROUND(AVG(annual_salary)/100000,2) AS avg_sal
    FROM employees GROUP BY department ORDER BY att_rate DESC
""")

att_reasons = q("""
    SELECT primary_reason, COUNT(*) AS count,
           ROUND(SUM(replacement_cost_lakh),1) AS total_cost
    FROM attrition GROUP BY primary_reason ORDER BY count DESC
""")

sprint_dept = q("""
    SELECT department, sprint_year,
           ROUND(AVG(velocity),1) AS avg_vel,
           ROUND(AVG(completion_rate),1) AS avg_comp
    FROM jira_sprints WHERE sprint_status='Completed'
    GROUP BY department, sprint_year ORDER BY department, sprint_year
""")

gender_sal = q("""
    SELECT gender, department,
           ROUND(AVG(annual_salary)/100000,2) AS avg_sal,
           COUNT(*) AS count
    FROM employees GROUP BY gender, department
""")

training_type = q("""
    SELECT training_type,
           COUNT(*) AS sessions,
           ROUND(AVG(score),1) AS avg_score,
           ROUND(COUNT(CASE WHEN completion_status='Completed' THEN 1 END)*100.0/COUNT(*),1) AS comp_rate,
           ROUND(AVG(cost_per_person),0) AS avg_cost
    FROM training GROUP BY training_type ORDER BY comp_rate DESC
""")

satisfaction_att = q("""
    SELECT job_satisfaction,
           COUNT(*) AS employees,
           ROUND(AVG(attrition)*100,2) AS att_rate
    FROM employees GROUP BY job_satisfaction ORDER BY job_satisfaction
""")

# Statistical tests
emp_raw = q("SELECT * FROM employees")
stayed = emp_raw[emp_raw['attrition']==0]['annual_salary']
left   = emp_raw[emp_raw['attrition']==1]['annual_salary']
t_stat, t_p = stats.ttest_ind(stayed, left)
chi_tab = pd.crosstab(emp_raw['attrition'], emp_raw['job_satisfaction'])
chi_stat, chi_p, chi_df, _ = stats.chi2_contingency(chi_tab)

print(f"T-test (salary): t={t_stat:.3f}, p={t_p:.4f}")
print(f"Chi-sq (satisfaction): chi2={chi_stat:.3f}, p={chi_p:.6f}")

# ── DASHBOARD ──────────────────────────────────────────────
fig = plt.figure(figsize=(22,26), facecolor='#FFFFFF')
gs  = gridspec.GridSpec(4, 3, figure=fig, hspace=0.48, wspace=0.38)

ax0 = fig.add_subplot(gs[0,:])
ax0.set_facecolor(DARK); ax0.set_xlim(0,10); ax0.set_ylim(0,1); ax0.axis('off')
ax0.text(5, 0.85, 'TechCorp HR Analytics Dashboard 2020-2024',
         ha='center', fontsize=15, fontweight='bold', color='white')
kpi_items = [
    (str(int(kpi['total_emp'].iloc[0])), 'Total Employees'),
    (str(int(kpi['active'].iloc[0])),    'Active Employees'),
    (f"{kpi['att_rate'].iloc[0]}%",      'Attrition Rate'),
    (f"Rs {kpi['avg_sal_lakh'].iloc[0]}L",'Avg Salary'),
    (str(kpi['avg_perf'].iloc[0]),        'Avg Performance'),
    (str(kpi['avg_sat'].iloc[0]),         'Avg Satisfaction'),
]
for i,(v,l) in enumerate(kpi_items):
    x = 0.85 + i*1.38
    ax0.text(x, 0.50, v, ha='center', fontsize=12, fontweight='bold', color=YELLOW)
    ax0.text(x, 0.22, l, ha='center', fontsize=8, color='#BDC3C7')

ax1 = fig.add_subplot(gs[1,0])
ax1.set_facecolor(LIGHT)
colors1 = [RED if r>25 else YELLOW if r>18 else GREEN for r in att_dept['att_rate']]
ax1.barh(att_dept['department'], att_dept['att_rate'],
         color=colors1, edgecolor='white')
ax1.set_title('Attrition Rate by Department', fontweight='bold', color=DARK, fontsize=10)
ax1.set_xlabel('Attrition Rate %', fontsize=8)
for i, v in enumerate(att_dept['att_rate']):
    ax1.text(v+0.3, i, f'{v}%', va='center', fontsize=7, color=DARK)

ax2 = fig.add_subplot(gs[1,1])
ax2.set_facecolor(LIGHT)
colors2 = [RED,YELLOW,GREEN,'#2980B9','#8E44AD','#1ABC9C',
           '#D35400','#16A085','#2C3E50','#7F8C8D'][:len(att_reasons)]
ax2.bar(range(len(att_reasons)), att_reasons['count'],
        color=colors2, edgecolor='white')
ax2.set_xticks(range(len(att_reasons)))
ax2.set_xticklabels([r[:12] for r in att_reasons['primary_reason']],
                    rotation=40, ha='right', fontsize=6.5)
ax2.set_title('Attrition by Reason', fontweight='bold', color=DARK, fontsize=10)
ax2.set_ylabel('Count', fontsize=8)

ax3 = fig.add_subplot(gs[1,2])
ax3.set_facecolor(LIGHT)
sat_colors = [RED if r>30 else YELLOW if r>20 else GREEN
              for r in satisfaction_att['att_rate']]
ax3.bar(satisfaction_att['job_satisfaction'].astype(str),
        satisfaction_att['att_rate'], color=sat_colors, edgecolor='white')
ax3.set_title('Attrition Rate by Job Satisfaction', fontweight='bold', color=DARK, fontsize=10)
ax3.set_xlabel('Satisfaction Score (1=Low, 5=High)', fontsize=8)
ax3.set_ylabel('Attrition Rate %', fontsize=8)
ax3.axhline(y=satisfaction_att['att_rate'].mean(), color=DARK,
            linestyle='--', linewidth=1.2, label='Average')
ax3.legend(fontsize=7)

# Sprint velocity
for dept_idx, dept in enumerate(['Engineering','Product','Data Analytics']):
    ax_s = fig.add_subplot(gs[2, dept_idx])
    ax_s.set_facecolor(LIGHT)
    dept_data = sprint_dept[sprint_dept['department']==dept]
    if len(dept_data) > 0:
        ax_s.plot(dept_data['sprint_year'], dept_data['avg_vel'],
                  color=GREEN, marker='o', linewidth=2, markersize=6, label='Velocity')
        ax_s_t = ax_s.twinx()
        ax_s_t.plot(dept_data['sprint_year'], dept_data['avg_comp'],
                    color=RED, marker='s', linewidth=2, markersize=6, label='Completion%')
        ax_s.set_title(f'{dept} Sprint Metrics', fontweight='bold', color=DARK, fontsize=9)
        ax_s.set_ylabel('Avg Velocity', color=GREEN, fontsize=8)
        ax_s_t.set_ylabel('Completion %', color=RED, fontsize=8)
        ax_s.set_xlabel('Year', fontsize=8)

ax7 = fig.add_subplot(gs[3,0])
ax7.set_facecolor(LIGHT)
colors7 = [GREEN if r>=80 else YELLOW if r>=65 else RED
           for r in training_type['comp_rate']]
ax7.barh(training_type['training_type'], training_type['comp_rate'],
         color=colors7, edgecolor='white')
ax7.set_title('Training Completion Rate by Type', fontweight='bold', color=DARK, fontsize=10)
ax7.set_xlabel('Completion Rate %', fontsize=8)
ax7.axvline(x=80, color=DARK, linestyle='--', linewidth=1.2)

ax8 = fig.add_subplot(gs[3,1])
ax8.set_facecolor(LIGHT)
ax8.axis('off')
stats_text = (
    f"Statistical Analysis Results\n"
    f"{'─'*35}\n\n"
    f"T-Test: Salary (Left vs Stayed)\n"
    f"Stayed mean : Rs {stayed.mean()/100000:.2f} Lakh\n"
    f"Left mean   : Rs {left.mean()/100000:.2f} Lakh\n"
    f"t-statistic : {t_stat:.3f}\n"
    f"p-value     : {t_p:.4f}\n"
    f"Result      : {'Significant' if t_p<0.05 else 'Not significant'}\n\n"
    f"Chi-Square: Attrition vs Satisfaction\n"
    f"chi2-stat   : {chi_stat:.3f}\n"
    f"p-value     : {chi_p:.6f}\n"
    f"df          : {chi_df}\n"
    f"Result      : {'Significant' if chi_p<0.05 else 'Not significant'}\n\n"
    f"Logistic Regression (in R script)\n"
    f"Key predictors of attrition:\n"
    f"1. Job Satisfaction (negative)\n"
    f"2. Overtime Hours (positive)\n"
    f"3. Annual Salary (negative)\n"
    f"4. Num Companies Worked (positive)"
)
ax8.text(0.05, 0.95, stats_text, transform=ax8.transAxes,
         va='top', ha='left', fontsize=8.5, color=DARK, linespacing=1.5,
         bbox=dict(boxstyle='round,pad=0.6', facecolor='#EBF5FB',
                   edgecolor=GREEN, linewidth=1.5))
ax8.set_title('Statistical Tests', fontweight='bold', color=DARK, fontsize=10)

ax9 = fig.add_subplot(gs[3,2])
ax9.set_facecolor(LIGHT)
male_sal   = gender_sal[gender_sal['gender']=='Male'].groupby('department')['avg_sal'].mean()
female_sal = gender_sal[gender_sal['gender']=='Female'].groupby('department')['avg_sal'].mean()
depts = list(male_sal.index)
x = range(len(depts))
ax9.bar([i-0.2 for i in x], male_sal.values,   0.4, label='Male',   color='#2980B9', alpha=0.8)
ax9.bar([i+0.2 for i in x], female_sal.values,  0.4, label='Female', color='#E91E63', alpha=0.8)
ax9.set_xticks(x)
ax9.set_xticklabels([d[:8] for d in depts], rotation=40, ha='right', fontsize=6.5)
ax9.set_title('Gender Pay Gap by Department', fontweight='bold', color=DARK, fontsize=10)
ax9.set_ylabel('Avg Salary (Lakh)', fontsize=8)
ax9.legend(fontsize=7)

plt.suptitle('TechCorp HR Analytics — Complete Workforce Dashboard',
             fontsize=16, fontweight='bold', y=0.995, color=DARK)
plt.savefig(f'{OUT}/hr_dashboard.png', dpi=150, bbox_inches='tight', facecolor='#FFFFFF')
plt.close()
print("Dashboard saved.")

# ── EXCEL ──────────────────────────────────────────────────
excel_path = f'{OUT}/TechCorp_HR_Report.xlsx'
writer = pd.ExcelWriter(excel_path, engine='xlsxwriter')
wb = writer.book

hdr = wb.add_format({'bold':True,'font_color':'#FFFFFF','bg_color':DARK,
                     'border':1,'align':'center','font_name':'Arial','font_size':9})
alt1= wb.add_format({'bg_color':'#EBF5FB','border':1,'font_name':'Arial','font_size':9})
alt2= wb.add_format({'bg_color':'#FFFFFF','border':1,'font_name':'Arial','font_size':9})
ttl = wb.add_format({'bold':True,'font_size':13,'font_color':'#FFFFFF',
                     'bg_color':DARK,'align':'center','font_name':'Arial'})
kpi_fmt = wb.add_format({'bold':True,'font_size':14,'font_color':RED,
                          'align':'center','border':2,'bg_color':'#FDEDEC','font_name':'Arial'})
kpi_lbl = wb.add_format({'font_size':8,'font_color':'#7F8C8D',
                          'align':'center','bg_color':LIGHT,'font_name':'Arial'})

def write_sheet(ws, df, row_start=1):
    for c, col in enumerate(df.columns):
        ws.write(row_start, c, col, hdr)
    for r, row in enumerate(df.itertuples(index=False), row_start+1):
        fmt = alt1 if r%2==0 else alt2
        for c, val in enumerate(row):
            ws.write(r, c, val, fmt)
    for c in range(len(df.columns)):
        ws.set_column(c, c, 18)

# Sheet 1: Executive Summary
ws1 = wb.add_worksheet('Executive Summary')
ws1.set_tab_color(RED)
ws1.merge_range('A1:G2','TechCorp HR Analytics — Executive Summary',ttl)
ws1.set_row(0,22); ws1.set_row(1,22)
kpis_list = [
    (str(int(kpi['total_emp'].iloc[0])),    'Total Employees'),
    (str(int(kpi['active'].iloc[0])),        'Active Employees'),
    (f"{kpi['att_rate'].iloc[0]}%",          'Attrition Rate'),
    (f"Rs {kpi['avg_sal_lakh'].iloc[0]}L",   'Avg Salary'),
    (str(kpi['avg_perf'].iloc[0]),            'Avg Performance'),
    (str(kpi['avg_sat'].iloc[0]),             'Avg Satisfaction'),
]
for i,(v,l) in enumerate(kpis_list):
    ws1.merge_range(3,i,3,i,v,kpi_fmt)
    ws1.merge_range(4,i,4,i,l,kpi_lbl)
    ws1.set_row(3,32); ws1.set_row(4,18)
ws1.merge_range('A7:G7','Department Overview',ttl)
write_sheet(ws1, att_dept, 7)
ws1.insert_image('A22', f'{OUT}/hr_dashboard.png',
                  {'x_scale':0.55,'y_scale':0.55})

ws2 = wb.add_worksheet('Attrition Analysis')
ws2.set_tab_color(YELLOW)
ws2.merge_range('A1:G1','Attrition Reasons and Cost Analysis',ttl)
write_sheet(ws2, att_reasons, 1)

ws3 = wb.add_worksheet('Training Analytics')
ws3.set_tab_color(GREEN)
ws3.merge_range('A1:G1','Training Type Performance',ttl)
write_sheet(ws3, training_type, 1)

ws4 = wb.add_worksheet('Agile Sprint Metrics')
ws4.set_tab_color('#2980B9')
ws4.merge_range('A1:G1','Sprint Performance by Department and Year',ttl)
write_sheet(ws4, sprint_dept, 1)

ws5 = wb.add_worksheet('Statistical Analysis')
ws5.set_tab_color('#8E44AD')
ws5.merge_range('A1:D1','Statistical Test Results',ttl)
stat_rows = [
    ('T-Test','Salary: Left vs Stayed', f't={t_stat:.3f}', f'p={t_p:.4f}',
     'Significant' if t_p<0.05 else 'Not Significant'),
    ('Chi-Square','Attrition vs Satisfaction', f'chi2={chi_stat:.3f}', f'p={chi_p:.6f}',
     'Significant' if chi_p<0.05 else 'Not Significant'),
]
ws5.write(1, 0, 'Test Type', hdr)
ws5.write(1, 1, 'Variables', hdr)
ws5.write(1, 2, 'Statistic', hdr)
ws5.write(1, 3, 'p-value', hdr)
ws5.write(1, 4, 'Conclusion', hdr)
for r, row in enumerate(stat_rows, 2):
    fmt = alt1 if r%2==0 else alt2
    for c, val in enumerate(row):
        ws5.write(r, c, val, fmt)
for c in range(5): ws5.set_column(c,c,22)

writer.close()
print(f"Excel saved: {excel_path}")
con.close()
print("All outputs complete.")
