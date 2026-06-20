from telethon.sync import TelegramClient, events
from time import ctime,sleep,time
from telethon import TelegramClient, events
import socks
import os
# Укажите свои данные
API_ID = os.getenv(API_ID')  # Замените на ваш API ID
API_HASH = os.getenv('API_HASH')  # Замените на ваш API Hash
SOURCE_CHANNEL = ['@dt_5p', 
    '@bin_4p', 
    '@gate_5p',
    '@bybit_5p','@yovssmashchat']
# Замените на @username или ID канала X
TARGET_CHANNEL = '@crscr1'  # Замените на @username или ID канала Y
# Создаем клиента

client = TelegramClient('session_name1', API_ID, API_HASH)

@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def forward_message(event):
    # 1. Простой и безопасный вывод в консоль для проверки
    print(f"Поймали новое сообщение! Текст: {event.raw_text}")
    
    # 2. Пересылка сообщения
    try:
        # Отправляем сообщение в целевой канал
        await client.send_message(TARGET_CHANNEL, event.message)
        print("Сообщение успешно переслано!")
    except Exception as e:
        print(f"Ошибка при пересылке: {e}")

print("Бот запущен...")
client.start()
client.run_until_disconnected()
