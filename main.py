from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import MessageEntityTextUrl, MessageEntityUrl
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import sys
import re
import threading
import asyncio

# --- Переменные окружения ---
API_ID = 29138810
API_HASH = os.getenv('API_HASH', '').strip()
SESSION_STRING = os.getenv('SESSION_STRING', '').strip()
BOT_TOKEN = os.getenv('BOT_TOKEN', '').strip()
URL1 = os.getenv('URL1')
URL2 = os.getenv('URL2')
URL3 = os.getenv('URL3')

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

# --- URL-шаблоны для бирж ---
EXCHANGE_URL_TEMPLATES = {
    'binance':      'https://www.binance.com/en/trade/{token}_USDT',
    'mexc':         'https://www.mexc.com/exchange/{token}_USDT',
    'bybit':        'https://www.bybit.com/trade/usdt/{token}USDT',
    'gate':         'https://www.gate.io/trade/{token}_USDT',
    'hyperliquid':  'https://app.hyperliquid.xyz/trade/{token}',
    'okx':          'https://www.okx.com/trade-spot/{token}-usdt',
    'aster':        'https://www.aster.com/trade/{token}_USDT',
    'bingx':        'https://bingx.com/en/spot/{token}USDT/',
}

SENDER_TO_EXCHANGE = {
    'bin_4p':    'binance',
    'bin_9p':    'binance',
    'bin_22p':   'binance',
    'mexc_5pf':  'mexc',
    'mexc_12pf': 'mexc',
    'dt_50p':    'mexc',
    'bybit_5p':  'bybit',
    'bb_10p':    'bybit',
    'gate_5p':   'gate',
    'g_12p':     'gate',
    'g_50p':     'gate',
    'hl_11p':    'hyperliquid',
    'hl_50p':    'hyperliquid',
    'okx_12p':   'okx',
    'okx_50p':   'okx',
    'aster_50p': 'aster',
    'bingx_50p': 'bingx',
}


def extract_token(text: str) -> str | None:
    match = re.search(r'\$([A-Z0-9]{2,20})', text)
    if match:
        return match.group(1)
    match = re.search(r'\b([A-Z]{2,20})\b', text)
    if match:
        return match.group(1)
    return None


def build_exchange_link(sender: str, text: str) -> str | None:
    exchange = SENDER_TO_EXCHANGE.get(sender)
    if not exchange:
        return None
    token = extract_token(text)
    if not token:
        return None
    url = EXCHANGE_URL_TEMPLATES[exchange].format(token=token)
    return f'<a href="{url}">Follow</a>'


# --- Замены слов ---
WORD_REPLACEMENTS = [
    ('Изм.',      'Price change'),
    ('Справедл.', 'Fair'),
    (
        'Данный токен не доступен в СНГ на MEXC',
        'This token is not available on MEXC in the CIS(SNG) region.'
    ),
]


def apply_word_replacements(text: str) -> str:
    for old, new in WORD_REPLACEMENTS:
        text = text.replace(old, new)
    return text


def remove_word_with_entities(text: str, entities: list, word: str):
    """
    Удаляет все вхождения слова из текста и сдвигает offsets entities.
    Возвращает (new_text, new_entities).
    """
    import copy
    word_bytes_len = len(word.encode('utf-16-le')) // 2  # в UTF-16 единицах

    result_text = text
    result_entities = [copy.copy(e) for e in (entities or [])]

    # Ищем все вхождения и удаляем справа налево (чтобы не сбивать индексы)
    matches = list(re.finditer(re.escape(word), result_text))
    for m in reversed(matches):
        start_char = m.start()
        end_char = m.end()
        # UTF-16 offset до начала совпадения
        utf16_start = len(result_text[:start_char].encode('utf-16-le')) // 2
        utf16_end   = len(result_text[:end_char].encode('utf-16-le')) // 2
        removed_len = utf16_end - utf16_start

        # Удаляем из строки
        result_text = result_text[:start_char] + result_text[end_char:]

        # Корректируем entities
        updated = []
        for e in result_entities:
            e_end = e.offset + e.length
            if e.offset >= utf16_end:
                # entity полностью после — сдвигаем
                e.offset -= removed_len
                updated.append(e)
            elif e_end <= utf16_start:
                # entity полностью до — не трогаем
                updated.append(e)
            elif e.offset >= utf16_start and e_end <= utf16_end:
                # entity полностью внутри удаляемого слова — выбрасываем
                pass
            else:
                # частичное пересечение — обрезаем length
                if e.offset < utf16_start:
                    e.length = min(e.length, utf16_start - e.offset)
                else:
                    e.offset = utf16_start
                    e.length = max(0, e_end - utf16_end)
                if e.length > 0:
                    updated.append(e)
        result_entities = updated

    return result_text, result_entities


def strip_last_line_with_entities(text: str, entities: list):
    """
    Удаляет последнюю непустую строку из текста и обрезает entities,
    которые в неё попадают. Возвращает (new_text, new_entities).
    """
    lines = text.splitlines()
    # убираем пустые строки с конца
    while lines and not lines[-1].strip():
        lines.pop()
    if not lines:
        return '', []

    # вычисляем байтовый срез, который нужно вырезать
    # (последняя строка + предшествующий \n)
    last_line = lines[-1]
    keep_text = '\n'.join(lines[:-1])
    cut_from = len(keep_text.encode('utf-16-le')) // 2  # TG считает в UTF-16 кодовых единицах

    new_entities = []
    for ent in (entities or []):
        ent_end = ent.offset + ent.length
        if ent_end <= cut_from:
            # entity полностью в сохраняемой части
            new_entities.append(ent)
        elif ent.offset < cut_from:
            # entity частично пересекает границу — обрезаем
            import copy
            e = copy.copy(ent)
            e.length = cut_from - ent.offset
            new_entities.append(e)
        # entity полностью в удалённой части — выбрасываем

    return keep_text.strip(), new_entities


