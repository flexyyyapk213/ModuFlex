import importlib.util
import subprocess

from __init__ import __modules__

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

from typing import Type
import time
import traceback

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

from loads import Data
from handling_plugins import handling_plugins as handling_plg, handle_plugin
from __init__ import __version__ as this_version

logging.basicConfig(filename='script.log', level=logging.WARN)

# Чистка логов
if os.path.getsize('script.log') >= 1_048_576:
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
except Exception as e:
    pass

there_is_update = False
features_of_the_version = []
stop = False

app = None

def check_updates():
    global there_is_update, features_of_the_version
    # Ссылка на официальный источник, так что вирусов не должно быть, нужно детально проверять ссылку(так же самое и в плагинах)
    link = 'https://github.com/flexyyyapk213/ModuFlex/archive/refs/heads/main.zip'

    with open(f'temp/main.zip', 'wb') as f:
        with requests.get(link, stream=True) as r:
            for chunk in alive_it(r.iter_content(chunk_size=512), title='Проверка обновления', spinner=styles.SPINNERS['pulse'], theme='smooth'):
                f.write(chunk)
    
    with zipfile.ZipFile(f'temp/main.zip', 'r') as zip_ref:
        zip_ref.extractall('temp')
    
    file_name = os.listdir('temp')

    for fil_name in file_name:
        if os.path.isdir('temp/'+fil_name):
            file_name = fil_name
            break
    
    version: str = __import__(f'temp.{file_name}.__init__', fromlist=['__version__']).__version__

    __version__ = __version.parse(this_version)

    _version = __version.parse(version)

    if __version__.is_prerelease:
        features_of_the_version.append('this_is_prerelease')

    if _version > __version__:
        if not send_msg_onstart_up:
            DecryptConfig(1)

            effect = Decrypt('Доступно новое обновление!Введите в чате /update для обновления.')
            with effect.terminal_output() as terminal:
                for frame in effect:
                    terminal.print(frame)
        else:
            there_is_update = True
    elif _version < __version__:
        features_of_the_version.append('you_are_tester')
        return
    
    for fil_name in os.listdir('temp'):
        try:
            if os.path.isdir('temp/'+fil_name):
                shutil.rmtree('temp/'+fil_name)
                continue

            os.remove('temp/'+fil_name)
        except OSError:
            pass
        
        except Exception as e:
            traceback.print_exc()

def handling_updates():
    updates: dict = Data.cache

    with ThreadPoolExecutor(max_workers=10) as executor:
        for func in Data.initializations:
            executor.submit(func, app)

    for update in updates:
        if not registers.get(update, False):
            registers.update({update: {"funcs": {}, "classes": {}}})

        for func_name, _func in updates[update]['funcs'].items():
            if registers[update]['funcs'].get(func_name, False):
                continue
            
            registers[update]['funcs'].update({func_name: _func['func']})

            if _func['type'] != 'default':
                continue

            app.add_handler(MessageHandler(_func['func'], _func['filters']))

