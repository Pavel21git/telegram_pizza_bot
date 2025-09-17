# bot/db.py
from __future__ import annotations
import aiosqlite
from typing import Dict, List

DB_PATH = "bot/db.sqlite3"

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS pizzas (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    description TEXT NOT NULL,
    price       REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    phone      TEXT NOT NULL,
    address    TEXT NOT NULL,
    total      REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_items (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id  INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    pizza_id  INTEGER NOT NULL REFERENCES pizzas(id),
    qty       INTEGER NOT NULL,
    price     REAL NOT NULL
);
"""

async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(SCHEMA_SQL)
        await db.commit()

async def upsert_pizzas_from_menu(menu: List[dict]) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        for item in menu:
            await db.execute(
                """
                INSERT INTO pizzas(id, name, description, price)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name=excluded.name,
                    description=excluded.description,
                    price=excluded.price
                """,
                (item["id"], item["name"], item["desc"], float(item["price"]))
            )
        await db.commit()

async def get_pizzas_by_ids(ids: List[int]) -> Dict[int, dict]:
    if not ids:
        return {}
    qs = ",".join("?" for _ in ids)
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(f"SELECT * FROM pizzas WHERE id IN ({qs})", ids)
        rows = await cur.fetchall()
    return {row["id"]: dict(row) for row in rows}

async def create_order(user_id: int, phone: str, address: str, items: Dict[int, int]) -> int:
    # items: {pizza_id: qty}
    if not items:
        raise ValueError("Корзина пуста")

    pizzas = await get_pizzas_by_ids(list(items.keys()))
    total = 0.0
    for pid, qty in items.items():
        total += float(pizzas[pid]["price"]) * qty

    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO orders(user_id, phone, address, total) VALUES (?, ?, ?, ?)",
            (user_id, phone, address, total)
        )
        order_id = cur.lastrowid

        for pid, qty in items.items():
            await db.execute(
                "INSERT INTO order_items(order_id, pizza_id, qty, price) VALUES (?, ?, ?, ?)",
                (order_id, pid, qty, float(pizzas[pid]["price"]))
            )
        await db.commit()
    return order_id