# ===================== telebot /start =====================
bot = telebot.TeleBot(BOT_TOKEN) if BOT_TOKEN else None


@bot.message_handler(commands=['start'])  # type: ignore[misc]
def start_command(message):
    markup = InlineKeyboardMarkup()
    if URL1:
        markup.add(InlineKeyboardButton(text="Tribute", url=URL1))
    if URL2:
        markup.add(InlineKeyboardButton(text="Crypto bot", url=URL2))
    if URL3:
        markup.add(InlineKeyboardButton(text="Support", url=URL3))
    bot.send_message(
        message.chat.id,
        "Hi! 👋 I'm your personal payment assistant.",
        reply_markup=markup
    )


def run_telebot():
    if bot:
        print("telebot запущен...")
        bot.polling(none_stop=True, timeout=30)


# ===================== Telethon userbot =====================
client = TelegramClient(
    StringSession(SESSION_STRING),
    API_ID,
    API_HASH
)


@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def forward_message(event):
    sender = getattr(event.chat, 'username', '')
    if sender:
        sender = sender.lower()

    chat_id = event.chat_id
    incoming_topic = getattr(event.message, 'reply_to_msg_id', None)

    destination_topic = None
    needs_strict_cleaning = False

    # --- МАРШРУТИЗАЦИЯ ---
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
    elif sender in ['dt_50p', 'hl_50p', 'g_50p', 'aster_50p', 'bingx_50p', 'okx_50p']:
        destination_topic = 211
    elif sender == 'hl_11p':
        destination_topic = 1
    elif sender == 'okx_12p':
        destination_topic = 1
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
        # ---- NFT канал: сохраняем entities, удаляем только последнюю строку ----
        if sender == 'tracervarikteat':
            raw = event.message.message or ""
            entities = list(event.message.entities or [])
            new_text, new_entities = strip_last_line_with_entities(raw, entities)

            await client.send_message(
                entity=TARGET_CHAT_ID,
                message=new_text,
                formatting_entities=new_entities,
                reply_to=destination_topic,
                file=event.media,
            )
            print("NFT — успешно отправлено!")
            return

        # ---- uainvest_scanner: сохраняем entities, удаляем "Link" ----
        if sender == 'uainvest_scanner':
            raw = event.message.message or ""
            entities = list(event.message.entities or [])

            # Удаляем слово "Link" (вместе с пробелом перед ним если есть)
            raw, entities = remove_word_with_entities(raw, entities, ' Link')
            raw, entities = remove_word_with_entities(raw, entities, 'Link')

            # Текстовые замены (не затрагивают entities — слова разные)
            raw = apply_word_replacements(raw)

            await client.send_message(
                entity=TARGET_CHAT_ID,
                message=raw,
                formatting_entities=entities,
                reply_to=destination_topic,
                file=event.media,
            )
            print("uainvest_scanner — успешно отправлено!")
            return

        # ---- Все остальные каналы: текстовая очистка ----
        text = event.raw_text or ""

        if text:
            text = re.sub(r'(?im)^.*Dolbaeb Trade.*$\n?', '', text)
            text = re.sub(r'(?im)^.*Scanner:.*$\n?', '', text)
            text = re.sub(r'(?im)^.*Trader:.*$\n?', '', text)

            text = re.sub(r'(https?://)?(www\.)?t\.me/[^\s]+', '', text)

            if needs_strict_cleaning:
                text = re.sub(r'https?://[^\s]+', '', text)

            text = text.replace('#', '')

            text = re.sub(r'^[\[\]\(\)]+$', '', text, flags=re.MULTILINE)
            text = re.sub(r'^[├└┌│─]+.*$', '', text, flags=re.MULTILINE)
            text = re.sub(r'^[\[\]└┌├│─]+$', '', text, flags=re.MULTILINE)
            text = re.sub(r'^[ \t]*$\n?', '', text, flags=re.MULTILINE)
            text = re.sub(r'\n{3,}', '\n\n', text)
            text = text.strip()
            text = apply_word_replacements(text)

        # Добавляем ссылку "Перейти" на биржу
        exchange_link = build_exchange_link(sender, text)
        if exchange_link:
            text = text + '\n\n' + exchange_link

        await client.send_message(
            entity=TARGET_CHAT_ID,
            message=text,
            reply_to=destination_topic,
            file=event.media,
            parse_mode='html'
        )
        print("Успешно очищено и отправлено!")

    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")


# ===================== Запуск =====================
async def main():
    print("Инициализация Telethon...")
    try:
        await client.connect()
        if not await client.is_user_authorized():
            print("КРИТИЧЕСКАЯ ОШИБКА: SESSION_STRING устарела!", file=sys.stderr)
            sys.exit(1)
        print("Telethon userbot запущен!")
        await client.run_until_disconnected()
    except Exception as e:
        print(f"Непредвиденная ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    # Запускаем telebot в отдельном потоке
    t = threading.Thread(target=run_telebot, daemon=True)
    t.start()

    # Запускаем Telethon в основном потоке
    client.loop.run_until_complete(main())
