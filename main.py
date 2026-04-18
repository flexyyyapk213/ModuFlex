import asyncio
import copy
import importlib.util
import inspect
import os
import random
import re
import shutil
import subprocess
import time
import traceback
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Dict
import json
import logging
import sys

import pyfiglet
from quart import Quart
import requests
import aiohttp
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from packaging import version
from packaging.specifiers import SpecifierSet
from pyrogram import Client, filters, enums, types
from pyrogram.enums import ParseMode
from pyrogram.handlers import MessageHandler

from alive_progress import alive_it, styles, alive_bar
from handling_plugins import handling_plugins as handling_plg, handle_plugin
from loads import Data, ScriptState
from terminaltexteffects.effects.effect_decrypt import Decrypt, DecryptConfig
from terminaltexteffects.effects.effect_rain import Rain
from utils import merge_directories, __find_command_name__, check_update, get_config_data

from __init__ import __modules__, __news__
from __init__ import __version__ as this_version
from web import app as approute

registers = {}

try:
    with open("config.ini", "r") as cfg:
        file = cfg.read()
    
    api_id = re.search(r'api_id\s*=\s*(\d+)', file)
    api_hash = re.search(r'api_hash\s*=\s*[\'"](.*?)[\'"]', file)

    phone_number = re.search(r'phone_number\s*=\s*(\d+)', file)
    password = re.search(r'password\s*=\s*[\'"](.*?)[\'"]', file)

    __config__ = get_config_data()

    send_msg_onstart_up = __config__['send_message_on_startup']

    if __config__['ask_to_downloads'] is not None: Data.ask_downloads = __config__['ask_to_downloads']

    if __config__['one_download_libs'] is not None: Data.one_download_libs = __config__['one_download_libs']

    if __config__['check_for_update'] is not None: Data.check_for_update = __config__['check_for_update']

    if __config__['timeout_download_lib'] is not None: Data.timeout_download_lib = __config__['timeout_download_lib']
except FileNotFoundError:
    print('Файл конфигурации не был обнаружен.Создайте в корне папке файл config.ini и введите свои данные.(Подробнее в contribution.md)')
    sys.exit()

there_is_update = False
features_of_the_version = []
stop = ScriptState.started
logger = logging.getLogger(__name__)

app = None