async def help(_, msg: types.Message):
    help_text = ''

    await app.delete_messages(msg.chat.id, msg.id)

    if len(msg.text.split()) == 1:
        help_text = 'Список плагинов:\n0) <code>ModuFlex</code>&lt;MAIN&gt;\n'

        for indx, plugin in enumerate(Data.description):
            if plugin == 'ModuFlex':
                continue

            help_text += f'{indx+1}) <code>{plugin}</code>\n'

            if indx >= 30:
                break
        
        pages = len(Data.description)/30

        if pages > int(pages): pages = int(pages) + 1
        
        help_text += f'\n<b>Страница: 1/{pages}</b>' + '\n●Чтобы узнать о функции плагина, введите: /help {имя плагина}\n●Чтобы скачать плагин, введите: /dwlmd {ссылка на гит хаб зип файл}\n●Чтобы удалить плагин, введите: /rmmd {имя плагина}\n●Чтобы обновить скрипт, введите: /update\n●Чтобы переходить на страницу, введите: для плагинов: /help 2, для команд: /help имя_плагина 1'
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

            help_text += f'{indx+1}) <code>{plugin}</code>\n'

            if indx >= page*30:
                break
        
        help_text += f'\n<b>Страница: {page}/{pages}</b>' + '\n●Чтобы узнать о функции плагина, введите: /help {имя плагина}\n●Чтобы скачать плагин, введите: /dwlmd {ссылка на гит хаб зип файл}\n●Чтобы удалить плагин, введите: /rmmd {имя плагина}\n●Чтобы обновить скрипт, введите: /update\n●Чтобы переходить на страницу, введите: для плагинов: /help 2, для команд: /help имя_плагина 1'
    elif len(msg.text.split()) == 2:
        plugin = msg.text.split()[1]
        try:
            help_text = f'Описание плагина <code>{plugin}</code>:\n{dict(Data.description[plugin].__dict__)["main_description"].description}\n\nСписок функций плагина:\n'
        except KeyError:
            return await msg.edit('Плагин не найден.')

        funcs = dict(Data.description[plugin].__dict__.items())['args_description']

        pages = len(funcs)/25

        if pages > int(pages): pages = int(pages) + 1

        i = 1
        try:
            for func in funcs:
                parameters = " ".join([" {" + parameter + "}" for parameter in func.parameters]) if func.parameters else ''
                help_text += f'<i>{i})</i> ' + '<b>{' + f'{", ".join(func.prefixes)}' + '}</b>' + f'<code>{func.command}</code>{parameters}{func.hyphen}{func.description}\n'
                i += 1

                if i == 25:
                    break
        except KeyError:
            help_text = 'Плагин не найден'
        
        help_text += f'\n<b>Страница: 1/{pages}</b>' + '\n●Чтобы переходить на страницу, введите: для плагинов: /help 2, для команд: /help имя_плагина 1\n<b>{...}</b> - доступные префиксы'
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
        
        try:
            funcs = dict(Data.description[plugin].__dict__.items())['args_description']

            pages = len(funcs)/25

            if pages > int(pages): pages = int(pages) + 1

            if page > pages:
                return await app.send_message(msg.chat.id, 'Кол-во заданных страниц выходит за границы доступного.')
        except KeyError:
            help_text = 'Плагин не найден'
            pages = 0

        i = 1
        try:
            for func in funcs:
                if i < (page-1)*25:
                    i += 1
                    continue

                parameters = " ".join([" {" + parameter + "}" for parameter in func.parameters]) if func.parameters else ''
                help_text += f'<i>{i})</i> ' + '<b>{' + f'{", ".join(func.prefixes)}' + '}</b>' + f'<code>{func.command}</code>{parameters}{func.hyphen}{func.description}\n'
                i += 1
                if i == page*25:
                    break
        except KeyError:
            help_text = 'Плагин не найден'
        
        help_text += f'\n<b>Страница: {page}/{pages}' + '</b>\n●Чтобы переходить на страницу, введите: для плагинов: /help 2, для команд: /help имя_плагина 1\n<b>{...}</b> - доступные префиксы'

    await app.send_message(msg.chat.id, help_text)

async def download_module(_, msg: types.Message):
    await app.edit_message_text(msg.chat.id, msg.id, 'Загрузка...')

    try:
        link = msg.text.split()[1]
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

    for fl_name in os.listdir(f'plugins/temp/{file_name}'):
        shutil.move(f'plugins/temp/{file_name}/{fl_name}', f'plugins/{fl_name}')

    shutil.rmtree('plugins/temp')

    os.remove(f'plugins/{file_name}.zip')

    handle_plugin(file_name)

    await app.edit_message_text(msg.chat.id, msg.id, 'Плагин успешно установлен')

async def remove_plugin(_, msg: types.Message):
    global stop

    try:
        plugin_name = msg.text.split()[1]
    except IndexError:
        return await app.edit_message_text(msg.chat.id, msg.id, 'Вы не верно ввели параметры.Пример: /rmmd {имя плагина}')
    
    if plugin_name not in Data.description:
        return await app.edit_message_text(msg.chat.id, msg.id, 'Плагин не найден')

    if plugin_name in ['StartedPack', 'AnimationPack']:
        return await app.edit_message_text(msg.chat.id, msg.id, 'Этот плагин не может быть удалён')
    
    os.remove(f'plugins/{plugin_name}')
    
    for plugin in Data.cache['funcs']:
        if Data.cache['funcs'][plugin]['PackName'] == plugin_name:
            Data.cache['funcs'].pop(plugin)
    
    Data.description.pop(plugin_name)

    await app.edit_message_text(msg.chat.id, msg.id, 'Плагин успешно удалён, происходит перезапуск скрипта.')

    await asyncio.sleep(1)

    stop = True

