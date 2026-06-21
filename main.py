'''from telethon import TelegramClient, events
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
    client.loop.run_until_complete(main())'''
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import os
import sys
import re  # Для очистки ссылок

# --- 1. Получаем данные из Railway Variables ---
API_ID_ENV = 29138810
API_HASH = os.getenv('API_HASH')
SESSION_STRING = os.getenv('SESSION_STRING')

API_ID = 29138810
API_HASH = API_HASH.strip()
SESSION_STRING = SESSION_STRING.strip()

# --- 2. Настройка каналов и топиков ---
# Список каналов, которые мы слушаем
SOURCE_CHANNELS = [
    '@arbionalerts', 
    '@uainvest_scanner', 
    '@yovssmashchat'
]

# Разделяем исходные топики на две группы
SOURCE_TOPICS_GROUP_1 = [7974, 20903, 7978, 7976, 7970]
SOURCE_TOPICS_GROUP_2 = [7964, 23111, 12, 2134, 8332]

# Целевой чат для обеих групп один и тот же
TARGET_CHAT_ID = -1004434633503 

# Целевые топики назначения
TARGET_TOPIC_1 = 2  # Куда слать из первой группы
TARGET_TOPIC_2 = 1  # Куда слать из второй группы

# Создаем клиента Telethon
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def forward_message(event):
    # Узнаем ID топика, из которого пришло сообщение
    incoming_topic = getattr(event.message, 'reply_to_msg_id', None)
    
    # Переменная для определения, в какой топик отправлять
    destination_topic = None
    
    # Проверяем, к какой группе относится пришедший топик
    if incoming_topic in SOURCE_TOPICS_GROUP_1:
        destination_topic = TARGET_TOPIC_1
    elif incoming_topic in SOURCE_TOPICS_GROUP_2:
        destination_topic = TARGET_TOPIC_2
    else:
        # Если сообщение пришло из топика, которого нет в списках — игнорируем его
        return 

    # Достаем текст сообщения
    text = event.text or ""
    
    if text:
        # Убираем ссылки (http:// и https://)
        text = re.sub(r'https?://\S+', '', text)
        # Убираем только символ решетки #
        text = text.replace('#', '')
        # Очищаем лишние пробелы по краям
        text = text.strip()

    print(f"Поймали сообщение из топика {incoming_topic}. Направляем в топик {destination_topic}.")
    
    try:
        # Отправляем очищенный текст в динамически определенный топик
        # file=event.media сохраняет картинки/видео, если они были в посте
        await client.send_message(
            entity=TARGET_CHAT_ID, 
            message=text, 
            reply_to=destination_topic,
            file=event.media 
        )
        print(f"Успешно переслано в топик {destination_topic}!")
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")

# --- 3. Асинхронный запуск бота ---
async def main():
    print("Инициализация клиента Telethon...")
    try:
        await client.connect()
        
        if not await client.is_user_authorized():
            print("КРИТИЧЕСКАЯ ОШИБКА: SESSION_STRING устарела или неверна!", file=sys.stderr)
            sys.exit(1)
            
        print("Бот успешно запущен!")
        print(f"Слушает топики группы 1 -> шлет в топик {TARGET_TOPIC_1}")
        print(f"Слушает топики группы 2 -> шлет в топик {TARGET_TOPIC_2}")
        
        await client.run_until_disconnected()
        
    except Exception as e:
        print(f"Непредвиденная ошибка при работе бота: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    client.loop.run_until_complete(main())
