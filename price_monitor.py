import sqlite3
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Price & Anomaly Monitor")
DB_NAME = "prices.db"

# 1. Create two relational tables in SQLite
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                url TEXT UNIQUE,
                target_price REAL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                price REAL,
                checked_at TEXT,
                FOREIGN KEY(product_id) REFERENCES products(id)
            )
        """)

init_db()

# 2. Input validation models
class ProductCreate(BaseModel):
    name: str
    url: str
    target_price: float

class PriceLog(BaseModel):
    product_id: int
    current_price: float

# 3. Register a product to track
@app.post("/products")
def track_product(item: ProductCreate):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cur = conn.execute(
                "INSERT INTO products (name, url, target_price) VALUES (?, ?, ?)",
                (item.name, item.url, item.target_price)
            )
        return {"product_id": cur.lastrowid, "status": "Tracking started"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Product URL already tracked")

# 4. Log a new price and check if it is a genuine deal
@app.post("/log-price")
def log_scraped_price(data: PriceLog):
    with sqlite3.connect(DB_NAME) as conn:
        product = conn.execute(
            "SELECT name, target_price FROM products WHERE id = ?",
            (data.product_id,)
        ).fetchone()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        history = [r[0] for r in conn.execute(
            "SELECT price FROM price_history WHERE product_id = ?",
            (data.product_id,)
        ).fetchall()]

        conn.execute(
            "INSERT INTO price_history (product_id, price, checked_at) VALUES (?, ?, ?)",
            (data.product_id, data.current_price, datetime.now().isoformat())
        )

    avg_price = round(sum(history) / len(history), 2) if history else data.current_price
    is_real_deal = data.current_price <= product[1] and data.current_price <= avg_price

    return {
        "product": product[0],
        "current_price": data.current_price,
        "historical_avg": avg_price,
        "target_price": product[1],
        "verdict": "REAL DEAL ALERT!" if is_real_deal else "No genuine drop (or fake markup)"
    }

# 5. View full price timeline for a product
@app.get("/products/{product_id}/history")
def get_price_history(product_id: int):
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT price, checked_at FROM price_history WHERE product_id = ? ORDER BY id DESC",
            (product_id,)
        ).fetchall()
    return {"product_id": product_id, "history": [dict(r) for r in rows]}