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

# 1. Указываем ТОЛЬКО названия самих чатов/каналов (без цифр через слеш)
SOURCE_CHANNELS = [
    '@arbionalerts', 
    '@uainvest_scanner', 
    '@yovssmashchat'
]

# Если нужно слушать не весь чат, а ТОЛЬКО конкретные топики (номера из ваших ссылок):
SOURCE_TOPICS = [7974, 20903, 7978, 7976, 7970, 7964, 23111, 12, 2134, 8332]

# 2. Указываем целевой чат и целевой топик раздельно
# В ссылках Telegram вида @c/4434633503/2 число 4434633503 — это ID чата. 
# Telethon требует, чтобы к ID супергрупп и каналов спереди добавлялось -100
TARGET_CHAT_ID = -1004434633503 
TARGET_TOPIC_ID = 2  # Цифра после последнего слеша

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def forward_message(event):
    # Проверяем, из нужного ли топика пришло сообщение (если это форум)
    # Если это обычный канал (не форум), это условие можно удалить
    if event.message.reply_to_msg_id not in SOURCE_TOPICS:
        # Если сообщение из другого топика — игнорируем его
        return 
        
    print(f"Поймали новое сообщение! Текст: {event.raw_text}")
    
    try:
        # Пересылаем сообщение, явно указывая ID нужного топика через reply_to
        await client.send_message(
            entity=TARGET_CHAT_ID, 
            message=event.message, 
            reply_to=TARGET_TOPIC_ID
        )
        print("Сообщение успешно переслано в целевой топик!")
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
