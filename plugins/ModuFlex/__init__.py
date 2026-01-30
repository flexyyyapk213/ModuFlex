from loads import Description, MainDescription, FuncDescription, route
from quart import render_template
from pyrogram.client import Client
from io import BytesIO
from pyrogram.enums import ParseMode

app: Client = None

def initialization(_app: Client):
    global app
    app = _app

__description__ = Description(
    MainDescription('ModuFlex - Модульный Telegram Юзербот.Не плагин, а команды из корня!'),
    FuncDescription('help', 'Выводит список плагинов/команд.Пример: .help(вывод плагинов), .help 2(вывод плагинов на 2 странице), .help ModuFlex(показывает команды плагина), help ModuFlex 2(показывает команды плагина на 2 странице)', parameters=['страница/имя плагина(не обязательно)', 'страница(не обязательно и после имя плагина)'], prefixes=['.', '/', '!']),
    FuncDescription('dwlmd', 'Скачивает сторонний плагин по ссылке из GitHub.', prefixes=['.', '/', '!'], parameters=['ссылка .zip файла']),
    FuncDescription('rmmd', 'Удаляет модуль.', prefixes=['.', '/', '!'], parameters=['имя плагина']),
    FuncDescription('update', 'Обновляет скрипт.', prefixes=['.', '/', '!']),
    FuncDescription('stop', 'Останавливает скрипт.', prefixes=['.', '/', '!']),
    FuncDescription('restart', 'Перезапускает скрипт.', prefixes=['.', '/', '!']),
    FuncDescription('moduflex', 'Показывает текущее состояние скрипта', prefixes=['.', '/', '!'])
)

@route('/')
async def main_page():
    return await render_template('ModuFlex/index.html')

@route('/send_logfile')
async def send_log_file():
    try:
        with open('script.log', 'rb') as f:
            _bytes = BytesIO(f.read())
            _bytes.name = 'script.log'
    except:
        return {'status': 400}

    try:
        await app.send_document('me', _bytes, parse_mode=ParseMode.HTML, caption='from <a href="https://github.com/flexyyyapk213/ModuFlex">ModuFlex</a>')
    except ValueError:
        await app.send_message('me', 'Log файл пуст.')
        return {'status': 400}

    return {'status': 200}