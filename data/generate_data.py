#!/usr/bin/env python3
"""Generate a sample sales SQLite database for the MCP demo.

Run once before starting the server:
    python data/generate_data.py
"""
import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

random.seed(42)
DB = Path(__file__).parent / "sales.db"

PRODUCTS = [
    ("Aurora Laptop 14", "Electronics", 899.00),
    ("Nimbus Headphones", "Electronics", 149.00),
    ("Trailblaze Backpack", "Outdoors", 79.00),
    ("Everpour Water Bottle", "Outdoors", 29.00),
    ("Lumen Desk Lamp", "Home", 59.00),
    ("Cloudrest Pillow", "Home", 49.00),
    ("Velocity Running Shoes", "Apparel", 129.00),
    ("Atlas Denim Jacket", "Apparel", 119.00),
    ("Pulse Smartwatch", "Electronics", 249.00),
    ("Terra Plant Pot Set", "Home", 39.00),
]
REGIONS = ["Northeast", "Midwest", "South", "West"]


def main():
    if DB.exists():
        DB.unlink()
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute(
        """CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            order_date TEXT NOT NULL,
            product TEXT NOT NULL,
            category TEXT NOT NULL,
            region TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            total REAL NOT NULL
        )"""
    )
    start = date(2025, 1, 1)
    rows = []
    oid = 1
    day = start
    while day <= date(2026, 9, 30):
        for _ in range(random.randint(0, 6)):
            product, category, price = random.choice(PRODUCTS)
            qty = random.randint(1, 4)
            rows.append(
                (
                    oid,
                    day.isoformat(),
                    product,
                    category,
                    random.choice(REGIONS),
                    qty,
                    price,
                    round(qty * price, 2),
                )
            )
            oid += 1
        day += timedelta(days=1)
    cur.executemany("INSERT INTO orders VALUES (?,?,?,?,?,?,?,?)", rows)
    con.commit()
    n = cur.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    total = cur.execute("SELECT ROUND(SUM(total),2) FROM orders").fetchone()[0]
    con.close()
    print(f"Wrote {n} orders, ${total:,.2f} total revenue -> {DB}")


if __name__ == "__main__":
    main()
