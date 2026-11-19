-- Metformin safety review: analysis queries (MySQL 8)
-- Run in MySQL Workbench. Select one query at a time and press Ctrl+Enter.
-- Tables are created by prepare.py:
--   reports   (primaryid, sex, age_yrs, age_band, fda_date, is_target, serious, died)
--   reactions (primaryid, pt)
-- is_target = 1 means metformin is the primary suspect drug in that report.

USE drugsafety;

-- Setup: indexes make the joins below much faster. Run once.
CREATE INDEX idx_reports_pid   ON reports (primaryid);
CREATE INDEX idx_reactions_pid ON reactions (primaryid);


-- Query 1. How many reports in total, and how many for metformin?
SELECT COUNT(*) AS all_reports,
       SUM(is_target) AS drug_reports
FROM reports;


-- Query 2. The 15 most reported reactions for metformin.
SELECT r.pt, COUNT(*) AS reports
FROM reactions r
JOIN reports p ON p.primaryid = r.primaryid
WHERE p.is_target = 1
GROUP BY r.pt
ORDER BY reports DESC
LIMIT 15;


-- Query 3. Who are the reports about? Age band and sex, with the share that were serious.
SELECT age_band, sex, COUNT(*) AS reports,
       ROUND(100 * AVG(serious), 1) AS pct_serious
FROM reports
WHERE is_target = 1
GROUP BY age_band, sex
ORDER BY age_band, sex;

-- Only if your tables were loaded before sex and age_band blanks were handled in prepare.py:
-- relabel NULL and 'nan' values once. The first line turns off Workbench's safe-update mode.
-- SET SQL_SAFE_UPDATES = 0;
-- UPDATE reports SET sex = 'UNK' WHERE sex IS NULL;
-- UPDATE reports SET age_band = 'Unknown' WHERE age_band IS NULL OR age_band = 'nan';


-- Query 4. How many were serious, and how many ended in death?
SELECT COUNT(*) AS total,
       SUM(serious) AS serious_reports,
       SUM(died) AS deaths
FROM reports
WHERE is_target = 1;


-- Query 5. Reports per month.
SELECT DATE_FORMAT(fda_date, '%Y-%m') AS month, COUNT(*) AS reports
FROM reports
WHERE is_target = 1
GROUP BY month
ORDER BY month;


-- Query 6. The comparison table behind the PRR.
-- For each reaction: a = metformin reports with it, c = reports for all other drugs with it.
-- Only reactions with at least 3 metformin reports are kept.
-- export.py writes this result to excel/results.xlsx, and the PRR is calculated there.
SELECT r.pt,
       CAST(SUM(p.is_target = 1) AS UNSIGNED) AS a,
       CAST(SUM(p.is_target = 0) AS UNSIGNED) AS c
FROM reactions r
JOIN reports p ON p.primaryid = r.primaryid
GROUP BY r.pt
HAVING SUM(p.is_target = 1) >= 3
ORDER BY a DESC
LIMIT 50;