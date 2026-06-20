from telethon.sync import TelegramClient, events
from telethon.sessions import StringSession
import os

# Получаем данные из переменных окружения
# Оборачиваем API_ID в int(), так как Telethon требует, чтобы это было число
API_ID = int(os.getenv('API_ID'))  
API_HASH = os.getenv('API_HASH')
SESSION_STRING = os.getenv('SESSION_STRING')  # Наша новая переменная

SOURCE_CHANNEL = [
    '@dt_5p', 
    '@bin_4p', 
    '@gate_5p',
    '@42777',
    '@yovssmashchat'
]

TARGET_CHANNEL = '@crscr1' 

# Создаем клиента с использованием StringSession
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

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
# При запуске теперь не будет требоваться ввод, так как данные есть в SESSION_STRING
client.start()
client.run_until_disconnected()
