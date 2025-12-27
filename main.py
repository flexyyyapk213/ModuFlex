import importlib.util
import subprocess
from typing import Dict

from __init__ import __modules__, __news__

from alive_progress import alive_it, styles

import zipfile
import shutil
import os

import re
import inspect
from concurrent.futures import ThreadPoolExecutor

import asyncio
import logging
import random

import time
import traceback
from datetime import datetime

import copy

from pyrogram import Client, filters, enums
from pyrogram.handlers import MessageHandler
from pyrogram import types

from terminaltexteffects.effects.effect_rain import Rain
from terminaltexteffects.effects.effect_decrypt import Decrypt, DecryptConfig
import requests

import pyfiglet
from pyrogram.enums import ParseMode
from platform import python_version

from packaging import version as __version
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from loads import Data, ScriptState
from handling_plugins import handling_plugins as handling_plg, handle_plugin
from __init__ import __version__ as this_version

from utils import merge_directories, __find_command_name__, check_update

logging.basicConfig(filename='script.log', level=logging.WARN)

# Чистка логов
if os.path.getsize('script.log') >= 262_144:
    with open('script.log', 'w') as f:
        pass

registers = {}

try:
    file = open("config.ini", "r").read()
    api_id = re.search(r'api_id\s*=\s*(\d+)', file)
    api_hash = re.search(r'api_hash\s*=\s*[\'"](.*?)[\'"]', file)
    send_msg_onstart_up = re.search(r'send_message\s*=\s*(true|false)', file)

    if send_msg_onstart_up is not None:
        send_msg_onstart_up = {'true': True, 'false': False}[send_msg_onstart_up.group(1)]
    else:
        send_msg_onstart_up = False

    phone_number = re.search(r'phone_number\s*=\s*(\d+)', file)
    password = re.search(r'password\s*=\s*[\'"](.*?)[\'"]', file)

    ask_to_downloads = re.search(r'ask_downloads\s*=\s(true|false)', file)

    if ask_to_downloads is not None: Data.ask_downloads = {'false': True, 'true': False}[ask_to_downloads.group(1)]

    one_download_libs = re.search(r'one_download_libs\s*=\s(true|false)', file)

    if one_download_libs is not None: Data.one_download_libs = {'true': True, 'false': False}[one_download_libs.group(1)]

    check_for_update = re.search(r'check_for_update\s*=\s(true|false)', file)

    if check_for_update is not None: Data.check_for_update = {'true': True, 'false': False}[check_for_update.group(1)]

    timeout_download_lib = re.search(r'timeout_download_lib\s*=\s(\d+)', file)

    if timeout_download_lib is not None: Data.timeout_download_lib = int(timeout_download_lib.group(1)) if timeout_download_lib.group(1).isdigit() else 60
except Exception as e:
    pass

there_is_update = False
features_of_the_version = []
stop = ScriptState.started
auto_check_for_update = AsyncIOScheduler()

app = None

# TODO: Сделать что то типа манифеста в скачивании плагина

def check_updates():
    global there_is_update, features_of_the_version
    # Ссылка на официальный источник, так что вирусов не должно быть, нужно детально проверять ссылку(так же самое и в плагинах)
    link = 'https://raw.githubusercontent.com/flexyyyapk213/ModuFlex/main/__init__.py'
    fresh_version = __version.parse(re.search(r'__version__ = \'(.*?)\'', requests.get(link, headers={'User-Agent': 'Mozilla/5.0'}).text).group(1))
    version_now = __version.parse(this_version)

    if version_now.is_prerelease:
        features_of_the_version.append('this_is_prerelease')
    
    if fresh_version > version_now:
        if not send_msg_onstart_up:
            DecryptConfig(1)

            effect = Decrypt('Доступно новое обновление!Введите в чате /update для обновления.')
            with effect.terminal_output() as terminal:
                for frame in effect:
                    terminal.print(frame)
        there_is_update = fresh_version
    elif fresh_version < version_now:
        features_of_the_version.append('you_are_tester')

