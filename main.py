'''from telethon import TelegramClient, events
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
    client.loop.run_until_complete(main())'''
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import os
import sys
import re

# --- 1. Получаем данные из Railway Variables ---
API_HASH = os.getenv('API_HASH')
SESSION_STRING = os.getenv('SESSION_STRING')

API_ID = 29138810
API_HASH = API_HASH.strip()
SESSION_STRING = SESSION_STRING.strip()

# --- 2. Настройка каналов и топиков ---
# Все каналы-источники, которые слушает бот
SOURCE_CHANNELS = [
    '@arbionalerts', '@uainvest_scanner', '@bin_4p', '@tracervarikteat', 
    '@bybit_5p', '@dt_5pf', '@gate_5p', '@dt_12pf', '@g_12p', '@bin_9p', 
    '@hl_11p', '@bb_10p', '@okx_12p', '@bin_22p', '@gate_8p', '@dt_50p', 
    '@hl_50p', '@g_50p', '@aster_50p', '@bingx_50p', '@okx_50p'
]

# Единый целевой чат
TARGET_CHAT_ID = -1004434633503 

# Создаем клиента Telethon
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def forward_message(event):
    # 1. Получаем юзернейм
    sender = getattr(event.chat, 'username', '')
    if sender:
        sender = sender.lower()
        
    # 2. Узнаем ID топика
    incoming_topic = getattr(event.message, 'reply_to_msg_id', None)
    
    # --- БЛОК ДИАГНОСТИКИ (Выводит в логи Railway всё, что видит бот) ---
    print("=========================================")
    print("🔔 ПОЙМАЛИ КАКОЕ-ТО СООБЩЕНИЕ!")
    print(f"Имя канала (sender): '{sender}'")
    print(f"ID чата: {event.chat_id}")
    print(f"ID топика: {incoming_topic}")
    print("=========================================")
    # -------------------------------------------------------------------

    destination_topic = None
    needs_cleaning = False

    # А) Проверяем форумы
    if sender == 'uainvest_scanner' and incoming_topic == 8332:
        destination_topic = 180
    elif sender == 'uainvest_scanner' and incoming_topic == 23111:
        destination_topic = 164
    elif sender == 'uainvest_scanner' and incoming_topic == 12:
        destination_topic = 155
    elif sender == 'arbionalerts' and incoming_topic == 7976:
        destination_topic = 158
        needs_cleaning = True
    elif sender == 'arbionalerts' and incoming_topic == 7966:
        destination_topic = 155
        needs_cleaning = True

    # Б) Проверяем обычные каналы
    elif sender in ['dt_50p', 'hl_50p', 'g_50p', 'aster_50p', 'bingx_50p', 'okx_50p']:
        destination_topic = 211
    elif sender == 'hl_11p':
        destination_topic = 2
    elif sender == 'okx_12p':
        destination_topic = 196
    elif sender in ['dt_5pf', 'dt_12pf']:
        destination_topic = 188
    elif sender in ['gate_5p', 'g_12p']:
        destination_topic = 190
    elif sender == 'tracervarikteat':
        destination_topic = 186
    elif sender in ['bybit_5p', 'bb_10p']:
        destination_topic = 184

    if destination_topic is None:
        print("❌ Сообщение проигнорировано (не подошло под правила).")
        return

    print(f"✅ Правило сработало! Отправляем в топик {destination_topic}...")
    
    try:
        if needs_cleaning:
            text = event.text or ""
            if text:
                text = re.sub(r'https?://\S+', '', text) 
                text = text.replace('#', '')             
                text = text.strip()
            
            await client.send_message(entity=TARGET_CHAT_ID, message=text, reply_to=destination_topic, file=event.media)
        else:
            await client.send_message(entity=TARGET_CHAT_ID, message=event.message, reply_to=destination_topic)
            
        print("Успешно отправлено!")
    except Exception as e:
        print(f"Ошибка при отправке: {e}")

    # --- 4. ОБРАБОТКА И ОТПРАВКА ---
    print(f"Поймали сообщение от {sender} (топик {incoming_topic}). Отправляем в топик {destination_topic}...")
    
    try:
        if needs_cleaning:
            # Если это тот самый arbionalerts, чистим текст
            text = event.text or ""
            if text:
                text = re.sub(r'https?://\S+', '', text) # Удаляем ссылки
                text = text.replace('#', '')             # Удаляем решетки
                text = text.strip()
            
            # Отправляем очищенный текст
            await client.send_message(
                entity=TARGET_CHAT_ID, 
                message=text, 
                reply_to=destination_topic,
                file=event.media 
            )
            print("Успешно очищено и отправлено!")
            
        else:
            # Если канал другой — отправляем сообщение в целевой топик как есть (со всеми ссылками)
            await client.send_message(
                entity=TARGET_CHAT_ID, 
                message=event.message, 
                reply_to=destination_topic
            )
            print("Успешно отправлено без изменений!")
            
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")

# --- 5. Асинхронный запуск бота ---
async def main():
    print("Инициализация клиента Telethon...")
    try:
        await client.connect()
        
        if not await client.is_user_authorized():
            print("КРИТИЧЕСКАЯ ОШИБКА: SESSION_STRING устарела или неверна!", file=sys.stderr)
            sys.exit(1)
            
        print("Бот успешно запущен и работает по новым правилам маршрутизации!")
        await client.run_until_disconnected()
        
    except Exception as e:
        print(f"Непредвиденная ошибка при работе бота: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    client.loop.run_until_complete(main())
