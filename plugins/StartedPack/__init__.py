from loads import func, MainDescription, FuncDescription, Description, set_modules, private_func, Data

#set_modules(['wikipedia', 'googletrans', 'gtts', 'speedtest', 'g4f'])

import asyncio
import json
import random
import re
import sys
import time
import traceback
import os

import requests
import speedtest
import wikipedia
from gtts import gTTS
from io import BytesIO
from googletrans import Translator, constants
from pyrogram import Client, filters, enums, types
from pyrogram.errors import FloodWait
from pyrogram.types import Message
from PIL import ImageDraw, ImageFont, Image
import dicttoxml

wikipedia.set_lang('ru')

__description__ = Description(
    MainDescription("Основной плагин для работы с юзер ботом"),
    FuncDescription('spam', 'Спамит текст кол-во раз', parameters=('кол-во', 'текст')),
    FuncDescription('ispam', 'Спамит текст с интервалом', parameters=('интервал(в секундах)', 'кол-во', 'текст')),
    FuncDescription('rd', 'Рандомно выбирает число из диапазона', parameters=('нижняя граница', 'верхняя граница')),
    FuncDescription('rt', 'Рандомно выбирает текст из списка', parameters=('текст1,тест2,тест3,и т.д',)),
    FuncDescription('calc', 'Вычисляет простое математическое выражение', parameters=('выражение',)),
    FuncDescription('wiki', 'Ищет текст в википедии', parameters=('текст',)),
    FuncDescription('tr', 'Переводит текст на выбранный язык', parameters=('с', 'на', 'текст')),
    FuncDescription('lg_list', 'Выводит в консоль список языков для перевода'),
    FuncDescription('tts', 'Преобразует текст в аудио', parameters=('текст',)),
    FuncDescription('info', 'Выводит информацию о пользователе или чате'),
    FuncDescription('tanos', 'Называет все имена в группе и добавляет к ним слово "исчез"'),
    FuncDescription('ping', 'Показывает ваш пинг и прочее данные'),
    FuncDescription('code', 'Выполняет питон код внутри песочнице(безопасно, но будьте осторожны).', parameters=['код']),
    FuncDescription('afk', 'Включает/выключает режим афк.Когда вам напишут и будет вкл. тогда пользователю отправиться сообщение.'),
    FuncDescription('excrypto', 'Показывает текущий указанный курс.Пример: .excrypto BTC/USDT 1', ' 💱 ', ('из(крипта)/в', 'кол-во')),
    FuncDescription('quote', 'Отправляет определённый стикер с текстом.Если не вводить параметры, в консоль отправится список названий стикеров.', parameters=('название стикера(не обязательно)', 'текст')),
    FuncDescription('export', 'Экспортирует чат в файл(xml или json) и отправляет в избранное.', parameters=('формат файла(xml или json)',))
)
#__description__ описывает плагин и его функции
# Теперь с версии 0.1.0 писать эту переменную можно в любом месте

try:
    with open('plugins/StartedPack/settings.json') as f:
        isAFK = json.load(f)['afk']
except FileNotFoundError as e:
    with open('plugins/StartedPack/settings.json', 'w') as f:
        f.write(json.dumps({
            'afk': False
        }, ensure_ascii=False))
        isAFK = False

