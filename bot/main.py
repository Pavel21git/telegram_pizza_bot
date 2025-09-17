# bot/main.py
from __future__ import annotations

import os
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from dotenv import load_dotenv


# ---------- Пути / конфиг ----------
BASE_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BASE_DIR / ".env"
DATA_DIR = BASE_DIR / "data"
MENU_PATH = DATA_DIR / "menu.json"

load_dotenv(ENV_PATH)

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN не найден. Проверь .env и формат BOT_TOKEN=...")

# Бот и диспетчер
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()


# ---------- Данные ----------
def load_menu() -> List[Dict]:
    with open(MENU_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


MENU: List[Dict] = load_menu()
# Быстрый доступ по id
PIZZAS_BY_ID: Dict[int, Dict] = {int(p["id"]): p for p in MENU}
# Корзина в памяти: user_id -> список pizza_id
CART: Dict[int, List[int]] = defaultdict(list)


# ---------- Вспомогательные ----------
def cart_text(uid: int) -> Tuple[str, float]:
    """
    Возвращает текст корзины и сумму. Никогда не возвращает пустой текст.
    """
    items = CART.get(uid, [])
    if not items:
        return "Корзина пуста. Сначала отправьте /menu и добавьте пиццы.", 0.0

    lines: List[str] = []
    total = 0.0
    for pid in items:
        p = PIZZAS_BY_ID.get(pid)
        if not p:
            continue
        price = float(p.get("price", 0))
        total += price
        lines.append(f'{p.get("name", "Пицца")} — {price:.2f}$')

    text = "<b>Корзина</b>\n" + "\n".join(lines) + f"\n\n<b>Итого:</b> {total:.2f}$"
    return text, total


# ---------- FSM заказа ----------
class OrderForm(StatesGroup):
    phone = State()
    address = State()


async def begin_order(message: types.Message, uid: int, state: FSMContext) -> None:
    if not CART.get(uid):
        await message.answer("Корзина пуста. Сначала /menu ➜ добавьте пиццы.")
        return
    await message.answer("Введите телефон (например, +44 7000 000000):")
    await state.set_state(OrderForm.phone)


# ---------- Команды ----------
@dp.message(Command("start"))
async def cmd_start(message: types.Message) -> None:
    await message.answer("Привет! Я бот-пиццерия 🍕. Готов принять заказ.\nНапиши /menu")


@dp.message(Command("menu"))
async def cmd_menu(message: types.Message) -> None:
    # Показываем позиции меню
    for p in MENU:
        pid = int(p["id"])
        text = (
            f"<b>{p.get('name')}</b>\n"
            f"{p.get('desc')}\n"
            f"Цена: {float(p.get('price', 0)):.2f}$"
        )
        kb = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="➕ В корзину", callback_data=f"add:{pid}"
                    )
                ]
            ]
        )
        await message.answer(text, reply_markup=kb)

    # Кнопка «Корзина»
    kb_cart = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="🧺 Открыть корзину", callback_data="cart")]
        ]
    )
    await message.answer("Когда будете готовы — откройте корзину:", reply_markup=kb_cart)


@dp.message(Command("cart"))
async def cmd_cart(message: types.Message) -> None:
    text, _ = cart_text(message.from_user.id)
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="🧹 Очистить", callback_data="clear")],
            [types.InlineKeyboardButton(text="✅ Оформить заказ", callback_data="order")],
        ]
    )
    await message.answer(text, reply_markup=kb)


@dp.message(Command("order"))
async def cmd_order(message: types.Message, state: FSMContext) -> None:
    await begin_order(message, message.from_user.id, state)


# ---------- Callback-кнопки ----------
@dp.callback_query(F.data.startswith("add:"))
async def on_add(cb: types.CallbackQuery) -> None:
    try:
        pid = int(cb.data.split(":", 1)[1])
    except Exception:
        await cb.answer("Неверный товар", show_alert=True)
        return

    if pid not in PIZZAS_BY_ID:
        await cb.answer("Пицца не найдена", show_alert=True)
        return

    CART[cb.from_user.id].append(pid)
    await cb.answer("Добавлено в корзину ✅", show_alert=False)


@dp.callback_query(F.data == "cart")
async def on_cart(cb: types.CallbackQuery) -> None:
    text, _ = cart_text(cb.from_user.id)
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="🧹 Очистить", callback_data="clear")],
            [types.InlineKeyboardButton(text="✅ Оформить заказ", callback_data="order")],
        ]
    )
    await cb.message.answer(text or "Корзина пуста. Сначала /menu ➜ добавьте пиццы.", reply_markup=kb)
    await cb.answer()


@dp.callback_query(F.data == "clear")
async def on_clear(cb: types.CallbackQuery) -> None:
    CART.pop(cb.from_user.id, None)
    await cb.message.answer("Корзина очищена 🧹")
    await cb.answer()


@dp.callback_query(F.data == "order")
async def start_order_by_button(cb: types.CallbackQuery, state: FSMContext) -> None:
    await begin_order(cb.message, cb.from_user.id, state)
    await cb.answer()


# ---------- Шаги формы ----------
@dp.message(OrderForm.phone)
async def get_phone(message: types.Message, state: FSMContext) -> None:
    await state.update_data(phone=message.text.strip())
    await message.answer("Введите адрес доставки:")
    await state.set_state(OrderForm.address)


@dp.message(OrderForm.address)
async def get_address(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    phone = data.get("phone", "")
    address = message.text.strip()

    uid = message.from_user.id
    text, total = cart_text(uid)
    if not CART.get(uid):
        await message.answer("Корзина пуста. Заказ отменён.")
        await state.clear()
        return

    # Простейший номер заказа
    order_id = abs(hash((uid, phone, address))) % 1_000_000

    # Очищаем корзину
    CART.pop(uid, None)
    await state.clear()

    clean_text = text.replace("<b>Корзина</b>\n", "")
    await message.answer(
        f"✅ Заказ оформлен!\n"
        f"<b>Номер:</b> <code>{order_id}</code>\n"
        f"<b>Телефон:</b> {phone}\n"
        f"<b>Адрес:</b> {address}\n\n"
        f"{clean_text}"
    )
# ---------- Точка входа ----------
async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())