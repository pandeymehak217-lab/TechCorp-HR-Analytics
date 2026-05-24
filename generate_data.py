"""
TechCorp HR Analytics — Attrition and Workforce Dataset
Author : Mehak Pandey
Email  : pandeymehak.217@gmail.com
Tables : employees, departments, performance, attrition,
         training, jira_sprints
Period : 2020 - 2024
"""
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

random.seed(21)
np.random.seed(21)

BASE = '/Users/mehekpandey/hr_project/data'

DEPARTMENTS = ['Engineering','Product','Sales','Marketing',
               'HR','Finance','Operations','Data Analytics',
               'Customer Success','Legal']

ROLES = {
    'Engineering':      ['Software Engineer','Senior Engineer','Tech Lead',
                         'Engineering Manager','Principal Engineer','DevOps Engineer'],
    'Product':          ['Product Manager','Senior PM','Director of Product',
                         'Product Analyst','VP Product'],
    'Sales':            ['Sales Executive','Senior Sales','Sales Manager',
                         'Regional Manager','VP Sales','Account Manager'],
    'Marketing':        ['Marketing Executive','Content Writer','SEO Analyst',
                         'Digital Marketing Manager','Brand Manager'],
    'HR':               ['HR Executive','HR Manager','Recruiter',
                         'HR Business Partner','HR Director'],
    'Finance':          ['Financial Analyst','Senior Analyst','Finance Manager',
                         'Controller','CFO'],
    'Operations':       ['Operations Executive','Operations Manager',
                         'Process Analyst','COO'],
    'Data Analytics':   ['Data Analyst','Senior Analyst','Data Scientist',
                         'Analytics Manager','BI Developer'],
    'Customer Success': ['CS Executive','CS Manager','Account Executive',
                         'CS Director'],
    'Legal':            ['Legal Executive','Legal Manager','Company Secretary',
                         'General Counsel'],
}

EDUCATION = ['High School','Diploma','Bachelor','Master','PhD']
EDU_WEIGHTS = [5,10,45,35,5]

CITIES = ['Bengaluru','Mumbai','Delhi','Hyderabad','Pune',
          'Chennai','Gurugram','Noida','Kolkata','Ahmedabad']

ATTRITION_REASONS = ['Better Opportunity','Higher Salary','Work Life Balance',
                     'Relocation','Manager Issues','Growth Stagnation',
                     'Company Culture','Personal Reasons','Competitor Offer',
                     'Health Issues']

TRAINING_TYPES = ['Technical Skills','Leadership','Communication',
                  'Data Analysis','Project Management','Compliance',
                  'Sales Training','Product Knowledge','Agile Scrum','Excel & BI Tools']

JIRA_ISSUE_TYPES = ['Story','Bug','Task','Epic','Sub-task']
JIRA_PRIORITIES  = ['Highest','High','Medium','Low','Lowest']
SPRINT_STATUS    = ['Completed','In Progress','Future']

first_names = ['Aarav','Aditi','Aditya','Akash','Ananya','Anjali','Arjun',
               'Deepika','Divya','Ishaan','Isha','Karan','Kavya','Meera',
               'Mihir','Nisha','Priya','Rahul','Riya','Rohit','Sanjay',
               'Shreya','Siddharth','Sneha','Tanvi','Utkarsh','Varun',
               'Vikram','Yash','Amit','Pooja','Rajesh','Sunita','Manoj']
last_names = ['Sharma','Patel','Singh','Gupta','Kumar','Verma','Joshi',
              'Nair','Reddy','Mehta','Shah','Iyer','Pillai','Rao',
              'Malhotra','Agarwal','Banerjee','Mishra','Pandey','Trivedi']

def rand_date(s, e):
    s = datetime.strptime(s, '%Y-%m-%d')
    e = datetime.strptime(e, '%Y-%m-%d')
    return s + timedelta(seconds=random.randint(0, int((e-s).total_seconds())))

# TABLE 1: DEPARTMENTS
departments = []
for i, dept in enumerate(DEPARTMENTS, 1):
    departments.append({
        'dept_id':        f'DEPT{i:02d}',
        'dept_name':      dept,
        'dept_head':      f'{random.choice(first_names)} {random.choice(last_names)}',
        'budget_lakh':    random.choice([50,100,200,300,500,800,1000]),
        'headcount_target': random.randint(20, 150),
        'location':       random.choice(CITIES),
        'cost_center':    f'CC{random.randint(1000,9999)}',
    })
