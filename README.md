# 🍕 Telegram Pizza Bot# 🍕 Telegram Pizza Bot

Дипломный проект по направлению **Python Developer (TeachMeSkills)**.  
Телеграм-бот для оформления заказов пиццы.  

---

## ✨ Функционал
- Просмотр меню (`/menu`)
- Добавление пиццы в корзину
- Просмотр корзины, очистка, оформление заказа
- Ввод телефона и адреса доставки
- Простая генерация номера заказа
- Сохранение заказов в базе данных **SQLite** 
- Возможность расширения проекта с помощью **Django / DRF**
- Подготовка к контейнеризации через **Docker**

---

## 🛠 Стек технологий
- Python 3.9+
- [aiogram 3](https://docs.aiogram.dev/)
- `python-dotenv`
- SQLite 
- Django + DRF 
- Docker 

---

## ## 📂 Структура проекта
```text
telegram_pizza_bot/
│── bot/
│   ├── main.py        # основной код бота
│   └── db.py          # заготовки для БД
│
│── data/
│   └── menu.json      # меню пицц
│
│── .env.example       # пример файла окружения
│── requirements.txt   # зависимости проекта
└── README.md          # документация
---

## 🔑 Переменные окружения
Создайте файл `.env` рядом с `.env.example` и укажите токен бота:
BOT_TOKEN=ваш_токен_от_BotFather

---

## 🚀 Запуск проекта локально

```bash
# Клонировать репозиторий
git clone https://github.com/Pavel21git/telegram_pizza_bot.git
cd telegram_pizza_bot

# Установить зависимости
pip install -r requirements.txt

# Запустить бота
python bot/main.py
📌 Контакты
Автор: Pavels Pankovs
GitHub: https://github.com/Pavel21git/telegram_pizza_bot

