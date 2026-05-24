# ================================================================
# TechCorp HR Analytics — R Statistical Analysis
# Author : Mehak Pandey
# Email  : pandeymehak.217@gmail.com
# Tools  : R, ggplot2, dplyr, tidyr, corrplot, caret
# ================================================================

# Install packages (run once)
# install.packages(c("tidyverse","corrplot","caret","ggplot2",
#                    "dplyr","readr","scales","gridExtra","RColorBrewer"))

library(tidyverse)
library(ggplot2)
library(dplyr)
library(readr)
library(corrplot)
library(scales)
library(gridExtra)
library(RColorBrewer)

# ── Load Data ─────────────────────────────────────────────
BASE <- "~/hr_project/data"

employees   <- read_csv(file.path(BASE, "employees.csv"))
attrition   <- read_csv(file.path(BASE, "attrition.csv"))
performance <- read_csv(file.path(BASE, "performance.csv"))
training    <- read_csv(file.path(BASE, "training.csv"))
sprints     <- read_csv(file.path(BASE, "jira_sprints.csv"))

cat("Data loaded successfully\n")
cat("Employees:", nrow(employees), "\n")
cat("Attrition records:", nrow(attrition), "\n")

# ── 1. DESCRIPTIVE STATISTICS ─────────────────────────────
cat("\n=== Descriptive Statistics ===\n")
summary(employees[, c("annual_salary","tenure_months","age",
                       "job_satisfaction","performance_rating",
                       "overtime_hours_weekly")])

# Standard deviation and coefficient of variation
numeric_cols <- employees %>%
  select(annual_salary, tenure_months, age,
         job_satisfaction, performance_rating) %>%
  summarise(across(everything(),
    list(mean=mean, sd=sd, cv=~sd(.)/mean(.)*100),
    na.rm=TRUE))
print(numeric_cols)

# ── 2. ATTRITION ANALYSIS ─────────────────────────────────
cat("\n=== Attrition Rate by Department ===\n")
att_dept <- employees %>%
  group_by(department) %>%
  summarise(
    headcount       = n(),
    attritions      = sum(attrition),
    attrition_rate  = round(mean(attrition)*100, 2),
    avg_salary      = round(mean(annual_salary)/100000, 2),
    avg_satisfaction= round(mean(job_satisfaction), 2)
  ) %>%
  arrange(desc(attrition_rate))
print(att_dept)

# ── 3. CHI-SQUARE TEST ────────────────────────────────────
# Is attrition independent of job satisfaction?
cat("\n=== Chi-Square: Attrition vs Job Satisfaction ===\n")
contingency <- table(employees$attrition, employees$job_satisfaction)
chi_result  <- chisq.test(contingency)
cat("Chi-square statistic:", round(chi_result$statistic, 3), "\n")
cat("p-value:", round(chi_result$p.value, 6), "\n")
cat("Degrees of freedom:", chi_result$parameter, "\n")
if (chi_result$p.value < 0.05) {
  cat("Result: Significant association between attrition and job satisfaction\n")
} else {
  cat("Result: No significant association found\n")
}

# ── 4. T-TEST ─────────────────────────────────────────────
# Is salary significantly different between those who left vs stayed?
cat("\n=== Welch T-Test: Salary (Left vs Stayed) ===\n")
stayed <- employees$annual_salary[employees$attrition == 0]
left   <- employees$annual_salary[employees$attrition == 1]
t_result <- t.test(stayed, left)
cat("Mean salary (Stayed): Rs", round(mean(stayed)/100000, 2), "Lakh\n")
cat("Mean salary (Left)  : Rs", round(mean(left)/100000, 2), "Lakh\n")
cat("t-statistic:", round(t_result$statistic, 3), "\n")
cat("p-value:", round(t_result$p.value, 4), "\n")
if (t_result$p.value < 0.05) {
  cat("Result: Salary difference is statistically significant\n")
}

# ── 5. CORRELATION ANALYSIS ───────────────────────────────
cat("\n=== Pearson Correlation Matrix ===\n")
cor_vars <- employees %>%
  select(attrition, annual_salary, tenure_months, age,
         job_satisfaction, work_life_balance,
         overtime_hours_weekly, performance_rating,
         distance_from_office, num_companies_worked) %>%
  na.omit()

cor_matrix <- cor(cor_vars, method="pearson")
cat("Correlation with Attrition:\n")
print(round(cor_matrix["attrition", ], 3))

# ── 6. LOGISTIC REGRESSION ────────────────────────────────
cat("\n=== Logistic Regression: Attrition Predictors ===\n")
model_data <- employees %>%
  select(attrition, annual_salary, tenure_months, age,
         job_satisfaction, work_life_balance,
         overtime_hours_weekly, distance_from_office,
         num_companies_worked, performance_rating) %>%
  na.omit() %>%
  mutate(attrition = as.factor(attrition))

log_model <- glm(attrition ~ annual_salary + tenure_months +
                   job_satisfaction + work_life_balance +
                   overtime_hours_weekly + num_companies_worked,
                 data = model_data,
                 family = binomial(link="logit"))

cat("\nLogistic Regression Coefficients:\n")
summary_model <- summary(log_model)
coef_table <- data.frame(
  Coefficient = round(coef(log_model), 4),
  Odds_Ratio  = round(exp(coef(log_model)), 4),
  p_value     = round(summary_model$coefficients[,4], 4)
)
print(coef_table)

cat("\nModel AIC:", round(AIC(log_model), 2), "\n")
cat("Null deviance:", round(log_model$null.deviance, 2), "\n")
cat("Residual deviance:", round(log_model$deviance, 2), "\n")

