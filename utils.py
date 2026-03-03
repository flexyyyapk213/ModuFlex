import shutil
import os
from typing import Optional, List, Tuple, Dict, Any
import re
import requests
from packaging import version
import json
import sys

def merge_directories(src: str, dst: str) -> None:
    """Умное слияние папок: копирует файлы из src в dst, сохраняя старые"""
    if not os.path.exists(dst):
        os.makedirs(dst)
    
    for item in os.listdir(src):
        src_path = os.path.join(src, item)
        dst_path = os.path.join(dst, item)
        
        if os.path.isdir(src_path):
            if not os.path.exists(dst_path):
                shutil.copytree(src_path, dst_path)
            else:
                merge_directories(src_path, dst_path)
        else:
            shutil.copy2(src_path, dst_path)

def __find_command__(_filters) -> Optional[List[str]]:
    if type(_filters).__name__ == 'CommandFilter':
        if isinstance(_filters.prefixes, list): return _filters.prefixes
        else: return list(_filters.prefixes)
    
    if _filters == None:
        return None

    if type(_filters.__dict__['other']).__name__ == 'CommandFilter':
        if isinstance(_filters.__dict__['other'].prefixes, list): return _filters.__dict__['other'].prefixes
        else: return list(_filters.__dict__['other'].prefixes)
    elif type(_filters.__dict__['base']).__name__ == 'CommandFilter':
        if isinstance(_filters.__dict__['base'].prefixes, list): return _filters.__dict__['base'].prefixes
        else: return list(_filters.__dict__['base'].prefixes)
    elif type(_filters.__dict__['base']).__name__ in ['AndFilter', 'OrFilter']:
        return __find_command__(_filters.__dict__['base'])
    else:
        return None

def __find_command_name__(_filters) -> Optional[str]:
    if type(_filters).__name__ == 'CommandFilter':
        return list(_filters.commands)[0]
    
    if _filters == None:
        return None

    if type(_filters.__dict__['other']).__name__ == 'CommandFilter':
        return list(_filters.__dict__['other'].commands)[0]
    elif type(_filters.__dict__['base']).__name__ == 'CommandFilter':
        return list(_filters.__dict__['base'].commands)[0]
    elif type(_filters.__dict__['base']).__name__ in ['AndFilter', 'OrFilter']:
        return __find_command_name__(_filters.__dict__['base'])
    else:
        return None

def check_update(version_now: str) -> Tuple:
    link = 'https://raw.githubusercontent.com/flexyyyapk213/ModuFlex/main/__init__.py'
    fresh_version = version.parse(re.search(r'__version__ = \'(.*?)\'', requests.get(link, headers={'User-Agent': 'Mozilla/5.0'}).text).group(1))
    _version_now = version.parse(version_now)

    return (fresh_version > _version_now, fresh_version)

def get_config_data() -> Dict[str, Any]:
    try:
        with open('config.ini', encoding='utf-8') as file:
            config = file.read()
    except FileNotFoundError:
        print('Файл конфигурации не был обнаружен.Создайте в корне папке файл config.ini и введите свои данные.(Подробнее в contribution.md)')
        sys.exit()
    
    send_msg_onstart_up = re.search(r'send_message\s*=\s*(true|false)', config)
    ask_to_downloads = re.search(r'ask_downloads\s*=\s(true|false)', config)
    one_download_libs = re.search(r'one_download_libs\s*=\s(true|false)', config)
    check_for_update = re.search(r'check_for_update\s*=\s(true|false)', config)
    timeout_download_lib = re.search(r'timeout_download_lib\s*=\s(\d+)', config)
    use_botvenv = re.search(r'use_botvenv\s*=\s*(true|false)', config)
    experimental = re.search(r'experimental\s*=\s*(true|false)', config)
    additional_accounts = re.search(r'accounts\s*=\s*(\[.*?\])', config, re.DOTALL)

    get_true_false = lambda value: {'true': True, 'false': False}[value]

    try:
        return {
            "send_message_on_startup": get_true_false(send_msg_onstart_up.group(1)) if send_msg_onstart_up is not None else False,
            "ask_to_downloads": get_true_false(ask_to_downloads.group(1)) if ask_to_downloads is not None else None,
            "one_download_libs": get_true_false(one_download_libs.group(1)) if one_download_libs is not None else None,
            "check_for_update": get_true_false(check_for_update.group(1)) if check_for_update is not None else None,
            "timeout_download_lib": int(timeout_download_lib.group(1)) if timeout_download_lib is not None else 120,
            "use_botvenv": get_true_false(use_botvenv.group(1)) if use_botvenv is not None else None,
            "experimental": get_true_false(experimental.group(1)) if experimental is not None else None,
            "additional_accounts": json.loads(additional_accounts.group(1)) if additional_accounts is not None else None
        }
    except Exception as e:
        print(e, '- Проверьте файл config.ini на наличии неправильного вида параметра.')

        sys.exit(1)