Metformin: one-drug safety review from FDA adverse event reports

Dashboard

I took one quarter of public FDA adverse event reports (FAERS), isolated the reports where metformin was the primary suspect drug, and asked which reactions are reported more often for metformin than for other drugs. The result is a MySQL database, an Excel results file and a one-page Power BI dashboard.

Voluntary reports show what people chose to report, not how often a reaction happens. A flag here is a lead for review, not proof that metformin caused anything.

What I found
1,364 metformin reports out of 421,332 in the quarter. 93% were marked serious. Median age was 67. 138 reports had a death outcome.
Lactic acidosis was the most reported reaction (454 reports) and had the highest signal (PRR 364.97). It is the reaction in metformin's boxed warning, so the method finds what is already known.
Acute kidney injury was second by count (318 reports, PRR 31.75). Kidney function is a known risk factor for metformin accumulation.
Euglycaemic diabetic ketoacidosis (77 reports, PRR 178.25) also flagged strongly. I did not check why. One possibility is that metformin is often taken with an SGLT2 inhibitor, and a combination product or co-reported drug could drive this. I would test it before saying anything about metformin itself.
Reports with unknown age (230) or unknown sex are a large share of the file, so the age and sex charts are incomplete.
Data
Source: FDA Adverse Event Reporting System quarterly ASCII files, [2026 Q3]. Public data from the FDA website.
Files used: DEMO (patient), DRUG (drugs), REAC (reactions), OUTC (outcomes).
The raw files are not in this repository because of their size. Download them from the FDA page and place them in data/raw/.
Method
Clean (Python, prepare.py). Keep the latest version of each case (caseversion per caseid). Mark a report as a metformin report when metformin is the primary suspect drug (role_cod = PS). Flag serious reports and deaths. Convert age to years and group it into bands. Fill missing sex as UNK.
Store (MySQL). Two tables, reports and reactions, in a database called drugsafety.
Analyse (SQL, sql/queries.sql). Six queries: totals, top reactions, age and sex split, serious and death counts, reports per month, and the reaction counts behind the PRR.
Export and calculate PRR (Python, Excel). export.py writes excel/results.xlsx with the reaction counts and totals. The PRR and the review flag are calculated there with Excel formulas.
Report (Power BI). One page: four headline numbers, a sex slicer, reports by age group and sex, the top 10 reactions, and a table of the highest PRR values.
How PRR is calculated

For each reaction:

a = metformin reports with the reaction
b = metformin reports without it
c = reports for all other drugs with the reaction
d = reports for all other drugs without it

PRR = (a / (a + b)) / (c / (c + d))

A reaction is flagged for review when PRR is at least 2 and there are at least 3 cases (the Evans rule). The dashboard table only shows reactions with at least 20 reports, so one or two cases cannot produce a large value.

Limitations
Voluntary reports are under-reported and uneven. Reports are more likely for serious or newly publicised events.
There is no count of how many people took metformin, so the numbers are not rates.
Metformin is used by people with diabetes, so some reactions come from the disease or other drugs rather than from metformin (confounding by indication).
The same event can be reported by more than one person. I kept the latest version of each case but did not match duplicates across cases.
PRR compares against all other drugs in the same quarter. It points at reactions to look at. It does not show cause.
A death outcome means a death was reported alongside the report, not that the drug caused it.
One quarter only. A signal that appears in one quarter should be checked in others.
How to run it

Requires Python 3.10 or later, MySQL 8, and Power BI Desktop (Windows).

bash
pip install pandas sqlalchemy pymysql cryptography openpyxl
Download the four FAERS files for the quarter and put them in data/raw/.
Create the database in MySQL: CREATE DATABASE drugsafety;
Set your MySQL password for this terminal session so it never sits in code.
PowerShell: $env:MYSQL_PWD = "your password"
Run python prepare.py, then python export.py.
Run the queries in sql/queries.sql in MySQL Workbench.
Open powerbi/metformin_safety.pbix. If it asks for credentials, choose the Database tab and enter the MySQL user and password.
Repository
data/raw/            FAERS files (not included)
sql/queries.sql      six analysis queries
prepare.py           clean and load to MySQL
export.py            write excel/results.xlsx
excel/results.xlsx   reaction counts and totals
powerbi/             metformin_safety.pbix
images/dashboard.png dashboard screenshot
What I would do next
Repeat the review across four quarters and check whether the same reactions keep flagging.
Separate reports where metformin appears with an SGLT2 inhibitor to see whether euglycaemic diabetic ketoacidosis changes.
Add the reporter type (health professional or consumer) to see whether the flags differ.
About

Prajwal Acharya, Pharm.D. This is a learning project in clinical data analytics. www.linkedin.com/in/prajwalacharya1205  | prajwalacharya2003@gmail.com