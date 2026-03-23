import os
import asyncio
from threading import Thread
import gradio as gr
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from groq import AsyncGroq

# Получаем ключи
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Инициализация (с проверкой)
bot = Bot(token=BOT_TOKEN) if BOT_TOKEN else None
dp = Dispatcher(bot, storage=MemoryStorage()) if bot else None
groq_client = AsyncGroq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Бот запущен и готов к работе!🤖")

@dp.message_handler()
async def chat(message: types.Message):
    if not groq_client:
        await message.reply("Ошибка: API ключ Groq не настроен.")
        return
    try:
        res = await groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": message.text}]
        )
        await message.reply(res.choices[0].message.content)
    except Exception as e:
        print(f"Error: {e}")

def run_bot():
    if dp:
        print("Starting Telegram Bot...")
        executor.start_polling(dp, skip_updates=True)
    else:
        print("BOT_TOKEN not found!")

# Интерфейс для Hugging Face
with gr.Blocks() as demo:
    gr.Markdown("# AI Telegram Bot Status")
    gr.Markdown("Если этот Space запущен, значит бот должен быть онлайн.")

if __name__ == '__main__':
    # Запуск бота в отдельном потоке
    Thread(target=run_bot, daemon=True).start()
    # Запуск интерфейса
    demo.launch(server_name="0.0.0.0", server_port=7860)
