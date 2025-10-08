# notebooks/crud.py
from pathlib import Path
import sqlite3
import pandas as pd
from shutil import copy2

THIS_DIR = Path(__file__).resolve().parent
DB_SRC = THIS_DIR.parent / "data" / "university_database.db"
DB_WORK = (
    THIS_DIR.parent / "data" / "university_database_working.db"
)  # mutate this copy
SQL_DIR = THIS_DIR  # .sql files live here

# make a working copy once (so the committed DB stays clean)
if not DB_WORK.exists():
    copy2(DB_SRC, DB_WORK)

conn = sqlite3.connect(DB_WORK.as_posix())


def run_sql_file(filename, params=None):
    q = (SQL_DIR / filename).read_text(encoding="utf-8").strip()
    if not q:
        raise ValueError(f"{filename} is empty.")
    if params:

        conn.execute(q, params)
    else:
        conn.executescript(q)
    conn.commit()


def qdf(query: str) -> pd.DataFrame:
    return pd.read_sql_query(query, conn)


print("Using DB:", DB_WORK)

# A) INSERT Duke Tech (2014)
print("\nA) INSERT Duke Tech (2014)")
print(
    "Rows in 2014 (before):",
    int(
        qdf("SELECT COUNT(*) AS n FROM university_rankings WHERE year=2014;").iloc[0, 0]
    ),
)
run_sql_file("insert_duke_tech_2014.sql")
print(
    "Rows in 2014 (after): ",
    int(
        qdf("SELECT COUNT(*) AS n FROM university_rankings WHERE year=2014;").iloc[0, 0]
    ),
)

# B) COUNT Japan in top 200 (2013)
print("\nB) COUNT Japan in top 200 (2013)")
res = qdf((SQL_DIR / "count_japan_top200_2013.sql").read_text())
print("Japan top-200, 2013:", int(res.iloc[0, 0]))

# C) UPDATE Oxford score +1.2 (2014)
print("\nC) UPDATE Oxford 2014 score +1.2")
before = qdf(
    """SELECT score FROM university_rankings
                WHERE institution='University of Oxford' AND year=2014 LIMIT 1;"""
)
print("Before:", None if before.empty else before.iloc[0, 0])
run_sql_file("update_oxford_2014.sql")
after = qdf(
    """SELECT score FROM university_rankings
               WHERE institution='University of Oxford' AND year=2014 LIMIT 1;"""
)
print("After: ", None if after.empty else after.iloc[0, 0])

# D) DELETE score < 45 in 2015
p = SQL_DIR / "delete_below45_2015.sql"
print("Delete SQL path:", p.resolve())
print("File size (bytes):", p.stat().st_size)
print("Preview:", repr(p.read_text()[:80]))

print("\nD) DELETE score < 45 in 2015")
b = qdf("SELECT COUNT(*) AS n FROM university_rankings WHERE year=2015 AND score < 45;")
print("To delete:", int(b.iloc[0, 0]))
run_sql_file("delete_below45_2015.sql")
a = qdf("SELECT COUNT(*) AS n FROM university_rankings WHERE year=2015 AND score < 45;")
print("Remaining:", int(a.iloc[0, 0]))

conn.close()
print("\nDone.")