def check_updates():
    global there_is_update, features_of_the_version
    # Ссылка на официальный источник, так что вирусов не должно быть, нужно детально проверять ссылку(так же самое и в плагинах)
    link = 'https://raw.githubusercontent.com/flexyyyapk213/ModuFlex/main/__init__.py'
    fresh_version = version.parse(re.search(r'__version__ = \'(.*?)\'', requests.get(link, headers={'User-Agent': 'Mozilla/5.0'}).text).group(1))
    version_now = version.parse(this_version)

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
            registers.update({update: {"funcs": {}, "classes": {}, "routes": {}}})

        for func_name, _func in updates[update]['funcs'].items():
            if registers[update]['funcs'].get(func_name, False):
                continue
            
            if _func['command_name'] is not None:
                if _func['command_name'] in Data.count_commands:
                    Data.count_commands[_func['command_name']].append(update)
                else:
                    Data.count_commands.update({_func['command_name']: [update]})
            
            registers[update]['funcs'].update({func_name: _func['func']})
        
        for class_id, _class in updates[update]['classes'].items():
            if registers[update]['classes'].get(class_id, False):
                continue

            registers[update]['classes'].update({class_id: {"class": _class['class'], "methods": {}}})

            for method_name, method in _class['methods'].items():
                if registers[update]['classes'][class_id]['methods'].get(method_name, {}).get('method', False) != method['method']:
                    continue

                if method['command_name'] is not None:
                    if method['command_name'] in Data.count_commands:
                        Data.count_commands[method['command_name']].append(update)
                    else:
                        Data.count_commands.update({method['command_name']: [update]})
                
                registers[update]['classes'][class_id]['methods'].update({method_name: method['method']})
        
        #NOTE: Experimental
        if updates[update]['routes'].get('blueprint', False) and Data.experimental:
            
            registers[update]['routes'].update({"funcs": {}, "methods": {}})

            for key, value in updates[update]['routes']['funcs'].items():
                if registers[update]['routes']['funcs'].get(key, False):
                    continue

                updates[update]['routes']['blueprint'].add_url_rule(view_func=value['func'], **value['parameters'])

                registers[update]['routes']['funcs'].update({value['func'].__name__: {"func": value['func'], "parameters": value['parameters']}})
            
            for method_name, method in updates[update]['routes']['methods'].items():
                if registers[update]['routes']['methods'].get(method_name, False):
                    continue

                updates[update]['routes']['blueprint'].add_url_rule(view_func=getattr(updates[update]['classes'][method['class_id']]['class'], method['method'].__name__), **method['parameters'])

                registers[update]['routes']['methods'].update({method['method'].__name__: {"method": method['method'], "class_id": method['class_id'], "parameters": method['parameters']}})
            
            approute.register_blueprint(updates[update]['routes']['blueprint'])

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
    elif len(msg.text.split()) == 2 and msg.text.split()[1].isnumeric():
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
                help_text += f'<i>{i})</i> ' + '<b>{' + f'{", ".join(sorted(func.prefixes or ["/"], key=lambda x: PREFERRED_ORDER.index(x) if x in PREFERRED_ORDER else 999))}' + '}</b>' + f'<code>{func.command}</code>{parameters}{func.hyphen}{func.description or "Описание отсутствует."}\n'

                if i == 25:
                    break
        except KeyError:
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
                help_text += f'<i>{i})</i> ' + '<b>{' + f'{", ".join(sorted(func.prefixes or ["/"], key=lambda x: PREFERRED_ORDER.index(x) if x in PREFERRED_ORDER else 999))}' + '}</b>' + f'<code>{func.command}</code>{parameters}{func.hyphen}{func.description or "Описание отсутствует."}\n'

                if i*page == 25:
                    break
        except KeyError:
            help_text = 'Плагин не найден'
        
        help_text += f'\n<b>Страница: {page}/{int(pages)}' + '</b>\n●Чтобы узнать о функции плагина, введите: /help {имя плагина}\n●Чтобы переходить на страницу, введите: для плагинов: /help 2, для команд: /help {имя плагина} 1\n<b>{...}</b> - доступные префиксы'

    await msg.edit_text(help_text)

