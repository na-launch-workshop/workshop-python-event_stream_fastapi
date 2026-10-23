import sqlite3
from pathlib import Path

db = Path(__file__).parent / "customers.db"

customers = [
    ("Alice",   "Engineering", "Backend Developer",   "New York"),
    ("Bob",     "Product",     "Product Manager",     "Chicago"),
    ("Carlos",  "Engineering", "DevOps Engineer",     "Austin"),
    ("Dana",    "Design",      "UX Designer",         "Seattle"),
    ("Eve",     "Engineering", "Frontend Developer",  "Boston"),
    ("Frank",   "Sales",       "Account Executive",   "Denver"),
    ("Grace",   "Engineering", "Data Engineer",       "San Francisco"),
    ("Hiro",    "Product",     "Product Analyst",     "Los Angeles"),
]

conn = sqlite3.connect(db)
conn.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        name TEXT PRIMARY KEY,
        department TEXT,
        role TEXT,
        location TEXT
    )
""")
conn.executemany(
    "INSERT OR IGNORE INTO customers (name, department, role, location) VALUES (?, ?, ?, ?)",
    customers,
)
conn.commit()
print(f"Seeded {len(customers)} customers into {db}")
conn.close()
