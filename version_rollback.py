"""
Файл для отката версии.
"""

import importlib.util
import subprocess
import sys
from __init__ import __version__
import os
import shutil
from pathlib import Path

script_dir = os.path.dirname(os.path.abspath(__file__))

import requests
import zipfile

def update_script(version: str):
    if not os.path.exists(os.path.join(script_dir, 'temp')):
        os.mkdir('temp')

    if 'v' in version:
        version = version.replace('v', '')

    if version == __version__:
        print('Версия написанная вами совпадает с текущей.')
        return

    link = f'https://github.com/flexyyyapk213/ModuFlex/archive/refs/tags/v{version}.zip'

    try:
        with open(f'temp/v{version.replace(".", "-")}.zip', 'wb') as f:
            with requests.get(link, stream=True) as r:
                if not r.ok:
                    print('Ошибка загрузки, возможно такой версии не существует.')
                    sys.exit(-1)
                for chunk in alive_it(r.iter_content(64), title='Загрузка отката', spinner=styles.SPINNERS['pulse'], theme='smooth'):
                    f.write(chunk)
    except (ConnectionError, TimeoutError):
        print('Возникли проблемы с интернет соединением, попробуйте позже.')
        return

    with zipfile.ZipFile(f'temp/v{version.replace(".", "-")}.zip', 'r') as zip_ref:
        zip_ref.extractall('temp')

    root_folders = os.listdir('temp')

    for file_name in root_folders:
        if os.path.isdir('temp/'+file_name):
            dir_name = file_name
            break

    for fl_name in os.listdir(f'temp/{dir_name}'):
        if fl_name == 'version_rollback.py':
            continue # На случай, если возникнут непредвиденные ошибки с откатом.Тогда можно откатиться снова и этот файл не заденет

        if os.path.exists(fl_name) and os.path.isfile(os.path.join('temp', dir_name, fl_name)):
            os.remove(fl_name)
            shutil.move(os.path.join('temp', dir_name, fl_name), '.')
        elif os.path.exists(fl_name) and os.path.isdir(os.path.join('temp', dir_name, fl_name)):
            shutil.copytree(os.path.join('temp', dir_name, fl_name), fl_name, dirs_exist_ok=True)
        else:
            shutil.move(os.path.join('temp', dir_name, fl_name), '.')

    os.remove(f'temp/v{version.replace(".", "-")}.zip')
    shutil.rmtree(f'temp/{dir_name}')

def install_venv():
    venv_path = Path(sys.executable)

    if 'botvenv' in venv_path.parts:
        return

    path_to_bot = Path(__file__)

    folders = [entry.name for entry in os.scandir(path_to_bot.parents[0]) if entry.is_dir()]

    if 'botvenv' not in folders:
        try:
            subprocess.run([sys.executable, '-m', 'venv', 'botvenv'], check=True)
        except Exception:
            print('\033[33mНе удалось создать botvenv.Дальнейшая работа будет производится без виртуального окружения.\033[0m')
            return

    path_to_botvenv = path_to_bot.parent / 'botvenv'

    if sys.platform == 'win32':
        python_exc = path_to_botvenv / 'Scripts' / 'python.exe'
    else:
        python_exc = path_to_botvenv / 'bin' / 'python'

    if not python_exc.exists():
        try:
            subprocess.run([sys.executable, '-m', 'venv', 'botvenv'], check=True)
        except Exception:
            print('\033[33mНе удалось создать botvenv.Дальнейшая работа будет производится без виртуального окружения.\033[0m')
            return

    try:
        # Run with botvenv
        subprocess.run([str(python_exc), sys.argv[0]], check=True)

        sys.exit()
    except (PermissionError, FileNotFoundError, NameError):
        print('\033[33mНе удалось создать botvenv.Дальнейшая работа будет производится без виртуального окружения.\033[0m')
    except Exception as e:
        print(e)

if __name__ == "__main__":
    # Go to the script root folder
    if os.getcwd() != script_dir:
        os.chdir(script_dir)

    install_venv()

    if importlib.util.find_spec('alive_progress') is None:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'alive-progress'])

    from alive_progress import alive_it, styles

    try:
        version = input("Введите версию(без префикса v): ")
    except KeyboardInterrupt:
        print('<3')
        sys.exit()

    update_script(version)

    print(f'Версия v{version} была успешно установлена.')