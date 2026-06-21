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
    '@arbionalerts', '@uainvest_scanner', '@bin_4p', '@tracervarikteat', 
    '@bybit_5p', 
    -1001234567890,  # ВАЖНО: Замените на реальный ID канала @dt_5pf
    '@gate_5p', 
    -1009876543210,  # ВАЖНО: Замените на реальный ID канала @dt_12pf
    '@g_12p', '@bin_9p', '@hl_11p', '@bb_10p', '@okx_12p', '@bin_22p', 
    '@gate_8p', '@dt_50p', '@hl_50p', '@g_50p', '@aster_50p', 
    '@bingx_50p', '@okx_50p'
]

TARGET_CHAT_ID = -1004434633503 

# Создаем клиента Telethon
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def forward_message(event):
    sender = getattr(event.chat, 'username', '')
    if sender:
        sender = sender.lower()
        
    chat_id = event.chat_id
    incoming_topic = getattr(event.message, 'reply_to_msg_id', None)
    
    destination_topic = None
    needs_cleaning = False  

    # --- 3. ЛОГИКА МАРШРУТИЗАЦИИ ---
    
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

    elif sender in ['dt_50p', 'hl_50p', 'g_50p', 'aster_50p', 'bingx_50p', 'okx_50p']:
        destination_topic = 211
    elif sender == 'hl_11p':
        destination_topic = 2
    elif sender == 'okx_12p':
        destination_topic = 196
    elif sender in ['gate_5p', 'g_12p']:
        destination_topic = 190
    elif sender == 'tracervarikteat':
        destination_topic = 186
    elif sender in ['bybit_5p', 'bb_10p']:
        destination_topic = 184
    elif sender in ['bin_4p', 'bin_9p']:
        destination_topic = 1
        
    elif chat_id in [-1001234567890, -1009876543210]: 
        destination_topic = 188

    if destination_topic is None:
        return

    # --- 4. ОБРАБОТКА И ОТПРАВКА ---
    print(f"Поймали сообщение от {sender or chat_id} (топик {incoming_topic}). Отправляем в топик {destination_topic}...")
    
    try:
        if needs_cleaning:
            text = event.text or ""
            if text:
                # 1. Удаляем слова Scanner: и Trader: (независимо от больших/маленьких букв)
                text = re.sub(r'(?i)Scanner:|Trader:', '', text)
                
                # 2. Удаляем ЛЮБЫЕ ссылки (включая t.me, http://, https://)
                text = re.sub(r'https?://[^\s]+', '', text) 
                
                # 3. Удаляем символ решетки #
                text = text.replace('#', '')             
                
                # 4. Наводим красоту: убираем пустые "дыры" в тексте, оставшиеся после удаления ссылок
                text = re.sub(r'^[ \t]+$', '', text, flags=re.MULTILINE) # стираем пробелы на пустых строках
                text = re.sub(r'\n{3,}', '\n\n', text) # сжимаем лишние переносы строк в один абзац
                text = text.strip()
            
            await client.send_message(
                entity=TARGET_CHAT_ID, 
                message=text, 
                reply_to=destination_topic,
                file=event.media 
            )
            print("Успешно очищено (без ссылок и слов Scanner/Trader) и отправлено!")
            
        else:
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
            
        print("Бот успешно запущен и работает!")
        await client.run_until_disconnected()
        
    except Exception as e:
        print(f"Непредвиденная ошибка при работе бота: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    client.loop.run_until_complete(main())