def draw_text_box(draw: ImageDraw.Draw, text: str, box: tuple, font_path: str, start_size=60, min_size=10, fill="black", align="center"):
    x, y, w, h = box
    size = start_size

    x = x - (h // 2)

    font_path = os.path.join('plugins', 'StartedPack', 'stickers', 'fonts', font_path) if '/' not in font_path or '\\' not in font_path else font_path

    def wrap_text(text, font, max_width):
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            while word:
                test_line = (current_line + " " + word).strip() if current_line else word
                if draw.textlength(test_line, font=font) <= max_width:
                    current_line = test_line
                    break
                if current_line:
                    lines.append(current_line)
                    current_line = ""
                    continue
                
                for i in range(1, len(word) + 1):
                    if draw.textlength(word[:i], font=font) > max_width:
                        break
                cut = max(i-1, 1)
                lines.append(word[:cut])
                word = word[cut:]
        if current_line:
            lines.append(current_line)
        return lines

    while size >= min_size:
        font = ImageFont.truetype(font_path, size)
        lines = wrap_text(text, font, w)

        line_bboxes = [draw.textbbox((0,0), line, font=font) for line in lines]
        line_heights = [bbox[3] - bbox[1] for bbox in line_bboxes]
        text_height = sum(line_heights)

        if text_height <= h:
            break
        size -= 1

    start_y = y + (h - text_height) // 2

    for i, line in enumerate(lines):
        text_width = draw.textlength(line, font=font)
        if align == "center":
            start_x = x + (w - text_width) // 2
        elif align == "left":
            start_x = x
        elif align == "right":
            start_x = x + w - text_width
        else:
            start_x = x

        draw.text((int(start_x), int(start_y)), line, font=font, fill=fill)
        start_y += line_heights[i] + 5

@func(filters.command('spam', prefixes=['.', '!', '/']) & filters.me)
async def spam(app: Client, msg: Message):
    try:
        count = int(msg.text.split()[1])
        text = ' '.join(msg.text.split()[2:])
    except (ValueError, IndexError):
        return await app.edit_message_text(msg.chat.id, msg.id, 'Вы не верно ввели параметры.Пример: /spam 1 текст')

    await msg.delete()
    
    for _ in range(count):
        try:
            await app.send_message(msg.chat.id, text)
        except FloodWait as e:
            count += 1
            await asyncio.sleep(e.value)

@func(filters.command('ispam', prefixes=['.', '!', '/']) & filters.me)
async def interval_spam(app: Client, msg: Message):
    try:
        interval = float(msg.text.split()[1])
        count = int(msg.text.split()[2])
        text = ' '.join(msg.text.split()[3:])
    except (ValueError, IndexError):
        return await app.edit_message_text(msg.chat.id, msg.id, 'Вы не верно ввели параметры.Пример: /ispam 10 1 текст')

    await msg.delete()
    
    for _ in range(count):
        try:
            if msg.reply_to_message:
                await app.send_message(msg.chat.id, text, reply_to_message_id=msg.reply_to_message.id)
            else:
                await app.send_message(msg.chat.id, text)
            await asyncio.sleep(interval)
        except FloodWait as e:
            count += 1
            await asyncio.sleep(e.value)

@func(filters.command('rd', prefixes=['.', '!', '/']) & filters.me)
async def random_digits(app: Client, msg: Message):
    try:
        value1 = int(msg.text.split()[1])
        value2 = int(msg.text.split()[2])
    except ValueError:
        return await app.edit_message_text(msg.chat.id, msg.id, 'Вы не верно ввели параметры.Пример: /rd 10 100')
    
    await app.edit_message_text(msg.chat.id, msg.id, str(random.randint(value1, value2)))

@func(filters.command('rt', prefixes=['.', '!', '/']) & filters.me)
async def random_text(app: Client, msg: Message):
    try:
        texts = ' '.join(msg.text.split()[1:]).split(',')
    except IndexError:
        return await app.edit_message_text(msg.chat.id, msg.id, 'Вы не верно ввели параметры.Пример: /rt текст1,текст2,текст3')

    await app.edit_message_text(msg.chat.id, msg.id, random.choice(texts))

@func(filters.command('calc', prefixes=['.', '!', '/']) & filters.me)
async def calculator(app: Client, msg: Message):
    expression = ' '.join(msg.text.split()[1:])

    for exp in expression:
        if exp not in '0123456789+-*/() ':
            return await app.edit_message_text(msg.chat.id, msg.id, 'Вы не верно ввели параметры.Пример: /calc 1+1')

    try:
        await app.edit_message_text(msg.chat.id, msg.id, str(eval(expression)))
    except SyntaxError:
        return await app.edit_message_text(msg.chat.id, msg.id, 'Вы не верно ввели параметры.Пример: /calc 1+1')

@func(filters.command('wiki', prefixes=['.', '!', '/']) & filters.me)
async def wikipedia_search(app: Client, msg: Message):
    await app.edit_message_text(msg.chat.id, msg.id, 'Поиск...')

    try:
        query = ' '.join(msg.text.split()[1:])
    except IndexError:
        return await app.edit_message_text(msg.chat.id, msg.id, 'Вы не верно ввели параметры.Пример: /wiki текст')

    try:
        result = wikipedia.summary(query, sentences=4095)
    except wikipedia.exceptions.DisambiguationError as e:
        options = '\n'.join(str(i) + option for i, option in enumerate(e.options, start=1))
        return await app.edit_message_text(msg.chat.id, msg.id, f'Найдено несколько результатов. Выберите один из них:\n{options}')
    except wikipedia.exceptions.PageError:
        return await app.edit_message_text(msg.chat.id, msg.id, 'Страница не найдена.')

    await app.edit_message_text(msg.chat.id, msg.id, result)

@func(filters.command('tr', prefixes=['.', '!', '/']) & filters.me)
async def translate(app: Client, msg: Message):
    try:
        if msg.reply_to_message is None:
            dest = msg.text.split()[1]
            src = msg.text.split()[2]
            text = ' '.join(msg.text.split()[3:])
        else:
            src = 'auto'
            dest = msg.text.split()[1]
            text = msg.reply_to_message.text
    except IndexError:
        return await app.edit_message_text(msg.chat.id, msg.id, 'Вы не верно ввели параметры.Пример: /tr {с} {на} {текст} (или, если ответили на сообщение: /tr {язык_на})')
    except ValueError:
        return await app.edit_message_text(msg.chat.id, msg.id, 'Вы не верно ввели язык.Пример: /tr ru en текст (или, если ответили на сообщение: /tr en)')
    
    trans = Translator()
    result = trans.translate(text, src=src, dest=dest)
    await app.edit_message_text(msg.chat.id, msg.id, f'```{result.src}\n{result.text}\n```')

@func(filters.command('lg_list', prefixes=['.', '!', '/']) & filters.me)
async def language_list(app: Client, msg: Message):

    await app.edit_message_text(msg.chat.id, msg.id, 'Список языков выведен в терминал')

    print(json.dumps(constants.LANGUAGES, indent=4))

@func(filters.command('tts', prefixes=['.', '!', '/']) & filters.me)
async def text_to_speech(app: Client, msg: Message):
    await app.delete_messages(msg.chat.id, msg.id)
    
    try:
        text = ' '.join(msg.text.split()[1:])
    except IndexError:
        return await app.edit_message_text(msg.chat.id, msg.id, 'Вы не верно ввели параметры.Пример: /tts текст')

    tts = gTTS(text, lang='ru')
    
    audio = BytesIO()
    audio.name = 'audio.ogg'

    tts.write_to_fp(audio)
    audio.seek(0)

    await app.send_audio(msg.chat.id, audio)

@func(filters.command('info', prefixes=['.', '!', '/']) & filters.me)
async def info(app: Client, msg: Message):
    if msg.reply_to_message:
        user = msg.reply_to_message.from_user

        await app.edit_message_text(msg.chat.id, msg.id, f'Информация о пользователе:\nID: {user.id}\nИмя: {user.first_name}\nНикнейм: {user.username}\nАктивность: {user.status}')
    else:
        await app.edit_message_text(msg.chat.id, msg.id, f'Информация о чате:\nID: {msg.chat.id}\nТип: {msg.chat.type}')

@func(filters.command('tanos', prefixes=['.', '!', '/']) & filters.me)
async def tanos(app: Client, msg: Message):
    if str(msg.chat.type) in ["ChatType.GROUP", "ChatType.SUPERGROUP"]:
        await app.send_message(msg.chat.id, '*Щелчок таноса')

        async for user in app.get_chat_members(msg.chat.id):
            try:
                await app.send_message(msg.chat.id, f'*{user.user.first_name} исчез')
            except FloodWait as e:
                await asyncio.sleep(e.value)

@func(filters.command('ping', prefixes=['.', '!', '/']) & filters.me)
async def check_ping(_, msg: Message):
    st = speedtest.Speedtest()

    await msg.edit('Подбор лучшего сервера...')

    st.get_best_server()

    await msg.edit(f'Пинг: {st.results.ping}ms\nСкачивание: {st.download()/1000000:.2f}mbs\nВыгрузка: {st.upload()/1000000:.2f}mbs')

@func(filters.command('code', prefixes=['.', '!', '/']) & filters.me)
async def code_runner(_, msg: Message):
    code = msg.text.split('code', maxsplit=1)[1].strip()

    await msg.edit(
        f'```python\n{code}\n```'
        '```bash\nВыполнение..\n```'
    )

    texts = ''
    start = time.time()

    try:
        _result = Data.sandbox_executor.run_code(code)
        
        texts = _result['output'].replace('<', '&lt;').replace('>', '&gt;')
    except Exception as e:
        texts = re.sub('File ".*"', 'File "Hidden"', traceback.format_exc())
    
    end = abs(start - time.time())

    code_slices = '\n'.join(f'{i}. {line}' for i, line in enumerate(code.split('\n'), start=1))

    final_result = (
        f'```python\n{code_slices.strip()}```\n',
        f'{texts}',
        f'```time\n{end:.2f}с.```'
    )
    
    await msg.edit(final_result[0] + '```bash\n' + final_result[1][(len(final_result[1]) + len(final_result[0]) + len(final_result[2])) - max(0, min(4083, len(final_result[1]))):len(final_result[1])] + '\n```\n' + final_result[2])

@func(filters.command('afk', prefixes=['.', '!', '/']) & filters.me)
async def afk_mode(_, msg: Message):
    global isAFK
    try:
        with open('plugins/StartedPack/settings.json', 'r') as f:
            settings = json.load(f)
        
        if settings['afk']:
            settings['afk'] = False

            await msg.edit('Вы вышли из режима афк.')
        else:
            settings['afk'] = True

            await msg.edit('Вы вошли в режим афк.')
        
        isAFK = settings['afk']

        with open('plugins/StartedPack/settings.json', 'w') as f:
            f.write(json.dumps(settings, ensure_ascii=False))
    except FileNotFoundError as e:
        print(e)
        with open('plugins/StartedPack/settings.json', 'w') as f:
            f.write(json.dumps({
                'afk': False
            }, ensure_ascii=False))
        
        await msg.edit('Файл настроек не был обнаружен.Вы не в режиме афк.')

@func(filters.command('excrypto', ['/', '.', '!']) & filters.me)
async def exchange_crypto(app: Client, msg: Message):
    try:
        await msg.delete()
    except:
        pass

    try:
        symbol = msg.text.split()[1]
        if len(msg.text.split()) == 3:
            count = int(msg.text.split()[2])
        else: count = 1
    except (IndexError, ValueError):
        return await app.send_message(msg.chat.id, 'Вы не верно ввели параметр.Пример: .excrypto BTC/USDT (не обязательно{кол-во})')
    except Exception as e:
        return await app.send_message(msg.chat.id, e)

    response = requests.get(f'https://api.binance.com/api/v3/ticker/price?symbol={"".join(symbol.split("/"))}')
    price = response.json()

    if "code" in price:
        return await app.send_message(msg.chat.id, 'Неизвестный курс.')
    
    price = float(price['price'])

    await app.send_message(msg.chat.id, f'Текущий курс: {price * count:.2f} {symbol.split("/")[1]} за {count} {symbol.split("/")[0]}')

@func(filters.command('everyone', ['/', '.', '!']) & filters.group & filters.me, description='Призывает всех пользователей.')
async def general_fe(client: Client, message: Message):
    await message.delete()
    
    user_links = ''
    count = 0

    async for user in client.get_chat_members(message.chat.id):
        if user.user.is_bot:
            continue
        user_links += f'{user.user.mention} '

        count += 1

    await client.send_message(message.chat.id, f'Призываю всех!({count}){user_links}', parse_mode=enums.ParseMode.HTML)

@func(filters.command('quote', ['/', '.', '!']) & filters.me)
async def quote_sticker(client: Client, msg: Message):
    await msg.delete()
    
    try:
        back_name = msg.text.split()[1]

        text = ' '.join(msg.text.split()[2:])
    except:
        await msg.answer('В консоль был выведен список названий стикеров.')
        return print('\n'.join([name.replace('.json', '') for name in os.listdir('plugins/StartedPack/stickers') if name.endswith('.json')]))

    try:
        img = Image.open(f'plugins/StartedPack/stickers/{back_name}.webp')
    except FileNotFoundError:
        return await client.send_message(msg.chat.id, 'Такого стикера нету.')
    draw = ImageDraw.Draw(img)

    with open(f'plugins/StartedPack/stickers/{back_name}.json') as f:
        json_parameters = json.load(f)

    draw_text_box(
        draw,
        text,
        json_parameters['box'],
        json_parameters['font_path'],
        json_parameters['start_size'],
        fill=json_parameters['fill'],
        align=json_parameters['align']
    )

    stk = BytesIO()

    img.save(stk, 'WEBP')

    stk.name = 'sticker.webp'

    await client.send_sticker(msg.chat.id, stk, reply_to_message_id=msg.reply_to_message.id if msg.reply_to_message else None)

def user_to_json(usr: types.User) -> dict:
    jsn = {
        "id": usr.id,
        "is_contact": usr.is_contact,
        "is_mutual_contact": usr.is_mutual_contact,
        "is_deleted": usr.is_deleted,
        "is_bot": usr.is_bot,
        "is_verified": usr.is_verified,
        "is_restricted": usr.is_restricted,
        "is_scam": usr.is_scam,
        "is_fake": usr.is_fake,
        "is_support": usr.is_support,
        "is_premium": usr.is_premium,
        "first_name": usr.first_name,
        "last_name": usr.last_name,
        "status": usr.status.value,
        "last_online_date": usr.last_online_date.strftime('%Y %m %d %H-%M-%S') if usr.last_online_date is not None else None,
        "next_offline_date": usr.next_offline_date.strftime('%Y %m %d %H-%M-%S') if usr.next_offline_date is not None else None,
        "username": usr.username,
        "language_code": usr.language_code,
        "dc_id": usr.dc_id,
        "photo": usr.photo.big_photo_unique_id if usr.photo is not None else None
    } if usr is not None else {}
    
    return jsn

def chat_to_json(cht: types.Chat) -> dict:
    jsn = {
        "id": cht.id,
        "type": cht.type.value,
        "is_verified": cht.is_verified,
        "is_scam": cht.is_scam,
        "is_fake": cht.is_fake,
        "is_support": cht.is_support,
        "title": cht.title,
        "username": cht.username,
        "first_name": cht.first_name,
        "last_name": cht.last_name,
        "photo": cht.photo.big_photo_unique_id if cht.photo is not None else None,
        "bio": cht.bio,
        "description": cht.description,
        "dc_id": cht.dc_id,
        "has_protected_content": cht.has_protected_content,
        "invite_link": cht.invite_link,
        "members_count": cht.members_count,
        "distance": cht.distance
    } if cht is not None else {}

    return jsn

def message_to_json(msg: Message) -> dict:
    jsn = {
        "id": msg.id,
        "user": user_to_json(msg.from_user),
        "date": msg.date.strftime('%Y %m %d %H-%M-%S') if msg.date is not None else None,
        "forward_from": user_to_json(msg.forward_from),
        "forward_from_chat": chat_to_json(msg.forward_from_chat),
        "reply_to_message_id": msg.reply_to_message_id,
        "reply_to_message": message_to_json(msg.reply_to_message),
        "edit_date": msg.edit_date.strftime('%Y %m %d %H-%M-%S') if msg.edit_date is not None else None,
        "text": msg.text,
        "audio": msg.audio.file_unique_id if msg.audio is not None else None,
        "document": msg.document.file_unique_id if msg.document is not None else None,
        "photo": msg.photo.file_unique_id if msg.photo is not None else None,
        "video": msg.video.file_unique_id if msg.video is not None else None,
        "video_note": msg.video_note.file_unique_id if msg.video_note is not None else None,
        "caption": msg.caption
    } if msg is not None else {}

    return jsn

@func(filters.command('export', ['/', '.', '!']) & filters.me)
async def export_chat_history(client: Client, message: Message):
    try:
        _format = message.text.split()[1].lower()
    except IndexError:
        return await message.edit_text('Вы не верно ввели параметры: /export <формат(HTML или json)>')
    
    chat = message.chat

    chat_history = {
        "chat": {
            "id": chat.id,
            "type": chat.type.value,
            "is_verified": chat.is_verified,
            "is_scam": chat.is_scam,
            "is_fake": chat.is_fake,
            "is_support": chat.is_support,
            "title": chat.title,
            "username": chat.username,
            "first_name": chat.first_name,
            "last_name": chat.last_name,
            "photo": chat.photo.big_photo_unique_id,
            "bio": chat.bio,
            "description": chat.description,
            "dc_id": chat.dc_id,
            "has_protected_content": chat.has_protected_content,
            "invite_link": chat.invite_link,
            "members_count": chat.members_count,
            "distance": chat.distance,
            "history": []
        }
    }

    async for history in client.get_chat_history(message.chat.id):
        chat_history['chat']['history'].append(message_to_json(history))
    
    if _format == 'xml':
        data = dicttoxml.dicttoxml(chat_history)
    else:
        data = json.dumps(chat_history, ensure_ascii=False).encode()
    
    file_data = BytesIO(data)
    file_data.name = f'exported_chat.{_format}'

    await client.send_document('me', file_data)

    await message.edit_text('Файл отправлен в избранное.')

@private_func()
async def _private_func(client: Client, msg: Message):
    if isAFK:
        await client.send_message(msg.from_user.id, '💤Сейчас я немного занят, но скоро вернусь!\n💬Если вдруг не отвечу в течение пары часов, обязательно напишите мне ещё разок!')