# ── 7. ANOVA: SALARY ACROSS DEPARTMENTS ───────────────────
cat("\n=== One-Way ANOVA: Salary across Departments ===\n")
anova_result <- aov(annual_salary ~ department, data=employees)
anova_summary <- summary(anova_result)
print(anova_summary)
if (anova_summary[[1]]["department","Pr(>F)"] < 0.05) {
  cat("Result: Salary differs significantly across departments\n")
  cat("Running Tukey HSD post-hoc test...\n")
  tukey <- TukeyHSD(anova_result)
  sig_pairs <- as.data.frame(tukey$department) %>%
    filter(`p adj` < 0.05) %>%
    select(`p adj`)
  cat("Significant department pairs:", nrow(sig_pairs), "\n")
}

# ── 8. SPRINT ANALYSIS ────────────────────────────────────
cat("\n=== Agile Sprint Performance Analysis ===\n")
sprint_summary <- sprints %>%
  filter(sprint_status == "Completed") %>%
  group_by(department) %>%
  summarise(
    sprints          = n(),
    avg_velocity     = round(mean(velocity), 1),
    avg_completion   = round(mean(completion_rate), 1),
    avg_bugs_found   = round(mean(bugs_found), 1),
    avg_retro_score  = round(mean(retrospective_score), 2),
    avg_blocked_days = round(mean(blocked_days), 1)
  ) %>%
  arrange(desc(avg_velocity))
print(sprint_summary)

# Correlation: team_size vs velocity
cor_sprint <- cor(sprints$team_size, sprints$velocity, use="complete.obs")
cat("\nCorrelation (team size vs velocity):", round(cor_sprint, 3), "\n")

# ── 9. TRAINING ROI ANALYSIS ──────────────────────────────
cat("\n=== Training Completion Rate by Type ===\n")
training_summary <- training %>%
  group_by(training_type) %>%
  summarise(
    sessions   = n(),
    completed  = sum(completion_status=="Completed"),
    comp_rate  = round(mean(completion_status=="Completed")*100, 1),
    avg_score  = round(mean(score, na.rm=TRUE), 1),
    total_cost = sum(cost_per_person),
    avg_cost   = round(mean(cost_per_person), 0)
  ) %>%
  arrange(desc(comp_rate))
print(training_summary)

# ── 10. VISUALIZATIONS ────────────────────────────────────
cat("\nGenerating visualizations...\n")

red    <- "#C0392B"
yellow <- "#F39C12"
green  <- "#27AE60"
dark   <- "#2C3E50"

# Plot 1: Attrition rate by department
p1 <- ggplot(att_dept, aes(x=reorder(department, attrition_rate),
                            y=attrition_rate,
                            fill=ifelse(attrition_rate>25, red,
                                  ifelse(attrition_rate>18, yellow, green)))) +
  geom_bar(stat="identity", width=0.7) +
  geom_text(aes(label=paste0(attrition_rate,"%")),
            hjust=-0.1, size=3, color=dark) +
  scale_fill_identity() +
  coord_flip() +
  labs(title="Attrition Rate by Department",
       x="", y="Attrition Rate (%)",
       caption="Author: Mehak Pandey | pandeymehak.217@gmail.com") +
  theme_minimal() +
  theme(text=element_text(family="Arial", color=dark),
        plot.title=element_text(face="bold", size=12))

# Plot 2: Salary distribution by attrition status
employees$attrition_label <- ifelse(employees$attrition==1, "Left", "Stayed")
p2 <- ggplot(employees, aes(x=annual_salary/100000,
                              fill=attrition_label)) +
  geom_histogram(bins=30, alpha=0.7, position="identity") +
  scale_fill_manual(values=c("Left"=red, "Stayed"=green)) +
  labs(title="Salary Distribution: Left vs Stayed",
       x="Annual Salary (Lakh Rs)", y="Count", fill="Status") +
  theme_minimal() +
  theme(text=element_text(family="Arial", color=dark),
        plot.title=element_text(face="bold", size=12))

# Plot 3: Sprint velocity trend
sprint_trend <- sprints %>%
  filter(sprint_status=="Completed") %>%
  group_by(department, sprint_year) %>%
  summarise(avg_vel=round(mean(velocity),1), .groups="drop")

p3 <- ggplot(sprint_trend, aes(x=sprint_year, y=avg_vel,
                                color=department, group=department)) +
  geom_line(linewidth=1.2) +
  geom_point(size=3) +
  scale_color_brewer(palette="Set2") +
  labs(title="Sprint Velocity Trend by Department (2020-2024)",
       x="Year", y="Avg Velocity (Story Points)", color="Department") +
  theme_minimal() +
  theme(text=element_text(family="Arial", color=dark),
        plot.title=element_text(face="bold", size=12))

# Plot 4: Correlation heatmap
png("~/hr_project/outputs/correlation_heatmap.png",
    width=800, height=700, res=100)
corrplot(cor_matrix, method="color",
         col=colorRampPalette(c(red,"white",green))(200),
         tl.cex=0.8, tl.col=dark, addCoef.col="black",
         number.cex=0.6, title="Attrition Correlation Matrix",
         mar=c(0,0,2,0))
dev.off()

# Save combined plots
png("~/hr_project/outputs/hr_dashboard.png",
    width=1400, height=1000, res=120)
grid.arrange(p1, p2, p3, ncol=2, nrow=2,
             top=grid::textGrob("TechCorp HR Analytics Dashboard",
                                 gp=grid::gpar(fontsize=16, fontface="bold",
                                               col=dark, fontfamily="Arial")))
dev.off()

cat("Visualizations saved to outputs/ folder\n")
cat("\nAnalysis complete.\n")
cat("Author: Mehak Pandey | pandeymehak.217@gmail.com\n")
