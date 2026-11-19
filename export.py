import os
import pandas as pd
from urllib.parse import quote_plus
from sqlalchemy import create_engine

engine = create_engine(f"mysql+pymysql://root:{quote_plus(os.environ['MYSQL_PWD'])}@localhost:3306/drugsafety")

top = pd.read_sql("""
    SELECT r.pt,
           CAST(SUM(p.is_target = 1) AS UNSIGNED) AS a,
           CAST(SUM(p.is_target = 0) AS UNSIGNED) AS c
    FROM reactions r JOIN reports p ON p.primaryid = r.primaryid
    GROUP BY r.pt HAVING SUM(p.is_target = 1) >= 3
    ORDER BY a DESC LIMIT 50
""", engine)

totals = pd.read_sql("""
    SELECT CAST(SUM(is_target = 1) AS UNSIGNED) AS target_reports,
           CAST(SUM(is_target = 0) AS UNSIGNED) AS other_reports
    FROM reports
""", engine)

os.makedirs("excel", exist_ok=True)
with pd.ExcelWriter("excel/results.xlsx") as xw:
    top.to_excel(xw, sheet_name="reactions", index=False)
    totals.to_excel(xw, sheet_name="totals", index=False)
print(top.head())