dept_df = pd.DataFrame(departments)

# TABLE 2: EMPLOYEES
N_EMP = 2000
employees = []
for eid in range(1, N_EMP+1):
    dept      = random.choice(DEPARTMENTS)
    role      = random.choice(ROLES[dept])
    join_date = rand_date('2015-01-01','2023-12-31')
    age       = random.randint(22, 55)
    edu       = random.choices(EDUCATION, weights=EDU_WEIGHTS)[0]

    # Salary based on role seniority
    base_sal  = {'Software Engineer':800000,'Senior Engineer':1400000,
                 'Tech Lead':2000000,'Engineering Manager':2800000,
                 'Principal Engineer':3500000,'Data Analyst':600000,
                 'Senior Analyst':1000000,'Data Scientist':1800000,
                 'Analytics Manager':2500000,'BI Developer':900000,
                 'Sales Executive':500000,'Senior Sales':800000,
                 'Sales Manager':1200000,'Product Manager':1500000,
                 'Senior PM':2200000,'HR Executive':450000,
                 'Financial Analyst':700000}.get(role, 700000)

    salary = round(base_sal * random.uniform(0.85, 1.25), 0)

    # Attrition probability
    attrition_prob = 0.15
    if salary < 600000:        attrition_prob += 0.10
    if age < 30:               attrition_prob += 0.08
    if dept == 'Sales':        attrition_prob += 0.05
    if dept == 'Engineering':  attrition_prob += 0.03

    left = random.random() < attrition_prob
    left_date = rand_date(join_date.strftime('%Y-%m-%d'), '2024-12-31') if left else None

    tenure_months = ((left_date or datetime(2024,12,31)) - join_date).days // 30

    employees.append({
        'emp_id':              f'EMP{eid:05d}',
        'emp_name':            f'{random.choice(first_names)} {random.choice(last_names)}',
        'age':                 age,
        'gender':              random.choices(['Male','Female','Other'],weights=[54,44,2])[0],
        'department':          dept,
        'role':                role,
        'education':           edu,
        'city':                random.choice(CITIES),
        'join_date':           join_date.strftime('%Y-%m-%d'),
        'left_date':           left_date.strftime('%Y-%m-%d') if left_date else None,
        'tenure_months':       tenure_months,
        'annual_salary':       salary,
        'salary_hike_pct':     round(random.uniform(3, 25), 1),
        'years_at_company':    round(tenure_months/12, 1),
        'work_from_home_days': random.randint(0, 5),
        'distance_from_office':random.randint(1, 50),
        'overtime_hours_weekly':random.randint(0, 20),
        'attrition':           1 if left else 0,
        'manager_id':          f'EMP{random.randint(1,200):05d}',
        'dept_id':             f'DEPT{DEPARTMENTS.index(dept)+1:02d}',
        'job_satisfaction':    random.randint(1, 5),
        'work_life_balance':   random.randint(1, 5),
        'environment_satisfaction': random.randint(1, 5),
        'relationship_satisfaction': random.randint(1, 5),
        'performance_rating':  random.choices([1,2,3,4,5],weights=[5,10,40,35,10])[0],
        'stock_options':       random.choices([0,1,2,3],weights=[30,35,25,10])[0],
        'num_companies_worked':random.randint(1, 8),
    })
emp_df = pd.DataFrame(employees)

# TABLE 3: PERFORMANCE REVIEWS
perf_reviews = []
rev_id = 1
for _, emp in emp_df.iterrows():
    n_reviews = min(5, max(1, int(emp['years_at_company'])))
    for rev_num in range(1, n_reviews+1):
        rev_year = 2020 + rev_num - 1
        if rev_year > 2024: break
        perf_reviews.append({
            'review_id':         f'REV{rev_id:07d}',
            'emp_id':            emp['emp_id'],
            'review_year':       rev_year,
            'review_quarter':    f'Q{random.randint(1,4)}',
            'kpi_score':         round(random.uniform(2.0, 5.0), 1),
            'goal_completion_pct':random.randint(50, 100),
            'manager_rating':    random.choices([1,2,3,4,5],weights=[5,10,35,35,15])[0],
            'peer_rating':       random.choices([1,2,3,4,5],weights=[5,10,35,35,15])[0],
            'self_rating':       random.choices([1,2,3,4,5],weights=[3,8,30,40,19])[0],
            'promotion_flag':    random.choices([0,1],weights=[85,15])[0],
            'increment_pct':     round(random.uniform(3, 30), 1),
            'department':        emp['department'],
        })
        rev_id += 1
