import subprocess
import time
import os
import signal
import sys

# Переходим в папку с ботами
os.chdir('/private/var/mobile/Containers/Data/Application/B5CFE526-04C9-4E8E-B1B2-E9DB091FA7E7/Documents/tg_groq_bot')

print("🚀 Запускаем обоих ботов...")

# Запускаем receiver.py в фоне
receiver = subprocess.Popen(['python3', 'receiver.py'], 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE)

print("✅ Бот-приёмник запущен (PID: {})".format(receiver.pid))

time.sleep(2)

# Запускаем bot.py (основной бот)
print("🤖 Запускаем ИИ бота...")
subprocess.run(['python3', 'bot.py'])

# Если основной бот остановлен, убиваем и receiver
print("🛑 Останавливаем бота-приёмник...")
receiver.terminate()