# ============================================================
# JOB MARKET ANALYSIS — STEP 2: SQL ANALYSIS (SQLite)
# ============================================================

import pandas as pd
import sqlite3

# ── LOAD CLEANED DATA ────────────────────────────────────────
df = pd.read_csv("gsearch_jobs_cleaned.csv")

# ── CREATE SQLite DATABASE ───────────────────────────────────
conn = sqlite3.connect("job_market.db")
df.to_sql("jobs", conn, if_exists="replace", index=False)
print("✅ Data loaded into SQLite → table: jobs")
print(f"   Total rows: {len(df):,}")

def run_query(label, sql):
    print(f"\n{'='*60}")
    print(f"📊 {label}")
    print('='*60)
    result = pd.read_sql_query(sql, conn)
    print(result.to_string(index=False))
    return result

# ════════════════════════════════════════════════════════════
# QUERY 1 — Top 10 Most In-Demand Job Titles
# ════════════════════════════════════════════════════════════
q1 = run_query("Top 10 Most In-Demand Job Titles", """
    SELECT title,
           COUNT(*) AS job_count,
           ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM jobs), 2) AS pct
    FROM jobs
    GROUP BY title
    ORDER BY job_count DESC
    LIMIT 10;
""")

# ════════════════════════════════════════════════════════════
# QUERY 2 — Top 15 Companies Hiring
# ════════════════════════════════════════════════════════════
q2 = run_query("Top 15 Companies Hiring Data Analysts", """
    SELECT company_name,
           COUNT(*) AS postings
    FROM jobs
    WHERE company_name IS NOT NULL
    GROUP BY company_name
    ORDER BY postings DESC
    LIMIT 15;
""")

# ════════════════════════════════════════════════════════════
# QUERY 3 — Salary Statistics by Job Title
# ════════════════════════════════════════════════════════════
q3 = run_query("Salary Statistics by Job Title (Top 10 by Avg Salary)", """
    SELECT title,
           COUNT(*)                           AS postings,
           ROUND(AVG(salary_standardized), 0) AS avg_salary,
           ROUND(MIN(salary_standardized), 0) AS min_salary,
           ROUND(MAX(salary_standardized), 0) AS max_salary
    FROM jobs
    WHERE salary_standardized IS NOT NULL
    GROUP BY title
    HAVING postings >= 10
    ORDER BY avg_salary DESC
    LIMIT 10;
""")

# ════════════════════════════════════════════════════════════
# QUERY 4 — Remote vs On-Site Jobs
# ════════════════════════════════════════════════════════════
q4 = run_query("Remote vs On-Site Breakdown", """
    SELECT
        CASE
            WHEN work_from_home = 1 OR work_from_home = 'True' THEN 'Remote'
            ELSE 'On-Site / Hybrid'
        END AS work_type,
        COUNT(*) AS job_count,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM jobs), 2) AS pct
    FROM jobs
    GROUP BY work_type;
""")

# ════════════════════════════════════════════════════════════
# QUERY 5 — Top 10 Hiring States
# ════════════════════════════════════════════════════════════
q5 = run_query("Top 10 Hiring States", """
    SELECT state,
           COUNT(*) AS job_count
    FROM jobs
    WHERE state IS NOT NULL AND state != ''
    GROUP BY state
    ORDER BY job_count DESC
    LIMIT 10;
""")

# ════════════════════════════════════════════════════════════
# QUERY 6 — Monthly Hiring Trend
# ════════════════════════════════════════════════════════════
q6 = run_query("Monthly Hiring Trend", """
    SELECT posting_month,
           COUNT(*) AS postings
    FROM jobs
    WHERE posting_month IS NOT NULL AND posting_month != 'NaT'
    GROUP BY posting_month
    ORDER BY posting_month;
""")

# ════════════════════════════════════════════════════════════
# QUERY 7 — Job Schedule Type Distribution
# ════════════════════════════════════════════════════════════
q7 = run_query("Job Schedule Type Distribution", """
    SELECT schedule_type,
           COUNT(*) AS count,
           ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM jobs), 2) AS pct
    FROM jobs
    GROUP BY schedule_type
    ORDER BY count DESC;
""")

# ════════════════════════════════════════════════════════════
# QUERY 8 — Salary Rate Type (Hourly vs Yearly)
# ════════════════════════════════════════════════════════════
q8 = run_query("Salary Rate Type Breakdown", """
    SELECT salary_rate,
           COUNT(*)                           AS postings,
           ROUND(AVG(salary_standardized), 0) AS avg_annual_equivalent
    FROM jobs
    WHERE salary_rate IS NOT NULL AND salary_standardized IS NOT NULL
    GROUP BY salary_rate
    ORDER BY postings DESC;
""")

# ════════════════════════════════════════════════════════════
# QUERY 9 — Top Job Posting Platforms
# ════════════════════════════════════════════════════════════
q9 = run_query("Top Job Posting Platforms", """
    SELECT via AS platform,
           COUNT(*) AS postings
    FROM jobs
    WHERE via IS NOT NULL
    GROUP BY via
    ORDER BY postings DESC
    LIMIT 10;
""")

# ════════════════════════════════════════════════════════════
# QUERY 10 — Remote vs On-Site Salary Comparison
# ════════════════════════════════════════════════════════════
q10 = run_query("Remote vs On-Site Salary Comparison", """
    SELECT
        CASE
            WHEN work_from_home = 1 OR work_from_home = 'True' THEN 'Remote'
            ELSE 'On-Site / Hybrid'
        END AS work_type,
        COUNT(*)                           AS postings_with_salary,
        ROUND(AVG(salary_standardized), 0) AS avg_salary,
        ROUND(MIN(salary_standardized), 0) AS min_salary,
        ROUND(MAX(salary_standardized), 0) AS max_salary
    FROM jobs
    WHERE salary_standardized IS NOT NULL
    GROUP BY work_type;
""")

# ── SAVE ALL RESULTS ─────────────────────────────────────────
results = {
    "top_titles":      q1,  "top_companies":    q2,
    "salary_by_title": q3,  "remote_vs_onsite": q4,
    "top_states":      q5,  "monthly_trend":    q6,
    "schedule_type":   q7,  "salary_rate":      q8,
    "platforms":       q9,  "salary_work_type": q10,
}
for name, rdf in results.items():
    rdf.to_csv(f"sql_{name}.csv", index=False)

conn.close()
print("\n✅ All 10 SQL queries complete — results saved as CSVs")
print("✅ Database saved → job_market.db")