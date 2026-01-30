import importlib.util
import json
import logging
import logging.handlers
import os
import re
import subprocess
import sys
from pathlib import Path

file_handler = logging.handlers.RotatingFileHandler(
    'script.log',
    maxBytes=1024 * 42,
    backupCount=3,
    encoding='utf-8'
)

console_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

root_logger = logging.getLogger()
root_logger.setLevel(logging.WARNING)

root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

venv_path = Path(sys.executable)

try:
    with open('config.ini') as f:
        text = f.read()

        use_botvenv = re.search(r'use_botvenv\s*=\s*(true|false)', text)

        experimental = re.search(r'experimental\s*=\s*(true|false)', text)

        if use_botvenv is not None: use_botvenv = {"true": True, "false": False}[use_botvenv.group(1)]
        else: use_botvenv = True

        if experimental is not None: experimental = {"true": True, "false": False}[experimental.group(1)]
        else: experimental = False
except FileNotFoundError:
    print('Файл конфигурации не был обнаружен.Создайте в корне папке файл config.ini и введите свои данные.(Подробнее в contribution.md)')
    exit()

# Run with botvenv
if list(venv_path.parts)[-3] != 'botvenv' and use_botvenv:
    path_to_bot = Path(__file__)

    folders = [entry.name for entry in os.scandir(path_to_bot.parents[0]) if entry.is_dir()]

    if 'botvenv' not in folders:
        if importlib.util.find_spec('venv') is None:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'venv'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        subprocess.run([sys.executable, '-m', 'venv', 'botvenv'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    path_to_botvenv = Path(__file__)

    if sys.platform == 'win32':
        if (path_to_botvenv.parents[0] / 'botvenv' / 'Scripts').exists() and (path_to_botvenv.parents[0] / 'botvenv' / 'Scripts' / 'python.exe').is_file():
            python_exc = [str(path_to_bot.parents[0] / 'botvenv' / 'Scripts' / 'python.exe'), str(path_to_bot.parents[0] / 'run.py')]
    else:
        if (path_to_botvenv.parents[0] / 'botvenv' / 'bin').exists() and (path_to_botvenv.parents[0] / 'botvenv' / 'bin' / 'python').is_file():
            python_exc = [str(path_to_bot.parents[0] / 'botvenv' / 'bin' / 'python'), str(path_to_bot.parents[0] / 'run.py')]

    try:
        subprocess.run(python_exc, check=True)

        sys.exit()
    except PermissionError:
        pass
    except FileNotFoundError:
        pass
    except NameError:
        pass
    except Exception as e:
        print(e)

from __init__ import __modules__

if importlib.util.find_spec('alive_progress') is None:
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'alive-progress'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

from alive_progress import alive_it, styles

try:
    with open('configuration.json') as f:
        _config = json.load(f)
except FileNotFoundError:
    with open('configuration.json', 'w') as f:
        json.dump({}, f, ensure_ascii=False)

        _config = {}

if 'ModuFlex' in _config:
    if not _config['ModuFlex']['libs_is_dwnld']:
        for module in alive_it(__modules__, title='Проверка модулей', spinner=styles.SPINNERS['pulse'], theme='smooth'):
            if importlib.util.find_spec(module) is None:
                try:
                    subprocess.run([sys.executable, '-m', 'pip', 'install', module], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
                except subprocess.TimeoutExpired:
                    pass
else:
    for module in alive_it(__modules__, title='Проверка модулей', spinner=styles.SPINNERS['pulse'], theme='smooth'):
        if importlib.util.find_spec(module) is None:
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', module], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
            except subprocess.TimeoutExpired:
                pass

import asyncio
import gc
import traceback
from time import sleep

from pyrogram.client import Client
from sqlite3 import OperationalError

from loads import ScriptState
from main import main, api_id, api_hash, phone_number, password

from loads import Data

Data.experimental = experimental

max_retries = 10
retry_delay = 15
retries = 0

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

async def start_bot() -> int:
    global retries

    result = ScriptState.started

    app = Client(
            'db', api_id=api_id.group(1) if api_id is not None else None, api_hash=api_hash.group(1) if api_hash is not None else None,
            phone_number=phone_number.group(1) if phone_number is not None else None,
            password=password.group(1) if password is not None else None, max_concurrent_transmissions=20, workers=8
            )

    async with app:
        try:
            result = await main(app, retries)
        except KeyboardInterrupt:
            result = ScriptState.exit
        except Exception:
            traceback.print_exc()

            result = ScriptState.error
    
    del app
    gc.collect()

    return result

while retries < max_retries:
    try:
        result = asyncio.run(start_bot())

        if result == ScriptState.exit:
            sys.exit()
        elif result == ScriptState.restart:
            subprocess.run([sys.executable, *sys.argv])
            sys.exit()
    except KeyboardInterrupt:
        print('<3')
        break
    except (ConnectionError, TimeoutError) as e:
        print(e)
        print('Ошибка с соединением...')
        sleep(retry_delay)
        continue
    except OperationalError as e:
        print(e, '.Возможно скрипт работает где то ещё.')
        sleep(5)
        continue
    except Exception as e:
        print(e)
        continue

    retries += 1