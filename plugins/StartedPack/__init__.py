from loads import func, MainDescription, FuncDescription, Description, set_modules, private_func

#set_modules(['wikipedia', 'googletrans', 'gtts', 'speedtest', 'g4f'])

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
import asyncio
import random
import wikipedia
from googletrans import Translator, constants
import json
from gtts import gTTS
from io import BytesIO
import speedtest
import time
import io
import sys
import traceback
import re
import requests

wikipedia.set_lang('ru')

__description__ = Description(
    MainDescription("Основной плагин для работы с юзер ботом"),
    FuncDescription('spam', 'Спамит текст кол-во раз', parameters=('кол-во', 'текст')),
    FuncDescription('ispam', 'Спамит текст с интервалом', parameters=('интервал(в секундах)', 'кол-во', 'текст')),
    FuncDescription('rd', 'Рандомно выбирает число из диапазона', parameters=('нижняя граница', 'верхняя граница')),
    FuncDescription('rt', 'Рандомно выбирает текст из списка', parameters=('текст1,тест2,тест3,и т.д',)),
    FuncDescription('calc', 'Вычисляет математическое выражение', parameters=('выражение',)),
    FuncDescription('wiki', 'Ищет текст в википедии', parameters=('текст',)),
    FuncDescription('tr', 'Переводит текст на выбранный язык', parameters=('с', 'на', 'текст')),
    FuncDescription('lg_list', 'Выводит в консоль список языков для перевода'),
    FuncDescription('tts', 'Преобразует текст в аудио', parameters=('текст',)),
    FuncDescription('info', 'Выводит информацию о пользователе или чате'),
    FuncDescription('tanos', 'Называет все имена в группе и добавляет к ним слово "исчез"'),
    FuncDescription('ping', 'Показывает ваш пинг и прочее данные'),
    FuncDescription('code', 'Выполняет пайтон код(осторожно с кодом, иначе будут ужасные необратимые последствия)', parameters=['код']),
    FuncDescription('afk', 'Включает/выключает режим афк.Когда вам напишут и будет вкл. тогда пользователю отправиться сообщение.'),
    FuncDescription('excrypto', 'Показывает текущий указанный курс.Пример: .excrypto BTC/USDT 1', ' 💱 ', ('из(крипта)/в', 'кол-во'))
)
#__description__ описывает плагин и его функции
# Теперь с версии 0.1.0 писать эту переменную можно в любом месте основного файла(т.е файла __init__)

try:
    with open('plugins/StartedPack/settings.json') as f:
        isAFK = json.load(f)['afk']
except FileNotFoundError as e:
    with open('plugins/StartedPack/settings.json', 'w') as f:
        f.write(json.dumps({
            'afk': False
        }, ensure_ascii=False))
        isAFK = False

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
    try:
        expression = ' '.join(msg.text.split()[1:])
    except IndexError:
        return await app.edit_message_text(msg.chat.id, msg.id, 'Вы не верно ввели параметры.Пример: /calc 1+1')

    for exp in expression:
        if exp not in '0123456789+-*/() ':
            return await app.edit_message_text(msg.chat.id, msg.id, 'Вы не верно ввели параметры.Пример: /calc 1+1')

    await app.edit_message_text(msg.chat.id, msg.id, str(eval(expression)))

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
        dest = msg.text.split()[1]
        src = msg.text.split()[2]
        text = ' '.join(msg.text.split()[3:])
    except IndexError:
        return await app.edit_message_text(msg.chat.id, msg.id, 'Вы не верно ввели параметры.Пример: /tr {с} {на} {текст}')
    except ValueError:
        return await app.edit_message_text(msg.chat.id, msg.id, 'Вы не верно ввели язык.Пример: /tr ru en текст')
    
    trans = Translator()
    result = trans.translate(text, src, dest)
    await app.edit_message_text(msg.chat.id, msg.id, result.text)

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

    output = io.StringIO()
    sys.stdout = output
    sys.stderr = output

    texts = ''
    start = time.time()

    try:
        exec(code)
    except Exception as e:
        error_trace = traceback.format_exc()

        error_trace = re.sub(r'\n\s*File ".*?", line \d+, in code_runner\n\s*exec\(code\)', '', error_trace, count=1)
        texts += output.getvalue().strip() + '\n' + error_trace
    finally:
        texts += output.getvalue()
    
    end = abs(start - time.time())

    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__

    code_slices = '\n'.join(f'{i}. {line}' for i, line in enumerate(code.split('\n'), start=1))
    
    await msg.edit(
        f'```python\n{code_slices.strip()}```\n'
        f'```bash\n{texts.strip()}```\n'
        f'```time\n{end:.2f}с.```'
    )

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

@private_func()
async def _private_func(client: Client, msg: Message):
    if isAFK:
        await client.send_message(msg.from_user.id, '💤Сейчас я немного занят, но скоро вернусь!\n💬Если вдруг не отвечу в течение пары часов, обязательно напишите мне ещё разок!')