def handling_updates():
    updates: Dict = Data.cache

    with ThreadPoolExecutor(max_workers=10) as executor:
        for func in Data.initializations:
            executor.submit(func, app)

    for update in updates:
        if not registers.get(update, False):
            registers.update({update: {"funcs": {}, "classes": {}}})

        for func_name, _func in updates[update]['funcs'].items():
            if registers[update]['funcs'].get(func_name, False):
                continue
            
            if _func['command_name'] is not None:
                if _func['command_name'] in Data.count_commands:
                    Data.count_commands[_func['command_name']].append(update)
                else:
                    Data.count_commands.update({_func['command_name']: [update]})
            
            registers[update]['funcs'].update({func_name: _func['func']})

async def help(_, msg: types.Message):
    help_text = ''

    if len(msg.text.split()) == 1:
        help_text = 'Список плагинов:\n0) <code>ModuFlex</code>&lt;MAIN&gt;\n'

        plgs_desc = copy.deepcopy(Data.description)

        plgs_desc.pop('ModuFlex')

        for indx, plugin in enumerate(plgs_desc):
            if plugin == 'ModuFlex':
                continue

            help_text += f'{indx+1}) <code>{plugin}</code>({len(Data.description[plugin].funcs_description)})\n'

            if indx >= 30:
                break
        
        pages = len(Data.description)/30

        if pages > int(pages): pages = int(pages) + 1
        
        help_text += f'\n<b>Страница: 1/{pages}</b>' + '\n●Чтобы узнать о функции плагина, введите: /help {имя плагина}\n●Чтобы переходить на страницу, введите: для плагинов: /help 2, для команд: /help {имя плагина} 1'
    elif len(msg.text.split()) == 2 and msg.text.split()[1].isdigit():
        help_text = 'Список плагинов:\n'

        try:
            page = int(msg.text.split()[1])
        except ValueError as e:
            return await msg.edit('Неверный номер страницы.')

        pages = len(Data.description)/30

        if pages > int(pages): pages = int(pages) + 1

        if page > pages:
            return await app.send_message(msg.chat.id, 'Кол-во заданных страниц выходит за границы доступного.')

        for indx, plugin in enumerate(Data.description):
            if indx < (page-1)*30:
                continue

            help_text += f'{indx+1}) <code>{plugin}</code>({len(registers[plugin]["funcs"])})\n'

            if indx >= page*30:
                break
        
        help_text += f'\n<b>Страница: {page}/{pages}</b>' + '\n●Чтобы узнать о функции плагина, введите: /help {имя плагина}\n●Чтобы переходить на страницу, введите: для плагинов: /help 2, для команд: /help {имя плагина} 1'
    elif len(msg.text.split()) == 2:
        plugin = msg.text.split()[1]
        try:
            help_text = f'Описание плагина <code>{plugin}</code>:\n{dict(Data.description[plugin].__dict__)["main_description"].description}\n\nСписок функций плагина:\n'
        except KeyError:
            return await msg.edit_text('Плагин не найден.')

        PREFERRED_ORDER = ['.', '!', '/']
        
        funcs = Data.description[plugin].funcs_description

        pages = len(funcs) / 25
        if pages > int(pages): pages = int(pages) + 1

        try:
            for i, (func_name, func) in enumerate(funcs.items()):
                parameters = " ".join([" {" + parameter + "}" for parameter in func.parameters]) if func.parameters else ''
                help_text += f'<i>{i})</i> ' + '<b>{' + f'{", ".join(sorted(func.prefixes, key=lambda x: PREFERRED_ORDER.index(x) if x in PREFERRED_ORDER else 999))}' + '}</b>' + f'<code>{func.command}</code>{parameters}{func.hyphen}{func.description}\n'

                if i == 25:
                    break
        except KeyError:
            print(traceback.format_exc())
            help_text = 'Плагин не найден'
        
        help_text += f'\n<b>Страница: 1/{int(pages)}</b>' + '\n●Чтобы узнать о функции плагина, введите: /help {имя плагина}\n●Чтобы переходить на страницу, введите: для плагинов: /help 2, для команд: /help {имя плагина} 1\n<b>{...}</b> - доступные префиксы'
    elif len(msg.text.split()) == 3 and msg.text.split()[2].isdigit():
        plugin = msg.text.split()[1]
        try:
            help_text = f'Описание плагина <code>{plugin}</code>:\n{dict(Data.description[plugin].__dict__)["main_description"].description}\n\nСписок функций плагина:\n'
        except KeyError:
            help_text = 'Плагин не найден'

        try:
            page = int(msg.text.split()[2])
        except ValueError as e:
            return await msg.edit('Неверный номер страницы')
        
        PREFERRED_ORDER = ['.', '!', '/']
        
        funcs = Data.description[plugin].funcs_description

        pages = len(funcs) / 25
        if pages > int(pages): pages = int(pages) + 1

        try:
            for i, func_name, func in enumerate(funcs.items()):
                if i < (page-1)*25:
                    continue

                parameters = " ".join([" {" + parameter + "}" for parameter in func.parameters]) if func.parameters else ''
                help_text += f'<i>{i})</i> ' + '<b>{' + f'{", ".join(sorted(func.prefixes, key=lambda x: PREFERRED_ORDER.index(x) if x in PREFERRED_ORDER else 999))}' + '}</b>' + f'<code>{func.command}</code>{parameters}{func.hyphen}{func.description}\n'

                if i*page == 25:
                    break
        except KeyError:
            print(traceback.format_exc())
            help_text = 'Плагин не найден'
        
        help_text += f'\n<b>Страница: {page}/{int(pages)}' + '</b>\n●Чтобы узнать о функции плагина, введите: /help {имя плагина}\n●Чтобы переходить на страницу, введите: для плагинов: /help 2, для команд: /help {имя плагина} 1\n<b>{...}</b> - доступные префиксы'

    await msg.edit_text(help_text)

