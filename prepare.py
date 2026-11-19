import os
import pandas as pd
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.types import String

DRUG = "METFORMIN"      # your drug, in capital letters

def load(prefix):       # read one file type: DEMO, DRUG, REAC or OUTC
    name = [f for f in os.listdir("data/raw") if f.upper().startswith(prefix)][0]
    return pd.read_csv("data/raw/" + name, sep="$", dtype=str, encoding="latin-1", low_memory=False)

demo, drug, reac, outc = load("DEMO"), load("DRUG"), load("REAC"), load("OUTC")

# keep the latest version of each case
demo["caseversion"] = pd.to_numeric(demo["caseversion"])
demo = demo.sort_values(["caseid", "caseversion"]).drop_duplicates("caseid", keep="last")

# reports where the drug is the primary suspect (PS)
ps = drug[drug["role_cod"] == "PS"]
is_drug = (ps["prod_ai"].fillna("") + " " + ps["drugname"].fillna("")).str.upper().str.contains(DRUG, regex=False)
demo = demo[demo["primaryid"].isin(ps["primaryid"])].copy()

# flags: about your drug? serious? died?
demo["is_target"] = demo["primaryid"].isin(ps.loc[is_drug, "primaryid"]).astype(int)
demo["serious"] = demo["primaryid"].isin(outc["primaryid"]).astype(int)
demo["died"] = demo["primaryid"].isin(outc.loc[outc["outc_cod"] == "DE", "primaryid"]).astype(int)

# age in years (ages given in days or months are left blank) and age bands
demo["age_yrs"] = pd.to_numeric(demo["age"], errors="coerce").where(demo["age_cod"] == "YR")
demo["age_band"] = pd.cut(demo["age_yrs"], [0, 18, 45, 65, 75, 111], right=False,
                          labels=["0-17", "18-44", "45-64", "65-74", "75+"]).astype(str)
demo["fda_date"] = pd.to_datetime(demo["fda_dt"], format="%Y%m%d", errors="coerce")

reports = demo[["primaryid", "sex", "age_yrs", "age_band", "fda_date", "is_target", "serious", "died"]]
reactions = reac.loc[reac["primaryid"].isin(reports["primaryid"]), ["primaryid", "pt"]].drop_duplicates()
reactions["pt"] = reactions["pt"].str.upper().str.strip()
print("reports:", len(reports), "| for", DRUG + ":", reports["is_target"].sum())

# send to MySQL
engine = create_engine(f"mysql+pymysql://root:{quote_plus(os.environ['MYSQL_PWD'])}@localhost:3306/drugsafety")
reports.to_sql("reports", engine, if_exists="replace", index=False, dtype={"primaryid": String(20)})
reactions.to_sql("reactions", engine, if_exists="replace", index=False, dtype={"primaryid": String(20), "pt": String(255)})