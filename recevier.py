import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# Токен бота-приёмника (НОВЫЙ бот, которого вы создали)
RECEIVER_BOT_TOKEN = "8797666617:AAHgoiwOqF03pCU5BwCgxcuPIU_unccVtcs"
# Ваш личный Telegram ID
ADMIN_ID = 6314769459

bot = Bot(token=RECEIVER_BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

@dp.message_handler()
async def forward_to_admin(message: types.Message):
    """Пересылает всё админу"""
    if message.from_user.id != ADMIN_ID:
        # Если пишет кто-то другой, пересылаем админу
        await bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    else:
        # Если пишет сам админ, просто отвечаем
        await message.reply("✅ Бот работает, логи приходят")

if __name__ == '__main__':
    print("Бот-приёмник запущен...")
    executor.start_polling(dp, skip_updates=True)