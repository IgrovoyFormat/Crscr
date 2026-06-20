from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import qrcode
import asyncio

API_ID = 29138810
API_HASH = 'API_HASH'

client = TelegramClient(StringSession(), API_ID, API_HASH)

async def generate_session_qr():
    await client.connect()
    if not await client.is_user_authorized():
        # Запрашиваем QR-логин
        qr_login = await client.qr_login()
        
        # Генерируем и выводим QR-код в консоль
        qr = qrcode.QRCode()
        qr.add_data(qr_login.url)
        # Выводим инвертированный QR-код (для темных терминалов)
        # Если код не читается телефоном, поменяй invert=True на invert=False
        qr.print_ascii(invert=True)
        
        print("\nОткрой приложение Telegram на телефоне.")
        print("Перейди в Настройки -> Устройства -> Подключить устройство.")
        print("Отсканируй этот QR-код!")
        
        # Ждем, пока пользователь отсканирует код
        await qr_login.wait()
        
    print("\nАвторизация успешна! Вот твоя String Session:")
    print("========================================")
    print(client.session.save())
    print("========================================")

with client:
    client.loop.run_until_complete(generate_session_qr())
