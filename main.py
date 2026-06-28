from telethon import TelegramClient, events
from telethon.sessions import StringSession
import os
import sys
import re

# --- 1. Получаем данные из Railway Variables ---
API_ID = 29138810
API_HASH = os.getenv('API_HASH')
SESSION_STRING = os.getenv('SESSION_STRING')

API_HASH = API_HASH.strip()
SESSION_STRING = SESSION_STRING.strip()

SOURCE_CHANNELS = [
    '@arbionalerts',
    '@uainvest_scanner',
    '@bin_4p',
    '@tracervarikteat',
    '@bybit_5p',
    '@mexc_5pf',
    '@gate_5p',
    '@mexc_12pf',
    '@g_12p',
    '@bin_9p',
    '@hl_11p',
    '@bb_10p',
    '@okx_12p',
    '@bin_22p',
    '@gate_8p',
    '@dt_50p',
    '@hl_50p',
    '@g_50p',
    '@aster_50p',
    '@bingx_50p',
    '@okx_50p'
]

TARGET_CHAT_ID = -1004434633503

client = TelegramClient(
    StringSession(SESSION_STRING),
    API_ID,
    API_HASH
)


ROUTES = {
('uainvest_scanner',8332):(180,False),('uainvest_scanner',23111):(164,False),('uainvest_scanner',12):(155,False),
('arbionalerts',7976):(158,True),('arbionalerts',7966):(155,True)}
TOPIC_BY_SENDER={'dt_50p':211,'hl_50p':211,'g_50p':211,'aster_50p':211,'bingx_50p':211,'okx_50p':211,'hl_11p':1,'okx_12p':1,'gate_5p':190,'g_12p':190,'tracervarikteat':186,'bybit_5p':184,'bb_10p':184,'bin_4p':1,'bin_9p':1,'mexc_5pf':188,'mexc_12pf':188}
EXCHANGE_BY_SENDER={'bin_4p':'binance','bin_9p':'binance','mexc_5pf':'mexc','mexc_12pf':'mexc','dt_50p':'mexc','bybit_5p':'bybit','bb_10p':'bybit','gate_5p':'gate','g_12p':'gate','g_50p':'gate','hl_11p':'hyperliquid','hl_50p':'hyperliquid','okx_12p':'okx','okx_50p':'okx','aster_50p':'aster','bingx_50p':'bingx'}
EXCHANGE_URLS={'binance':'https://www.binance.com/en/futures/{token}USDT','mexc':'https://futures.mexc.com/exchange/{token}_USDT','bybit':'https://www.bybit.com/trade/usdt/{token}USDT','gate':'https://www.gate.io/futures_trade/USDT/{token}_USDT','hyperliquid':'https://app.hyperliquid.xyz/trade/{token}','okx':'https://www.okx.com/trade-swap/{token}-usdt-swap','aster':'https://www.asterdex.com/en/trade/{token}_USDT','bingx':'https://bingx.com/en/futures/forward/{token}USDT'}


@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def forward_message(event):
    sender = getattr(event.chat, 'username', '')

    if sender:
        sender = sender.lower()

    chat_id = event.chat_id
    incoming_topic = getattr(event.message, 'reply_to_msg_id', None)

    destination_topic = None
    needs_strict_cleaning = False

    # --- ЛОГИКА МАРШРУТИЗАЦИИ ---

    if sender == 'uainvest_scanner' and incoming_topic == 8332:
        destination_topic = 180

    elif sender == 'uainvest_scanner' and incoming_topic == 23111:
        destination_topic = 164

    elif sender == 'uainvest_scanner' and incoming_topic == 12:
        destination_topic = 155

    elif sender == 'arbionalerts' and incoming_topic == 7976:
        destination_topic = 158
        needs_strict_cleaning = True

    elif sender == 'arbionalerts' and incoming_topic == 7966:
        destination_topic = 155
        needs_strict_cleaning = True

    elif sender in [
        'dt_50p',
        'hl_50p',
        'g_50p',
        'aster_50p',
        'bingx_50p',
        'okx_50p'
    ]:
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

    elif sender in ['mexc_5pf', 'mexc_12pf']:
        destination_topic = 188

    if destination_topic is None:
        return

    print(
        f"Поймали сообщение от {sender or chat_id} "
        f"(топик {incoming_topic}). "
        f"Отправляем в топик {destination_topic}..."
    )

    try:
        # Берём только текст без скрытых ссылок
        text = event.raw_text or ""

        if text:

            # Удаляем строки целиком
            text = re.sub(r'(?im)^.*Dolbaeb Trade.*$\n?', '', text)
            text = re.sub(r'(?im)^.*Scanner:.*$\n?', '', text)
            text = re.sub(r'(?im)^.*Trader:.*$\n?', '', text)

            # Удаляем ссылки Telegram
            text = re.sub(
                r'(https?://)?(www\.)?t\.me/[^\s]+',
                '',
                text
            )

            # Для arbionalerts удаляем вообще все ссылки
            if needs_strict_cleaning:
                text = re.sub(r'https?://[^\s]+', '', text)

            # Удаляем #
            text = text.replace('#', '')

            # Удаляем одиночные скобки
            text = re.sub(
                r'^[\[\]\(\)]+$',
                '',
                text,
                flags=re.MULTILINE
            )

            # Удаляем строки из псевдографики
            text = re.sub(
                r'^[├└┌│─]+.*$',
                '',
                text,
                flags=re.MULTILINE
            )

            # Удаляем одиночные символы типа [, ], └, ├
            text = re.sub(
                r'^[\[\]└┌├│─]+$',
                '',
                text,
                flags=re.MULTILINE
            )

            # Удаляем пустые строки
            text = re.sub(
                r'^[ \t]*$\n?',
                '',
                text,
                flags=re.MULTILINE
            )

            # Не более одной пустой строки подряд
            text = re.sub(r'\n{3,}', '\n\n', text)

            text = text.strip()

        await client.send_message(
            entity=TARGET_CHAT_ID,
            message=text,
            reply_to=destination_topic,
            file=event.media
        )

        print("Успешно очищено и отправлено!")

    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")


# --- Запуск ---
async def main():
    print("Инициализация клиента Telethon...")

    try:
        await client.connect()

        if not await client.is_user_authorized():
            print(
                "КРИТИЧЕСКАЯ ОШИБКА: SESSION_STRING устарела или неверна!",
                file=sys.stderr
            )
            sys.exit(1)

        print("Бот успешно запущен и работает!")

        await client.run_until_disconnected()

    except Exception as e:
        print(
            f"Непредвиденная ошибка при работе бота: {e}",
            file=sys.stderr
        )
        sys.exit(1)


if __name__ == '__main__':
    client.loop.run_until_complete(main())
