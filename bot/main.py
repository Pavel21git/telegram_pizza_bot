import asyncio
import logging
import os
import json
from collections import defaultdict

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

# ── базовая настройка ──────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)

ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(ENV_PATH)

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
if not BOT_TOKEN:
    raise RuntimeError("✗ BOT_TOKEN не найден. Проверь .env (формат BOT_TOKEN=...)")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ── данные меню + корзина ─────────────────────────────────────────────────────
with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "menu.json"), "r", encoding="utf-8") as f:
    MENU = json.load(f)  # список словарей: {"id": 1, "name": "...", "desc": "...", "price": 9.99}

MENU_BY_ID = {item["id"]: item for item in MENU}
CART = defaultdict(list)  # user_id -> [product_id, product_id, ...]

# ── хендлеры ───────────────────────────────────────────────────────────────────
@dp.message(Command("start"))
async def cmd_start(msg: types.Message):
    await msg.answer("Привет! Я бот-пиццерия 🍕. Готов принять заказ.\nКоманды:\n/menu — меню\n/cart — корзина")

@dp.message(Command("menu"))
async def cmd_menu(msg: types.Message):
    # Текст + одна общая клавиатура с кнопками «Добавить»
    text_lines = []
    kb_rows = []
    for item in MENU:
        text_lines.append(
            f"<b>#{item['id']}</b> — <b>{item['name']}</b>\n"
            f"{item['desc']}\n"
            f"<i>Цена:</i> <b>{item['price']:.2f} $</b>\n"
        )
        kb_rows.append([InlineKeyboardButton(text=f"➕ В корзину: {item['name']}", callback_data=f"add:{item['id']}")])

    kb = InlineKeyboardMarkup(inline_keyboard=kb_rows)
    await msg.answer("\n".join(text_lines), reply_markup=kb, parse_mode="HTML")

@dp.callback_query(lambda c: c.data and c.data.startswith("add:"))
async def on_add_to_cart(callback: types.CallbackQuery):
    pid = int(callback.data.split(":", 1)[1])
    uid = callback.from_user.id
    if pid in MENU_BY_ID:
        CART[uid].append(pid)
        # короткое всплывающее сообщение
        await callback.answer("Добавлено в корзину!", show_alert=False)
    else:
        await callback.answer("Такого товара нет 🤔", show_alert=True)

@dp.message(Command("cart"))
async def cmd_cart(msg: types.Message):
    uid = msg.from_user.id
    items = CART.get(uid, [])
    if not items:
        await msg.answer("🧺 Ваша корзина пуста.")
        return

    # посчитаем количество и сумму
    counts = defaultdict(int)
    for pid in items:
        counts[pid] += 1

    lines = []
    total = 0.0
    for pid, qty in counts.items():
        item = MENU_BY_ID.get(pid)
        if not item:
            continue
        subtotal = item["price"] * qty
        total += subtotal
        lines.append(f"{item['name']} × {qty} = {subtotal:.2f} $")

    lines.append("—" * 24)
    lines.append(f"ИТОГО: <b>{total:.2f} $</b>")
    await msg.answer("\n".join(lines), parse_mode="HTML")

# ── запуск ─────────────────────────────────────────────────────────────────────
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
