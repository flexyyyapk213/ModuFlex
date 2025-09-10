import importlib.util
import subprocess
import sys
from pathlib import Path
import os

venv_path = Path(sys.executable)

# Run with botvenv
if list(venv_path.parts)[-3] != 'botvenv':
    path_to_bot = Path(__file__)

    folders = [entry.name for entry in os.scandir(path_to_bot.parents[0]) if entry.is_dir()]

    if 'botvenv' not in folders:
        if importlib.util.find_spec('venv') is None:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'venv'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        subprocess.run([sys.executable, '-m', 'venv', 'botvenv'])

    subprocess.run([str(path_to_bot.parents[0] / 'botvenv' / 'Scripts' / 'python.exe'), str(path_to_bot.parents[0] / 'run.py')])
    sys.exit()

from __init__ import __modules__

if importlib.util.find_spec('alive_progress') is None:
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'alive-progress'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

from alive_progress import alive_it, styles

for module in alive_it(__modules__, title='Проверка модулей', spinner=styles.SPINNERS['pulse'], theme='smooth'):
    if importlib.util.find_spec(module) is None:
        subprocess.run([sys.executable, '-m', 'pip', 'install', module], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

import asyncio
from time import sleep
import subprocess
from pyrogram.client import Client
from sqlite3 import OperationalError
from main import main, api_id, api_hash, phone_number, password
import gc

max_retries = 10
retry_delay = 15
retries = 0

async def start_bot():
    global retries

    app = Client(
            'db', api_id=api_id.group(1) if api_id is not None else None, api_hash=api_hash.group(1) if api_hash is not None else None,
            phone_number=phone_number.group(1) if phone_number is not None else None,
            password=password.group(1) if password is not None else None, max_concurrent_transmissions=20, workers=8
            )

    async with app:
        await main(app, retries)
    
    del app
    gc.collect()

while retries < max_retries:
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        asyncio.run(start_bot())

        subprocess.run([sys.executable] + sys.argv)
        sys.exit()
    except KeyboardInterrupt:
        print('<3')
        break

    except (ConnectionError, TimeoutError) as e:
        print(e)
        print('Ошибка с соединением...')
        sleep(retry_delay)
    except OperationalError as e:
        sleep(5)
    except Exception as e:
        print(e)

    retries += 1
