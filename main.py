from telethon import TelegramClient, events
from telethon.sessions import StringSession
import os
import sys

# 1. Получаем данные из Railway Variables
API_ID_ENV = 29138810
API_HASH = os.getenv('API_HASH')
SESSION_STRING = os.getenv('SESSION_STRING')

if not API_ID_ENV or not API_HASH:
    print("КРИТИЧЕСКАЯ ОШИБКА: API_ID или API_HASH не заданы в переменных Railway!", file=sys.stderr)
    sys.exit(1)

if not SESSION_STRING:
    print("КРИТИЧЕСКАЯ ОШИБКА: Переменная SESSION_STRING пустая!", file=sys.stderr)
    sys.exit(1)

API_ID = 29138810
API_HASH = API_HASH.strip()
SESSION_STRING = SESSION_STRING.strip()

SOURCE_CHANNEL = [
    '@dt_5p', 
    '@bin_4p', 
    '@gate_5p',
    '@bybit_5p',
    '@yovssmashchat'
]
TARGET_CHANNEL = '@crscr1' 

# 2. Создаем клиента
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def forward_message(event):
    print(f"Поймали новое сообщение! Текст: {event.raw_text}")
    try:
        await client.send_message(TARGET_CHANNEL, event.message)
        print("Сообщение успешно переслано!")
    except Exception as e:
        print(f"Ошибка при пересылке: {e}")

# 3. Асинхронный запуск
async def main():
    print("Инициализация клиента Telethon...")
    try:
        await client.connect()
        
        # Если строка сессии правильная, он пройдет эту проверку
        if not await client.is_user_authorized():
            print("КРИТИЧЕСКАЯ ОШИБКА: SESSION_STRING устарела или неверна!", file=sys.stderr)
            sys.exit(1)
            
        print("Бот успешно авторизован по String Session!")
        print("Бот запущен и слушает каналы...")
        await client.run_until_disconnected()
        
    except Exception as e:
        print(f"Непредвиденная ошибка при запуске клиента: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    client.loop.run_until_complete(main())
