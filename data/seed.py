import sqlite3
from pathlib import Path

db = Path(__file__).parent / "appliances.db"

appliances = [
    ("Refrigerator",             1.2),
    ("Air Conditioner",          3.5),
    ("Electric Vehicle Charger", 9.6),
    ("Washing Machine",          1.8),
    ("Tumble Dryer",             4.5),
    ("Dishwasher",               1.4),
    ("Electric Oven",            2.3),
    ("Electric Water Heater",    4.0),
    ("Laptop",                   0.05),
    ("LED TV",                   0.1),
]

conn = sqlite3.connect(db)
conn.execute("""
    CREATE TABLE IF NOT EXISTS appliances (
        name      TEXT PRIMARY KEY,
        daily_kwh REAL NOT NULL
    )
""")
conn.executemany(
    "INSERT OR IGNORE INTO appliances (name, daily_kwh) VALUES (?, ?)",
    appliances,
)
conn.commit()
print(f"Seeded {len(appliances)} appliances into {db}")
conn.close()