async def download_module(app: Client, msg: types.Message):
    await msg.edit_text('Загрузка...')

    if os.path.exists(os.path.join(os.path.dirname(__file__), 'plugins', 'temp')):
        shutil.rmtree(os.path.join(os.path.dirname(__file__), 'plugins', 'temp'))

    try:
        json_manifest = None
        is_old_format = False

        try:
            link = msg.text.split()[1]
            _version = None

            if len(msg.text.split()) == 3:
                _version = ' '.join(msg.text.split()[2:])
        except IndexError:
            return await app.edit_message_text(msg.chat.id, msg.id, 'Вы не верно ввели параметры.Пример: /dwlmd {ссылка на гит хаб репозиторий}')
        
        if 'https://github.com/' not in link:
            return await app.edit_message_text(msg.chat.id, msg.id, 'Вы не верно ввели параметры.Пример: /dwlmd {ссылка на гит хаб репозиторий}')

        async with aiohttp.ClientSession() as session:
            link_path = link.split('/')
            _author = link_path[3]
            repo_name = link_path[4]

            async with session.get('https://raw.githubusercontent.com/' + link_path[3] + '/' + link_path[4] + '/main/manifest.json') as file_manifest:
                try:
                    if file_manifest.status == 404:
                        await app.edit_message_text(msg.chat.id, msg.id, 'Загрузка...(Устаревший формат плагина, могут быть сбои)')
                        is_old_format = True
                    else:
                        manifest = await file_manifest.text('utf-8')

                        json_manifest = json.loads(manifest)
                        
                        spec = SpecifierSet(json_manifest['mf_version'])

                        if not spec.contains(version.parse(this_version)):
                            return await app.edit_message_text(msg.chat.id, msg.id, f'Плагин устарел и не поддерживает версию ModuFlex {this_version}')
                        
                        try:
                            if json_manifest['name'] in Data.modules:
                                with open(f'plugins/{json_manifest["name"]}/manifest.json') as f:
                                    _manifest = json.load(f)
                                
                                current_version = version.parse(_manifest['version'])
                                new_version = version.parse(json_manifest['version'])

                                if not current_version < new_version:
                                    return await app.edit_message_text(msg.chat.id, msg.id, f'Плагин не нуждается в обновлении.')
                        except FileNotFoundError as e:
                            logging.debug(traceback.format_exc())
                except TypeError as e:
                    logging.debug(traceback.format_exc())
                    
                    return await app.edit_message_text(msg.chat.id, msg.id, 'Ошибка скачивания плагина(См. в log.log)')
            
            if is_old_format:
                return await old_download_module(app, msg, link_path=link_path, link=link)

            os.makedirs('plugins/temp/module', exist_ok=True)
            
            with open(f'plugins/temp/main.zip', 'wb') as f:
                async with session.get('https://github.com/' + _author + '/' + repo_name + '/archive/refs/heads/main.zip') as r:
                    total_size = int(r.headers.get('Content-Length', 0))

                    with alive_bar(total_size, title='Загрузка модуля', spinner=styles.SPINNERS['pulse'], theme='smooth') as bar:
                        async for chunk in r.content.iter_chunked(512):
                            f.write(chunk)

                            bar(len(chunk))
            
            with zipfile.ZipFile(f'plugins/temp/main.zip', 'r') as zip_ref:
                for member in zip_ref.namelist():
                    abs_path = os.path.abspath(os.path.join('plugins/temp/module', member))
                    if not abs_path.startswith(os.path.abspath('plugins/temp/module')):
                        raise Exception("Обнаружена попытка path traversal!")
                
                zip_ref.extractall('plugins/temp/module')
            
            os.remove(f'plugins/temp/main.zip')

            os.makedirs(f'plugins/{json_manifest["name"]}', exist_ok=True)

            source_dir_name = next(
                (item for item in os.listdir('plugins/temp/module/') if os.path.isdir(os.path.join('plugins/temp/module/', item))), 
                ''
            )

            merge_directories(os.path.join('plugins/temp/module/' + source_dir_name), f'plugins/{json_manifest["name"]}')

            shutil.rmtree(os.path.join(os.path.dirname(__file__), 'plugins', 'temp'))

            handle_plugin(json_manifest["name"])
    except Exception as e:
        logger.error(traceback.format_exc())
        
        return await msg.edit('Произошла ошибка(см. в файле log.log)')
    finally:
        if os.path.exists(os.path.join(os.path.dirname(__file__), 'plugins', 'temp')):
            shutil.rmtree(os.path.join(os.path.dirname(__file__), 'plugins', 'temp'))

    await msg.edit(f'Плагин успешно установлен!\n{json_manifest["name"]} v{json_manifest["version"]}\n{json_manifest["description"]}\n\nАвтор: {json_manifest["author"]}\nРепозиторий: {json_manifest["repository"]}', parse_mode=ParseMode.MARKDOWN)

async def old_download_module(app: Client, msg: types.Message, link_path, link):
    """
    Старый способ установки, крайне не рекомендуется скачивать плагины, которые не поддерживают версию >=0.1.0b2
    Этот способ установки скоро будет вырезан.
    """
    file_name = link_path[-1][:-4]
    
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

async def remove_plugin(app: Client, msg: types.Message):
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

