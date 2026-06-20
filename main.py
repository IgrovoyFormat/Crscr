from telethon import TelegramClient, events
from telethon.sessions import StringSession
import os
import sys

# 1. Проверяем переменные окружения
API_ID_ENV = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
SESSION_STRING = os.getenv('SESSION_STRING')

if not API_ID_ENV or not API_HASH:
    print("КРИТИЧЕСКАЯ ОШИБКА: API_ID или API_HASH не заданы в переменных Railway!", file=sys.stderr)
    sys.exit(1)

if not SESSION_STRING:
    print("КРИТИЧЕСКАЯ ОШИБКА: Переменная SESSION_STRING пустая!", file=sys.stderr)
    sys.exit(1)

try:
    API_ID = int(API_ID_ENV.strip())
except ValueError:
    print(f"КРИТИЧЕСКАЯ ОШИБКА: API_ID должен быть числом, а получено: '{API_ID_ENV}'", file=sys.stderr)
    sys.exit(1)

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

# Создаем клиента (импорт теперь обычный, без .sync)
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def forward_message(event):
    print(f"Поймали новое сообщение! Текст: {event.raw_text}")
    try:
        await client.send_message(TARGET_CHANNEL, event.message)
        print("Сообщение успешно переслано!")
    except Exception as e:
        print(f"Ошибка при пересылке: {e}")

# Заворачиваем запуск в правильную асинхронную функцию
async def main():
    print("Инициализация клиента Telethon...")
    try:
        # Подключаемся к серверам (теперь с await)
        await client.connect()
        
        # Проверяем валидность нашей сессии
        if not await client.is_user_authorized():
            print("КРИТИЧЕСКАЯ ОШИБКА: Предоставленная SESSION_STRING не авторизована или устарела!", file=sys.stderr)
            sys.exit(1)
            
        print("Бот успешно авторизован по String Session!")
        print("Бот запущен и слушает каналы...")
        
        # Запускаем бесконечное ожидание сообщений
        await client.run_until_disconnected()
        
    except Exception as e:
        print(f"Непредвиденная ошибка при запуске клиента: {e}", file=sys.stderr)
        sys.exit(1)

# Стандартная точка входа для запуска
if __name__ == '__main__':
    client.loop.run_until_complete(main())