async def download_module(_, msg: types.Message):
    await app.edit_message_text(msg.chat.id, msg.id, 'Загрузка...')

    try:
        link = msg.text.split()[1]
        version = None

        if len(msg.text.split()) == 3:
            version = msg.text.split()[2]
    except IndexError:
        return await app.edit_message_text(msg.chat.id, msg.id, 'Вы не верно ввели параметры.Пример: /dwlmd {ссылка на зип из гит хаба}')
    
    if 'https://github.com/' not in link or not link.endswith('.zip'):
        return await app.edit_message_text(msg.chat.id, msg.id, 'Вы не верно ввели параметры.Пример: /dwlmd {ссылка на зип из гит хаба}')
    
    file_name = link.split("/")[-1][:-4]
    
    with open(f'plugins/{file_name}.zip', 'wb') as f:
        with requests.get(link, stream=True) as r:
            for chunk in alive_it(r.iter_content(chunk_size=512), title='Загрузка модуля', spinner=styles.SPINNERS['pulse'], theme='smooth'):
                f.write(chunk)
    
    os.makedirs('plugins/temp', exist_ok=True)
    
    with zipfile.ZipFile(f'plugins/{file_name}.zip', 'r') as zip_ref:
        zip_ref.extractall('plugins/temp')
    
    file_name = os.listdir('plugins/temp')[0]

    main_dir = os.listdir(f'plugins/temp/{file_name}')[0]
    
    merge_directories(f'plugins/temp/{file_name}/{main_dir}', f'plugins/{main_dir}')

    shutil.rmtree('plugins/temp')

    os.remove(f'plugins/main.zip')

    handle_plugin(main_dir)

    await app.edit_message_text(msg.chat.id, msg.id, 'Плагин успешно установлен/обновлён')

async def remove_plugin(_, msg: types.Message):
    global stop

    try:
        plugin_name = msg.text.split()[1]
    except IndexError:
        return await app.edit_message_text(msg.chat.id, msg.id, 'Вы не верно ввели параметры.Пример: /rmmd {имя плагина}')
    
    if plugin_name not in Data.cache:
        return await app.edit_message_text(msg.chat.id, msg.id, 'Плагин не найден.')

    if plugin_name in ['StartedPack', 'AnimationPack']:
        return await app.edit_message_text(msg.chat.id, msg.id, 'Этот плагин не может быть удалён.')
    
    os.remove(f'plugins/{plugin_name}')
    
    Data.cache.pop(plugin_name)
    
    try:
        Data.description.pop(plugin_name)
    except:
        pass

    await app.edit_message_text(msg.chat.id, msg.id, 'Плагин успешно удалён.')

