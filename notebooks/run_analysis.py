from pathlib import Path
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# ---- Paths (assumes this file is in notebooks/) ----
THIS_DIR = Path(__file__).resolve().parent
DB_PATH = THIS_DIR.parent / "data" / "university_database.db"
SQL_DIR = THIS_DIR

# For VS Code test runs
# THIS_DIR = Path.cwd()  # current working directory (notebooks/)
# DB_PATH = THIS_DIR / "data" / "university_database.db"
# SQL_DIR = THIS_DIR  # SQL files are in the same folder as this notebook/script

print("Current working directory:", THIS_DIR)
print("Database path:", DB_PATH)
print("SQL directory:", SQL_DIR)

# ---- 1) Connect (read/write) ----
conn = sqlite3.connect(DB_PATH.as_posix())

# ---- 2) Quick summaries ----
print("Tables:")
print(
    pd.read_sql_query(
        'SELECT name FROM sqlite_master WHERE type="table" ORDER BY name;', conn
    )
)

print("\nSchema for university_rankings:")
print(pd.read_sql_query('PRAGMA table_info("university_rankings");', conn))

print("\nRow count:")
print(pd.read_sql_query("SELECT COUNT(*) AS n_rows FROM university_rankings;", conn))

# Find Top5 Universities by score across years and their scores

print("\nTop 5 by score every year:")
query = """
SELECT year, world_rank, institution, score
FROM (
    SELECT year, world_rank, institution, score,
           ROW_NUMBER() OVER (PARTITION BY year ORDER BY score DESC) AS rank_in_year
    FROM university_rankings
)
WHERE rank_in_year <= 5
ORDER BY year, rank_in_year;
"""

df_top5 = pd.read_sql_query(query, conn)
print(df_top5)


# ---- 3) Simple plots ----
df = pd.read_sql_query("SELECT * FROM university_rankings;", conn)

# Count of Universities by country (top 10)
country_counts = df["country"].value_counts().head(10)
country_counts.plot(kind="bar", title="Top 10 Countries by Row Count")
plt.tight_layout()
plt.savefig("notebooks/top10_countries.png", dpi=150)
plt.show()


# Average score by year
avg_by_year = df.groupby("year", as_index=False)["score"].mean()
avg_by_year["year"] = avg_by_year["year"].astype(int)  # ensure integers

fig, ax = plt.subplots()
ax.plot(avg_by_year["year"], avg_by_year["score"])
ax.set_xticks(sorted(avg_by_year["year"].unique()))  # show only whole years

ax.set_title("Average Score by Year")
ax.set_xlabel("Year")
ax.set_ylabel("Avg Score")
fig.tight_layout()
plt.savefig("notebooks/avg_score_by_year.png", dpi=150)
plt.show()


# ---- 4) Close ----
conn.close()
print("\nDone.")