perf_df = pd.DataFrame(perf_reviews)

# TABLE 4: ATTRITION DETAILS
attrited = emp_df[emp_df['attrition']==1]
attrition_details = []
for _, emp in attrited.iterrows():
    attrition_details.append({
        'attrition_id':      f'ATT{len(attrition_details)+1:05d}',
        'emp_id':            emp['emp_id'],
        'department':        emp['department'],
        'role':              emp['role'],
        'left_date':         emp['left_date'],
        'tenure_months':     emp['tenure_months'],
        'annual_salary':     emp['annual_salary'],
        'primary_reason':    random.choice(ATTRITION_REASONS),
        'secondary_reason':  random.choice(ATTRITION_REASONS),
        'exit_interview_done': random.choices([1,0],weights=[75,25])[0],
        'would_rejoin':      random.choices(['Yes','No','Maybe'],weights=[30,40,30])[0],
        'notice_period_days':random.choice([30,60,90]),
        'replacement_cost_lakh': round(emp['annual_salary']/100000 * random.uniform(0.5,1.5), 1),
        'age':               emp['age'],
        'gender':            emp['gender'],
        'job_satisfaction':  emp['job_satisfaction'],
        'work_life_balance': emp['work_life_balance'],
    })
att_df = pd.DataFrame(attrition_details)

# TABLE 5: TRAINING RECORDS
training = []
for tid in range(1, 3001):
    emp = emp_df.sample(1).iloc[0]
    tr_date = rand_date('2020-01-01','2024-12-31')
    training.append({
        'training_id':       f'TRN{tid:05d}',
        'emp_id':            emp['emp_id'],
        'department':        emp['department'],
        'training_type':     random.choice(TRAINING_TYPES),
        'training_date':     tr_date.strftime('%Y-%m-%d'),
        'duration_hours':    random.choice([4,8,16,24,40]),
        'completion_status': random.choices(['Completed','In Progress','Not Started'],
                                            weights=[80,12,8])[0],
        'score':             random.randint(50, 100),
        'cost_per_person':   random.choice([5000,10000,15000,25000,50000]),
        'trainer_type':      random.choices(['Internal','External','Online'],
                                            weights=[35,35,30])[0],
        'certification':     random.choices([1,0],weights=[40,60])[0],
    })
training_df = pd.DataFrame(training)

# TABLE 6: JIRA SPRINT DATA (Agile metrics)
sprints = []
for sid in range(1, 201):
    dept      = random.choice(['Engineering','Product','Data Analytics'])
    start     = rand_date('2020-01-01','2024-10-01')
    end       = start + timedelta(days=14)
    planned   = random.randint(20, 60)
    completed = int(planned * random.uniform(0.5, 1.0))
    velocity  = random.randint(30, 80)
    sprints.append({
        'sprint_id':         f'SPR{sid:04d}',
        'sprint_name':       f'Sprint {sid}',
        'department':        dept,
        'start_date':        start.strftime('%Y-%m-%d'),
        'end_date':          end.strftime('%Y-%m-%d'),
        'sprint_year':       start.year,
        'planned_points':    planned,
        'completed_points':  completed,
        'completion_rate':   round(completed/planned*100, 1),
        'velocity':          velocity,
        'bugs_found':        random.randint(0, 15),
        'bugs_fixed':        random.randint(0, 12),
        'team_size':         random.randint(5, 12),
        'sprint_status':     random.choices(SPRINT_STATUS,weights=[70,20,10])[0],
        'retrospective_score': round(random.uniform(3.0, 5.0), 1),
        'blocked_days':      random.randint(0, 5),
    })
sprints_df = pd.DataFrame(sprints)

# SAVE
dfs = {
    'departments': dept_df,
    'employees':   emp_df,
    'performance': perf_df,
    'attrition':   att_df,
    'training':    training_df,
    'jira_sprints':sprints_df,
}
for name, df in dfs.items():
    df.to_csv(f'{BASE}/{name}.csv', index=False)
    print(f"{name:15s}: {len(df):6,} rows x {len(df.columns)} cols")

print(f"\nAttrition Rate : {emp_df['attrition'].mean()*100:.1f}%")
print(f"Avg Salary     : Rs {emp_df['annual_salary'].mean():,.0f}")
print(f"Total Sprints  : {len(sprints_df)}")
print(f"Training Records: {len(training_df)}")