async def update_script(_, msg: types.Message):
    global stop

    await msg.edit('Проверка обновлений...')
    
    # Ссылка на официальный источник, так что вирусов не должно быть, нужно детально проверять ссылку(так же самое и в плагинах)
    link = 'https://github.com/flexyyyapk213/ModuFlex/archive/refs/heads/main.zipp'

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
    
    if __version.parse((version := __import__(f'temp.{file_name}.__init__', fromlist=['__version__', '__modules__'])).__version__) > __version.parse(this_version):
        if not __version.parse(python_version()) >= __version.parse('3.8'):
            return await msg.edit('Обновление найдено, но версия интерпретатора не подходит(требуется 3.8 и больше)')

        await msg.edit(f'Обновление найдено, версия: {version.__version__}, установка...')

        await asyncio.sleep(0.5)

        for module in alive_it(version.__modules__, title='Установка модулей', spinner=styles.SPINNERS['pulse'], theme='smooth'):
            if importlib.util.find_spec(module) is not None:
                continue
            subprocess.run(['pip', 'install', module], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        script_dir = os.path.dirname(os.path.abspath(__file__))

        botvenv_has_been_changed = False
        
        botvenv_python_version = subprocess.run([f'temp/{file_name}/botvenv/Scripts/python.exe', '-V'], stdout=subprocess.PIPE)

        if botvenv_python_version.stdout.decode('utf-8').split(maxsplit=1)[1] != python_version():
            botvenv_has_been_changed = True
        
        for fl_name in _file_name:
            if fl_name == 'botvenv' and not botvenv_has_been_changed:
                continue
            else:
                shutil.copytree(f'temp/{file_name}', script_dir, dirs_exist_ok=True)
            
            if fl_name == 'config.ini':
                continue

            if fl_name == 'plugins':
                shutil.copytree(f'temp/{file_name}/{fl_name}', os.path.join(script_dir, fl_name), dirs_exist_ok=True)
                continue

            if os.path.isfile(f'temp/{file_name}/{fl_name}') and os.path.exists(f'{os.path.split(__file__)[0]}/{fl_name}'):
                os.remove(f'{os.path.split(__file__)[0]}/{fl_name}')
            
            if fl_name == 'temp':
                continue
            
            shutil.move(f'temp/{file_name}/{fl_name}', f'{os.path.split(__file__)[0]}')

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

        stop = True
    else:
        await msg.edit('Обновление не найдено')

async def send_version(_, msg: types.Message):
    await app.send_message(msg.chat.id, f'Обновление: {"Есть" if there_is_update else "Нету"}\nТекущая версия: {this_version}')

async def all_messages(app: Client, message: types.Message):
    asyncio.gather(send_update_function(app, message))

async def send_update_function(app: Client, message: types.Message):
    with ThreadPoolExecutor(20) as executor:
        for pack_name in Data.cache:
            for func_name, _func in Data.cache[pack_name]['funcs'].items():
                chat_types = {
                        "ChatType.PRIVATE": "private",
                        "ChatType.CHANNEL": "channel",
                        "ChatType.GROUP": "chat",
                        "ChatType.SUPERGROUP": "chat",
                        "ChatType.BOT": "bot"
                    }
                
                if _func['type'] == chat_types[str(message.chat.type)] or _func['type'] == 'all':
                    if inspect.iscoroutinefunction(_func['func']):
                        asyncio.create_task(_func['func'](app, message))
                    else:
                        executor.submit(_func['func'], app, message)

async def main(_app: Client, retries: int=None):
    global stop, app, features_of_the_version

    app = _app

    app.add_handler(MessageHandler(help, filters.command('help', ['.', '/', '!']) & filters.me))
    app.add_handler(MessageHandler(download_module, filters.command('dwlmd', ['.', '/', '!']) & filters.me))
    app.add_handler(MessageHandler(remove_plugin, filters.command('rmmd', ['.', '/', '!']) & filters.me))
    app.add_handler(MessageHandler(update_script, filters.command('update', ['.', '/', '!']) & filters.me))
    app.add_handler(MessageHandler(send_version, filters.command('version', ['.', '/', '!']) & filters.me))
    
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
            await app.send_message('me', '👍Данная версия находится в бета релизе, возможны баги!!!', entities=[types.MessageEntity(type=enums.MessageEntityType.CUSTOM_EMOJI, offset=0, length=2, custom_emoji_id=5352964886584367997)])
        
        try:
            msgs.append(msg)
        except:
            pass
    
    handling_plg()

    handling_updates()

    app.add_handler(MessageHandler(all_messages))

    for _msg in msgs:
        await _msg.delete()
    
    del msgs
    del _msg

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

    while not stop:
        await asyncio.sleep(1)

        if start is not None:
            if time.time() - start > 15:
                try:
                    await msg.delete()
                except:
                    pass
                finally:
                    start = None