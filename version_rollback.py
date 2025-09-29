"""
Файл для отката версии.
"""

from enum import verify
import importlib.util
import subprocess
import sys

if importlib.util.find_spec('alive_progress') is None:
    subprocess.run(sys.executable, '-m', 'pip', 'install', 'alive-progress')

from alive_progress import alive_it, styles
import requests
import zipfile
from __init__ import __version__
import os
import shutil

version = input("Введите версию(без префикса v): ")

if 'v' in version:
    version.replace('v', '')

if version == __version__:
    print('Версия написанная вами совпадает с текущей.')
    sys.exit()

link = f'https://github.com/flexyyyapk213/ModuFlex/archive/refs/tags/v{version}.zip'

with open(f'temp/v{version.replace(".", "-")}.zip', 'wb') as f:
    with requests.get(link, stream=True) as r:
        for chunk in alive_it(r.iter_content(64), title='Загрузка отката', spinner=styles.SPINNERS['pulse'], theme='smooth'):
            f.write(chunk)

with zipfile.ZipFile(f'temp/v{version.replace(".", "-")}.zip', 'r') as zip_ref:
    zip_ref.extractall('temp')

dir_name = os.listdir('temp')

for file_name in dir_name:
    if os.is_dir('temp/'+file_name):
        dir_name = file_name
        break

script_dir = os.path.dirname(os.path.abspath(__file__))

for file_name in alive_it(os.listdir('temp/'+dir_name), title='Перенос файлов', spinner=styles.SPINNERS['pulse'], theme='smooth'):
    if file_name == 'botvenv':
        continue
    
    if file_name == 'config.ini':
        continue

    if file_name == 'plugins':
        shutil.copytree(f'temp/{dir_name}/{file_name}', os.path.join(script_dir, file_name), dirs_exist_ok=True)
        continue

    if os.path.isfile(f'temp/{dir_name}/{file_name}') and os.path.exists(f'{os.path.split(__file__)[0]}/{file_name}'):
        os.remove(f'{os.path.split(__file__)[0]}/{file_name}')
    
    if file_name == 'temp':
        continue
    
    shutil.move(f'temp/{dir_name}/{file_name}', f'{os.path.split(__file__)[0]}')

os.remove(f'temp/v{version.replace(".", "-")}.zip')
shutil.rmtree(f'temp/{dir_name}')

print(f'Версия v{version} была успешно установлена.')