async def update_script(app: Client, msg: types.Message):
    global stop

    await msg.edit('Проверка обновлений...')
    
    _checking = check_update(this_version)
    
    if _checking[0]:
        await msg.edit(f'Обновление найдено, версия: {_checking[1]}, установка...')

        # Ссылка на официальный источник, так что вирусов не должно быть, нужно детально проверять ссылку(так же самое и в плагинах)
        link = 'https://github.com/flexyyyapk213/ModuFlex/archive/refs/heads/main.zip'

        try:
            with open(f'temp/main.zip', 'wb') as f:
                with requests.get(link, stream=True) as r:
                    for chunk in alive_it(r.iter_content(chunk_size=512), title='Загрузка обновления', spinner=styles.SPINNERS['pulse'], theme='smooth'):
                        f.write(chunk)
        except FileNotFoundError:
            os.mkdir("temp")

            return await update_script(app, msg)
        
        with zipfile.ZipFile(f'temp/main.zip', 'r') as zip_ref:
            zip_ref.extractall('temp')
        
        dir_name = zip_ref.namelist[0]

        _file_name = os.listdir(f'temp/{dir_name}')

        spec = importlib.util.spec_from_file_location("__init__", f'temp/{dir_name}/__init__.py')
        version = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(version)

        await asyncio.sleep(0.5)

        for module in alive_it(version.__modules__, title='Установка модулей', spinner=styles.SPINNERS['pulse'], theme='smooth'):
            if importlib.util.find_spec(module) is None:
                subprocess.run([sys.executable, 'install', module], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        for fl_name in _file_name:
            try:
                if os.path.exists(fl_name) and os.path.isfile(os.path.join('temp', dir_name, fl_name)):
                    os.remove(fl_name)
                    shutil.move(os.path.join('temp', dir_name, fl_name), '.')
                elif os.path.exists(fl_name) and os.path.isdir(os.path.join('temp', dir_name, fl_name)):
                    shutil.copytree(os.path.join('temp', dir_name, fl_name), fl_name, dirs_exist_ok=True)
                else:
                    shutil.move(os.path.join('temp', dir_name, fl_name), '.')
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

        Data.config['ModuFlex']['libs_is_dwnld'] = False
        
        await msg.edit(f'Обновление успешно установлено\n{version.__news__}\nПерезапуск скрипта...', parse_mode=ParseMode.MARKDOWN)

        stop = ScriptState.restart
    else:
        await msg.edit('Обновление не найдено')

async def modu_flex_state(_, msg: types.Message):
    global send_message
    
    with open('script.log', encoding='utf-8') as log:
        logs_text = ''.join(log.readlines()[-3:])
    
    await msg.edit_text(fr"""```moduflex
 ____    ____  ________  
|_   \  /   _||_   __  |
  |   \/   |    | |_ \_|
  | |\  /| |    |  _|
 _| |_\/_| |_  _| |_
|_____||_____||_____|
```
```Логи
{logs_text}
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
    Экспериментальный режим: {'Да' if Data.experimental else 'Нет'}
    """)

async def send_update_function(app: Client, message: types.Message):
    with ThreadPoolExecutor(20) as executor:
        prefix = None
        plugin_name = None
        command_name = None

        for pack_name in Data.cache:
            for classes in Data.cache[pack_name]['classes'].values():
                for _func in classes['methods'].values():
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

                    if _func['prefixes'] is not None and text is not None:
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
                    
                    if inspect.iscoroutinefunction(_func['method']):
                        asyncio.create_task(getattr(classes['class'], _func['method'].__name__)(app, message))
                        continue
                    else:
                        executor.submit(getattr(classes['class'], _func['method'].__name__), app, message)
                        continue
            
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

                if _func['prefixes'] is not None and text is not None:
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

async def schedule_check_for_update(app: Client, auto_check_for_update):
    global there_is_update

    _update = check_update(this_version)

    if there_is_update == _update[1]:
        auto_check_for_update.shutdown()
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
        auto_check_for_update.shutdown()

async def check_plugin_for_webinterface(_, message: types.Message):
    try:
        plugin_name = message.text.split()[1]
    except IndexError:
        return await message.edit_text('Вы не верно ввели параметры: /webi {ИмяПлагина}')
    
    if plugin_name not in Data.cache:
        return await message.edit_text(f'Этот плагин `{plugin_name}` не существует.', parse_mode=ParseMode.MARKDOWN)
    
    if not Data.cache[plugin_name]['routes']['funcs'] and not Data.cache[plugin_name]['routes']['methods']:
        return await message.edit_text(f'У этого плагина `{plugin_name}` нету страницы на сайте.', parse_mode=ParseMode.MARKDOWN)
    
    return await message.edit_text(f'У данного плагина существует своя страница.\nhttp://127.0.0.1:1205/{plugin_name}/')

class ModuFlex:
    def __init__(self, app: Client, approute: Quart, is_basic: bool=False, **kwargs):
        self.stop = ScriptState.started
        self.app = app
        self.auto_check_for_update = AsyncIOScheduler()
        self.features_of_the_version = []
        self.registers = {}
        self.logger = logging.getLogger(__name__)
        self.there_is_update = False
        self.is_basic = is_basic
        self.approute = approute
        self.is_init = False

    async def run(self) -> ScriptState:
        self.app.add_handler(MessageHandler(help, filters.command('help', ['.', '/', '!']) & filters.me))
        self.app.add_handler(MessageHandler(download_module, filters.command('dwplg', ['.', '/', '!']) & filters.me))
        self.app.add_handler(MessageHandler(remove_plugin, filters.command('rmplg', ['.', '/', '!']) & filters.me))
        self.app.add_handler(MessageHandler(update_script, filters.command('update', ['.', '/', '!']) & filters.me))
        self.app.add_handler(MessageHandler(modu_flex_state, filters.command('moduflex', ['.', '/', '!']) & filters.me))
        self.app.add_handler(MessageHandler(self._stop, filters.command('stop', ['.', '/', '!']) & filters.me))
        self.app.add_handler(MessageHandler(self._restart, filters.command('restart', ['.', '/', '!']) & filters.me))
        self.app.add_handler(MessageHandler(check_plugin_for_webinterface, filters.command('webi', ['.', '/', '!']) & filters.me))
        self.app.add_handler(MessageHandler(self.all_messages))

        self.check_updates()

        msgs = []

        for feature in self.features_of_the_version:
            if feature == 'you_are_tester':
                msg = await self.app.send_message('me', '👍ТЫ ТЕСТЕР!', entities=[types.MessageEntity(type=enums.MessageEntityType.CUSTOM_EMOJI, offset=0, length=2, custom_emoji_id=random.choice([
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
                await self.app.send_message('me', '👍Данная версия находится в бета релизе, возможны баги.', entities=[types.MessageEntity(type=enums.MessageEntityType.CUSTOM_EMOJI, offset=0, length=2, custom_emoji_id=5352964886584367997)])
            
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
            
            try:
                _date = datetime.strptime(Data.config['ModuFlex']['dwnlds_libs_date'], '%Y-%m-%d').date()
            except:
                _date = datetime(1970, 1, 1)

                Data.config['ModuFlex']['dwnlds_libs_date'] = datetime.today().date().strftime('%Y-%m-%d')

            if _date == datetime.today().date():
                Data.skip_downloads = True
        
        Data.__save_config__()
        
        if Data.check_for_update:
            self.auto_check_for_update.add_job(schedule_check_for_update, IntervalTrigger(minutes=10), (self.app, self.auto_check_for_update))
            self.auto_check_for_update.start()
        
        if self.is_basic: handling_plg()

        self.handling_updates()

        if 'libs_is_dwnld' not in Data.config['ModuFlex']:
            Data.config['ModuFlex'].update({'libs_is_dwnld': True})

            Data.__save_config__()
        else:
            if not Data.config['ModuFlex']['libs_is_dwnld']:
                Data.config['ModuFlex']['libs_is_dwnld'] = True
            
                Data.__save_config__()
        
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

        def endless_dummy():
            return asyncio.Future()

        #NOTE: Experimental
        if Data.experimental and self.is_basic: server_task = asyncio.create_task(self.approute.run_task(port=1205, shutdown_trigger=endless_dummy))

        if send_msg_onstart_up:
            if self.there_is_update:
                await self.app.send_message('me', '👍Доступно новое обновление!', entities=[types.MessageEntity(type=enums.MessageEntityType.CUSTOM_EMOJI, offset=0, length=2, custom_emoji_id=6327717992268301521)])

            msg = await self.app.send_message('me', '👍Юзер бот запущен' + ('.\nЛокальный сайт: http://127.0.0.1:1205' if Data.experimental else ''), entities=[types.MessageEntity(type=enums.MessageEntityType.CUSTOM_EMOJI, offset=0, length=2, custom_emoji_id=random.choice([
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

        self.is_init = True

        while self.stop == ScriptState.started:
            await asyncio.sleep(1)

            if start is not None:
                if time.time() - start > 15 + 45 if Data.experimental else 0:
                    try:
                        await msg.delete()
                    except:
                        pass
                    finally:
                        start = None

        self.auto_check_for_update.shutdown()
        
        #NOTE: Experimental
        if Data.experimental and self.is_basic: server_task.cancel()

        # #NOTE: Experimental
        if Data.experimental and self.is_basic:
            try:
                await server_task
            except asyncio.CancelledError:
                pass

        return self.stop
    
    def check_updates(self):
        # Ссылка на официальный источник, так что вирусов не должно быть, нужно детально проверять ссылку(так же самое и в плагинах)
        link = 'https://raw.githubusercontent.com/flexyyyapk213/ModuFlex/main/__init__.py'
        fresh_version = version.parse(re.search(r'__version__ = \'(.*?)\'', requests.get(link, headers={'User-Agent': 'Mozilla/5.0'}).text).group(1))
        version_now = version.parse(this_version)

        if version_now.is_prerelease:
            self.features_of_the_version.append('this_is_prerelease')
        
        if fresh_version > version_now:
            if not send_msg_onstart_up:
                DecryptConfig(1)

                effect = Decrypt('Доступно новое обновление!Введите в чате /update для обновления.')
                with effect.terminal_output() as terminal:
                    for frame in effect:
                        terminal.print(frame)
            self.there_is_update = fresh_version
        elif fresh_version < version_now:
            self.features_of_the_version.append('you_are_tester')
    
    def handling_updates(self):
        updates: Dict = Data.cache

        with ThreadPoolExecutor(max_workers=10) as executor:
            for func in Data.initializations:
                executor.submit(func, self.app)

        for update in updates:
            if not self.registers.get(update, False):
                self.registers.update({update: {"funcs": {}, "classes": {}, "routes": {}}})

            for func_name, _func in updates[update]['funcs'].items():
                if self.registers[update]['funcs'].get(func_name, False):
                    continue
                
                if _func['command_name'] is not None and self.is_basic:
                    if _func['command_name'] in Data.count_commands:
                        Data.count_commands[_func['command_name']].append(update)
                    else:
                        Data.count_commands.update({_func['command_name']: [update]})
                
                self.registers[update]['funcs'].update({func_name: _func['func']})
            
            for class_id, _class in updates[update]['classes'].items():
                if self.registers[update]['classes'].get(class_id, False):
                    continue

                _class['class'](self.app)
                
                self.registers[update]['classes'].update({class_id: {"class": _class['class'], "methods": {}}})
                
                for method_name, method in _class['methods'].items():
                    if self.registers[update]['classes'][class_id]['methods'].get(method_name, {}).get('method', False):
                        continue
                    
                    if method['command_name'] is not None and self.is_basic:
                        if method['command_name'] in Data.count_commands:
                            Data.count_commands[method['command_name']].append(update)
                        else:
                            Data.count_commands.update({method['command_name']: [update]})
                    
                    self.registers[update]['classes'][class_id]['methods'].update({method_name: method['method']})
            
            #NOTE: Experimental
            if updates[update]['routes'].get('blueprint', False) and Data.experimental and self.is_basic:
                
                self.registers[update]['routes'].update({"funcs": {}, "methods": {}})

                for key, value in updates[update]['routes']['funcs'].items():
                    if self.registers[update]['routes']['funcs'].get(key, False):
                        continue

                    updates[update]['routes']['blueprint'].add_url_rule(view_func=value['func'], **value['parameters'])

                    self.registers[update]['routes']['funcs'].update({value['func'].__name__: {"func": value['func'], "parameters": value['parameters']}})
                
                for method_name, method in updates[update]['routes']['methods'].items():
                    if registers[update]['routes']['methods'].get(method_name, False):
                        continue

                    updates[update]['routes']['blueprint'].add_url_rule(view_func=getattr(updates[update]['classes'][method['class_id']]['class'], method['method'].__name__), **method['parameters'])

                    self.registers[update]['routes']['methods'].update({method['method'].__name__: {"method": method['method'], "class_id": method['class_id'], "parameters": method['parameters']}})
                
                if self.is_basic: self.approute.register_blueprint(updates[update]['routes']['blueprint'])
    
    async def _stop(self, _, message: types.Message):
        self.stop = ScriptState.exit

        await message.edit_text('Скрипт завершён.')

    async def _restart(self, _, message: types.Message):
        self.stop = ScriptState.restart

        await message.edit_text('Перезапуск...')
    
    async def all_messages(self, app: Client, message: types.Message):
        if not self.is_init: return
        asyncio.gather(send_update_function(app, message))