async def update_script(_, msg: types.Message):
    global stop

    await msg.edit('Проверка обновлений...')
    
    _checking = check_update(this_version)
    
    if _checking[0]:
        await msg.edit(f'Обновление найдено, версия: {_checking[1]}, установка...')

        # Ссылка на официальный источник, так что вирусов не должно быть, нужно детально проверять ссылку(так же самое и в плагинах)
        link = 'https://github.com/flexyyyapk213/ModuFlex/archive/refs/heads/main.zip'

        with open(f'temp/main.zip', 'wb') as f:
            with requests.get(link, stream=True) as r:
                for chunk in alive_it(r.iter_content(chunk_size=512), title='Загрузка обновления', spinner=styles.SPINNERS['pulse'], theme='smooth'):
                    f.write(chunk)
        
        with zipfile.ZipFile(f'temp/main.zip', 'r') as zip_ref:
            zip_ref.extractall('temp')
        
        file_name = os.listdir('temp')

        for fil_name in file_name:
            if os.path.isdir('temp/'+fil_name):
                file_name = fil_name
                break

        _file_name = os.listdir(f'temp/{file_name}')

        spec = importlib.util.spec_from_file_location("__init__", f'temp/{file_name}/__init__.py')
        version = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(version)

        await asyncio.sleep(0.5)

        for module in alive_it(version.__modules__, title='Установка модулей', spinner=styles.SPINNERS['pulse'], theme='smooth'):
            if importlib.util.find_spec(module) is not None:
                continue
            subprocess.run(['pip', 'install', module], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        for fl_name in _file_name:
            try:
                if fl_name == 'botvenv':
                    continue
                
                if fl_name == 'config.ini':
                    continue

                if fl_name == 'plugins':
                    shutil.copytree(f'temp/{file_name}/{fl_name}', os.path.join(script_dir, fl_name), dirs_exist_ok=True)
                    continue

                if os.path.isfile(f'temp/{file_name}/{fl_name}') and os.path.exists(f'{os.path.split(__file__)[0]}/{fl_name}'):
                    os.remove(f'{os.path.split(__file__)[0]}/{fl_name}')
                
                if fl_name == '__pycache__':
                    continue
                
                if fl_name == 'temp':
                    continue
                
                shutil.move(f'temp/{file_name}/{fl_name}', f'{os.path.split(__file__)[0]}')
            except Exception as e:
                print(e)

        for fil_name in os.listdir('temp'):
            try:
                if os.path.isdir('temp/'+fil_name):
                    shutil.rmtree('temp/'+fil_name)
                    continue

                os.remove('temp/'+fil_name)
            except OSError:
                pass
            
            except Exception as e:
                print(e)

        await msg.edit(f'Обновление успешно установлено\n{version.__news__}\nПерезапуск скрипта...', parse_mode=ParseMode.MARKDOWN)

        stop = ScriptState.restart
    else:
        await msg.edit('Обновление не найдено')

async def modu_flex_state(_, msg: types.Message):
    global send_message
    
    await msg.edit_text(f"""```
 ____    ____  ________  
|_   \  /   _||_   __  |
  |   \/   |    | |_ \_|
  | |\  /| |    |  _|
 _| |_\/_| |_  _| |_
|_____||_____||_____|
```
Текущая версия: {this_version}
Обновление: {there_is_update if there_is_update else 'Нету'}
Количество плагинов: {len(Data.cache)}/{len(Data.cache) + Data.failed_modules}

**Параметры**:
    О старте отправлять: {'В избранное' if send_msg_onstart_up else 'В консоль'}
    Установка библиотек: {'Не спрашивать' if Data.ask_downloads else 'Спрашивать'}
    Обновлять библиотеки: {'При установке' if Data.one_download_libs else 'При запуске'}
    Проверка обновлении: {'Да' if Data.check_for_update else 'Нет'}
    Таймаут установки библ.: {Data.timeout_download_lib}с.
    """)

async def all_messages(app: Client, message: types.Message):
    asyncio.gather(send_update_function(app, message))

async def send_update_function(app: Client, message: types.Message):
    with ThreadPoolExecutor(20) as executor:
        command_with_plugin_activate = False
        original_text = message.text
        # Сделать определения для prefix, plugin_name, command_name
        prefix = None
        plugin_name = None
        command_name = None

        for pack_name in Data.cache:
            for _func in Data.cache[pack_name]['funcs'].values():
                chat_types = {
                        "ChatType.PRIVATE": "private",
                        "ChatType.CHANNEL": "channel",
                        "ChatType.GROUP": "chat",
                        "ChatType.SUPERGROUP": "chat",
                        "ChatType.BOT": "bot"
                    }
                
                if not (_func['type'] == chat_types[str(message.chat.type)] or (_func['type'] == 'all' or _func['type'] == 'default')):
                    continue
                
                text = message.text

                if _func['prefixes'] is not None:
                    if prefix is None or plugin_name is None or command_name is None:
                        for _prefix in _func['prefixes']:
                            if text.startswith(_prefix):
                                prefix = _prefix
                                break
                        else:
                            continue
                        
                        if text[1:].startswith(pack_name):
                            plugin_name = pack_name
                            text = prefix + text[len(pack_name) + 2:]
                        
                        if text[1:].startswith(_func['command_name']):
                            if len(Data.count_commands[_func['command_name']]) > 1:
                                try:
                                    command_with_plugin = ''
                                    for plugin in Data.count_commands[_func['command_name']]:
                                        command_with_plugin += f'\n`{prefix}{plugin}.{_func["command_name"]}`'

                                    await message.edit_text(f"Данная команда `{_func['command_name']}` существует в нескольких плагинах:{command_with_plugin}\n\nОтправьте один из вариантов.")
                                    break
                                except:
                                    continue
                            else:
                                command_name = _func['command_name']
                        else:
                            continue
                
                if command_name is not None: message.text = text
                
                if _func['filters'] is not None and not await _func['filters'](app, message):
                    continue
                
                if inspect.iscoroutinefunction(_func['func']):
                    asyncio.create_task(_func['func'](app, message))
                else:
                    executor.submit(_func['func'], app, message)

async def _stop(_, message: types.Message):
    global stop
    stop = ScriptState.exit

    await message.edit_text('Скрипт завершён.')

async def _restart(_, message: types.Message):
    global stop
    stop = ScriptState.restart

    await message.edit_text('Перезапуск...')

async def schedule_check_for_update(app: Client):
    global there_is_update

    _update = check_update(this_version)

    if there_is_update == _update[1]:
        auto_check_for_update.pause()
        return

    if _update[0]:
        if not send_msg_onstart_up:
            DecryptConfig(1)

            effect = Decrypt('Доступно новое обновление!Введите в чате /update для обновления.')
            with effect.terminal_output() as terminal:
                for frame in effect:
                    terminal.print(frame)
        else:
            await app.send_message('me', '👍Доступно новое обновление!', entities=[types.MessageEntity(type=enums.MessageEntityType.CUSTOM_EMOJI, offset=0, length=2, custom_emoji_id=6327717992268301521)])
        
        there_is_update = _update[1]
        auto_check_for_update.pause()

async def main(_app: Client, retries: int=None) -> int:
    global stop, app, features_of_the_version
    
    app = _app

    app.add_handler(MessageHandler(help, filters.command('help', ['.', '/', '!']) & filters.me))
    app.add_handler(MessageHandler(download_module, filters.command('dwlmd', ['.', '/', '!']) & filters.me))
    app.add_handler(MessageHandler(remove_plugin, filters.command('rmmd', ['.', '/', '!']) & filters.me))
    app.add_handler(MessageHandler(update_script, filters.command('update', ['.', '/', '!']) & filters.me))
    app.add_handler(MessageHandler(modu_flex_state, filters.command('moduflex', ['.', '/', '!']) & filters.me))
    app.add_handler(MessageHandler(_stop, filters.command('stop', ['.', '/', '!']) & filters.me))
    app.add_handler(MessageHandler(_restart, filters.command('restart', ['.', '/', '!']) & filters.me))
    
    check_updates()

    msgs = []

    for feature in features_of_the_version:
        if feature == 'you_are_tester':
            msg = await app.send_message('me', '👍ТЫ ТЕСТЕР!', entities=[types.MessageEntity(type=enums.MessageEntityType.CUSTOM_EMOJI, offset=0, length=2, custom_emoji_id=random.choice([
                6325685291621287657,
                6325462176660195024,
                5370853232098681087,
                6001555482865569587,
                6046478147837235883,
                6046554675564515809,
                5195083971842547465,
                5395448151865841306,
                5395855254635960960,
                5458602128375290972,
                5197335548317933406,
                5244673458083734407,
                5240108114006516325,
                5244946884291732268,
                5377583918297916260,
                5319006409830965724,
                5318977191168452300
            ]))])
        
        if feature == 'this_is_prerelease':
            await app.send_message('me', '👍Данная версия находится в бета релизе, возможны баги.', entities=[types.MessageEntity(type=enums.MessageEntityType.CUSTOM_EMOJI, offset=0, length=2, custom_emoji_id=5352964886584367997)])
        
        try:
            msgs.append(msg)
        except:
            pass

    
    if 'ModuFlex' not in Data.config:
        Data.config.update({"ModuFlex": Data.DEFAULT_MODUFLEX_CONFIG})
    else:
        for key in Data.DEFAULT_MODUFLEX_CONFIG:
            if key not in Data.config['ModuFlex'] or type(Data.DEFAULT_MODUFLEX_CONFIG[key]) != type(Data.config['ModuFlex'].get(key, '')):
                Data.config['ModuFlex'].update({key: copy.deepcopy(Data.DEFAULT_MODUFLEX_CONFIG[key])})
    
    Data.__save_config__()

    try:
        _date = datetime.strptime(Data.config['ModuFlex']['dwnlds_libs_date'], '%Y-%m-%d').date()
    except:
        _date = datetime(1970, 1, 1)

        Data.config['ModuFlex']['dwnlds_libs_date'] = datetime.today().date().strftime('%Y-%m-%d')

        Data.__save_config__()

    if _date == datetime.today().date():
        Data.skip_downloads = True
    
    if Data.check_for_update:
        auto_check_for_update.add_job(schedule_check_for_update, IntervalTrigger(minutes=10), (_app,))
        auto_check_for_update.start()
    
    handling_plg()

    handling_updates()

    if 'libs_is_dwnld' not in Data.config['ModuFlex']:
        Data.config['ModuFlex'].update({'libs_is_dwnld': True})

        Data.__save_config__()
    else:
        if not Data.config['ModuFlex']['libs_is_dwnld']:
            Data.config['ModuFlex']['libs_is_dwnld'] = True
        
            Data.__save_config__()

    app.add_handler(MessageHandler(all_messages))

    for _msg in msgs:
        await _msg.delete()
    
    try:
        del msgs
    except:
        pass

    try:
        del _msg
    except:
        pass

    print(pyfiglet.figlet_format("ModuFlex", font=random.choice(pyfiglet.FigletFont.getFonts())))

    if send_msg_onstart_up:
        if there_is_update:
            await app.send_message('me', '👍Доступно новое обновление!', entities=[types.MessageEntity(type=enums.MessageEntityType.CUSTOM_EMOJI, offset=0, length=2, custom_emoji_id=6327717992268301521)])
        # Увы, юзерам такое отправлять нельзя(
        msg = await app.send_message('me', '👍Юзер бот запущен', entities=[types.MessageEntity(type=enums.MessageEntityType.CUSTOM_EMOJI, offset=0, length=2, custom_emoji_id=random.choice([
            6204226842010847828,
            6325468301283558870,
            6203811806436132645,
            6206350076273494131,
            5384064740479747298,
            5456188142006575553,
            5456254812783910040,
            5244469322583120930
        ]))])
    else:
        effect = Rain('Скрипт запущен, подождите 5 секунд\nПриятного использования!')
        with effect.terminal_output() as terminal:
            for frame in effect:
                terminal.print(frame)
    
    start = time.time()

    if retries != None: retries -= 1

    stop = ScriptState.started

    while stop == ScriptState.started:
        await asyncio.sleep(1)

        if start is not None:
            if time.time() - start > 15:
                try:
                    await msg.delete()
                except:
                    pass
                finally:
                    start = None

    return stop