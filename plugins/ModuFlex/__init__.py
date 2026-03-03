from loads import Description, MainDescription, FuncDescription, route
from quart import render_template, request
from pyrogram.client import Client
from io import BytesIO
from pyrogram.enums import ParseMode
from utils import get_config_data
import json
import logging
import traceback
import re
from typing import List

logger = logging.getLogger()

app: Client = None

def initialization(_app: Client):
    global app
    app = _app

__description__ = Description(
    MainDescription('ModuFlex - Модульный Telegram Юзербот.Не плагин, а команды из корня!'),
    FuncDescription('help', 'Выводит список плагинов/команд.Пример: .help(вывод плагинов), .help 2(вывод плагинов на 2 странице), .help ModuFlex(показывает команды плагина), help ModuFlex 2(показывает команды плагина на 2 странице)', parameters=['страница/имя плагина(не обязательно)', 'страница(не обязательно и после имя плагина)'], prefixes=['.', '/', '!']),
    FuncDescription('dwplg', 'Скачивает сторонний плагин по ссылке из GitHub.', prefixes=['.', '/', '!'], parameters=['ссылка на гит хаб репозиторий']),
    FuncDescription('rmplg', 'Удаляет плагин.', prefixes=['.', '/', '!'], parameters=['имя плагина']),
    FuncDescription('update', 'Обновляет скрипт.', prefixes=['.', '/', '!']),
    FuncDescription('stop', 'Останавливает скрипт.', prefixes=['.', '/', '!']),
    FuncDescription('restart', 'Перезапускает скрипт.', prefixes=['.', '/', '!']),
    FuncDescription('moduflex', 'Показывает текущее состояние скрипта', prefixes=['.', '/', '!']),
    FuncDescription('webi', 'Проверяет у плагина, имеется ли страница на локальном сайте.', ['.', '/', '!'], parameters=['имяПлагина'])
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

@route('/additional_accounts/')
async def аdditional_аccounts():
    return await render_template('ModuFlex/additional_accounts.html')

@route('/additional_accounts/add', methods=['POST'])
async def add_new_account():
    data = await request.json

    cfg = get_config_data()
    accounts: List[dict] = cfg['additional_accounts']

    for account in accounts:
        if account['phone_number'] == data['phone_number']:
            return {"status": 400}

    if accounts is None:
        accounts = []

    accounts.append({"phone_number": data['phone_number'], "password": data['password']})

    try:
        with open('config.ini') as file:
            config = file.read()
    except FileNotFoundError:
        logger.error(traceback.format_exc())

        return {"status": 200}
    
    if re.search(r'accounts\s*=\s*\[.*?\]', config, flags=re.DOTALL) is None:
        try:
            with open('config.ini', 'a', encoding='utf-8') as file:
                file.write(f'\naccounts = {json.dumps(accounts, ensure_ascii=False)}')

                return {"status": 200}
        except FileNotFoundError:
            logger.error(traceback.format_exc())
    
    config = re.sub(r'accounts\s*=\s*\[.*?\]', f'accounts = {json.dumps(accounts, ensure_ascii=False)}', config, flags=re.DOTALL)

    try:
        with open('config.ini', 'w', encoding='utf-8') as file:
            file.write(config)
    except FileNotFoundError:
        logger.error(traceback.format_exc())
    
    return {"status": 200}

@route('/additional_accounts/get_accounts', methods=['GET'])
async def get_accounts():
    cfg = get_config_data()
    accounts: list = cfg['additional_accounts']

    if accounts is None:
        accounts = []

    return {"status": 200, "accounts": cfg['additional_accounts']}

@route('/additional_accounts/delete_account=<int:index>')
async def delete_account(index: int):
    cfg = get_config_data()
    accounts: list = cfg['additional_accounts']

    if accounts is None:
        accounts = []

    try:
        accounts.pop(index)
    except IndexError:
        return {"status": 400}

    try:
        with open('config.ini') as file:
            config = file.read()
    except FileNotFoundError:
        logger.error(traceback.format_exc())
    
    if re.search(r'accounts\s*=\s*\[.*?\]', config, flags=re.DOTALL) is None:
        try:
            with open('config.ini', 'a', encoding='utf-8') as file:
                file.write(f'\naccounts = {json.dumps(accounts, ensure_ascii=False)}')

                return {"status": 200}
        except FileNotFoundError:
            logger.error(traceback.format_exc())
    
    config = re.sub(r'accounts\s*=\s*\[.*?\]', f'accounts = {json.dumps(accounts, ensure_ascii=False)}', config, flags=re.DOTALL)

    try:
        with open('config.ini', 'w', encoding='utf-8') as file:
            file.write(config)
    except FileNotFoundError:
        logger.error(traceback.format_exc())
    
    return {"status": 200}