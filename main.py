import random
import sqlite3
import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

conn = sqlite3.connect("data.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT UNIQUE,
    used INTEGER DEFAULT 0
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS plank (
    date TEXT,
    seconds INTEGER
)
""")

conn.commit()

@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer(
        "Salom 👋\n\n"
        "Men sening kunlik vazifalar botingman.\n\n"
        "Buyruqlar:\n"
        "/soz_qoshish so‘z\n"
        "/planka soniya\n"
        "/bugun"
    )

@dp.message(Command("soz_qoshish"))
async def add_word(msg: types.Message):
    word = msg.text.replace("/soz_qoshish", "").strip()
    if not word:
        await msg.answer("❗ So‘z yoz.")
        return
    try:
        cur.execute("INSERT INTO words(word) VALUES(?)", (word,))
        conn.commit()
        await msg.answer(f"✅ So‘z qo‘shildi: {word}")
    except:
        await msg.answer("⚠️ Bu so‘z oldin bor.")

@dp.message(Command("planka"))
async def plank(msg: types.Message):
    try:
        sec = int(msg.text.split()[1])
        cur.execute("INSERT INTO plank VALUES(?,?)",
                    (datetime.now().date(), sec))
        conn.commit()
        await msg.answer(f"🧘 Planka: {sec} soniya")
    except:
        await msg.answer("❗ /planka 90 ko‘rinishida yoz.")

@dp.message(Command("bugun"))
async def today(msg: types.Message):
    await msg.answer("📊 Bugungi statistika hozircha minimal versiya.")

async def send_daily_words():
    cur.execute("SELECT word FROM words WHERE used=0")
    all_words = cur.fetchall()
    if len(all_words) < 15:
        return

    selected = random.sample(all_words, 15)
    text = "📅 Bugungi vazifalar\n\n🧠 So‘zlar:\n"
    for i, w in enumerate(selected, 1):
        text += f"{i}. {w[0]}\n"
        cur.execute("UPDATE words SET used=1 WHERE word=?", (w[0],))
    conn.commit()

    await bot.send_message(chat_id=ADMIN_ID, text=text)

async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_daily_words, "cron", hour=8, minute=0)
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
