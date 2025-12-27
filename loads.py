from typing import Callable, Union, Optional, Any, Dict, List, Tuple
import inspect
from pyrogram import filters
import os
import importlib.util
import logging
import traceback
import json
import copy
from enum import Enum
from utils import __find_command__, __find_conflict__, __find_command_name__
from alive_progress import alive_it, styles
import subprocess
import sys
from datetime import datetime

logging.basicConfig(filename='script.log', level=logging.WARN)

__all__ = [
    'Data',
    'func',
    'private_func',
    'chat_func',
    'channel_func',
    'all_func',
    'set_modules',
    'MainDescription',
    'FuncDescription',
    'Description',
    'handleMethods',
    'download_library'
]

class ScriptState(int, Enum):
    started = 0
    restart = 1
    error = -1
    exit = 2

class MappingConfig(dict):
    def __init__(self, plugin_name: str):
        self.plugin_name = plugin_name

    def __setitem__(self, key, value):
        Data.config[self.plugin_name][key] = value

        self._save()

    def __getitem__(self, key):
        return Data.config[self.plugin_name][key]

    def __delitem__(self, key):
        del Data.config[self.plugin_name][key]

        self._save()

    def update(self, _dict: Dict):
        Data.config[self.plugin_name].update(_dict)

        self._save()

    def keys(self):
        return Data.config[self.plugin_name].keys()

    def values(self):
        return Data.config[self.plugin_name].values()

    def items(self):
        return Data.config[self.plugin_name].items()

    def _save(self):
        with open('configuration.json', 'w', encoding='utf-8') as f:
            json.dump(Data.config, f, ensure_ascii=False)

    def clear(self):
        Data.config[self.plugin_name].clear()

        self._save()

    def popitem(self):
        _item = Data.config[self.plugin_name].popitem()

        self._save()

        return _item

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({Data.config[self.plugin_name]})"

    def __len__(self) -> int:
        return Data.config[self.plugin_name].__len__()

    def pop(self, key):
        Data.config[self.plugin_name].pop(key)

        self._save()

    def copy(self):
        return Data.config[self.plugin_name].copy()
    
    def get(self, key, default=None):
        return Data.config[self.plugin_name].get(key, default)

    def setdefault(self, _dict: Dict) -> None:
        """
        Устанавливает по умолчанию заданый словарь, если сам конфиг плагина пуст.
        Если же конфиг плагина не пуст, то функция ищет не достающие ключи и вставляет.
        Удобно для тех, кто добавляет новые ключи и не хочет писать для такого случая код.
        """
        if not Data.config[self.plugin_name]:
            self.update(_dict)
        else:
            for key in _dict:
                if key not in Data.config[self.plugin_name] or type(_dict[key]) != type(Data.config[self.plugin_name].get(key, '')):
                    self.update({key: copy.deepcopy(_dict[key])})

class Data:
    """
    Центр хранения модулей.
    """

    cache = {

    }

    description = {}

    modules = []

    initializations = []

    config = {}

    count_commands: Dict[str, List[str]] = {}

    ask_downloads = False

    skip_downloads = False

    one_download_libs = True

    failed_modules: int = 0

    check_for_update = True

    # Таймаут скачивания библиотеки
    timeout_download_lib: int = 60

    DEFAULT_MODUFLEX_CONFIG = {'dwnlds_libs_date': (datetime.now()).strftime('%Y-%m-%d'), 'libs_is_dwnld': False}

    try:
        with open('configuration.json', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        with open('configuration.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False)
    except Exception as e:
        logging.error(traceback.format_exc())
        print(e)

    @classmethod
    def get_name_plugins(cls) -> List[str]:
        """
        Возвращает список плагинов.
        """
        return list(Data.description.keys())
    
    @classmethod
    def get_config(cls, plugin_name: Optional[str]=None) -> Union[MappingConfig, Dict]:
        """
        Возвращает словарь настроек.
        Если оставить `plugin_name` None, вернёт конфиги плагинов.
        Если плагин попытается изменить данные чужого плагина, то у него этого не получиться.

        Args:
            plugin_name (Optional[str]=None): Имя плагина
        Returns:
            Union[
            Mapping[str, Any] - словарь нельзя изменить,
            dict - это не ваш конфиг, но он доступен в качестве просмотра
            ]
        """
        if plugin_name is not None:
            if plugin_name not in Data.config:
                Data.config.update({plugin_name: {}})

                with open('configuration.json', 'w', encoding='utf-8') as f:
                    json.dump(Data.config, f, ensure_ascii=False)
            
            frame = inspect.currentframe()
            caller_frame = frame.f_back
            caller_filename = caller_frame.f_code.co_filename
            
            path_parts = os.path.normpath(caller_filename).split(os.sep)
            pack_name = path_parts[path_parts.index('plugins') + 1]
            
            if plugin_name == pack_name:
                return MappingConfig(plugin_name)
            else:
                return copy.deepcopy(Data.config[plugin_name])
        else:
            return copy.deepcopy(Data.config)
    
    @classmethod
    def __save_config__(cls):
        with open('configuration.json', 'w', encoding='utf-8') as f:
            json.dump(Data.config, f, ensure_ascii=False)

class chatType(str, Enum):
    DEFAULT = "default"
    PRIVATE = "private"
    CHAT = "chat"
    CHANNEL = "channel"
    ALL = "all"

class MainDescription:
    """
    Класс для описания плагина.
    """
    def __init__(self, description: str) -> None:
        self.description = description

class FuncDescription:
    """
    Класс для описания функций плагина.
    """
    def __init__(self, command: str, description: str="Описание отсутствует.", hyphen: str=' - ', prefixes: Union[Tuple, List]=None, parameters: Union[Tuple, List]=[]) -> None:
        """
        Args:
            command (str): Команда.
            description (str): Описание(Опционально).
            hyphen (str): Символ заменяющий дефис(Опционально).
            prefixes (Union[tuple, list]): Префиксы к командам(Опционально).
            parameters (Union[tuple, list]): Параметры к командам(Опционально).
        Return:
            None
        """
        self.command = command
        self.description = description
        self.hyphen = hyphen
        self.prefixes = prefixes
        self.parameters = parameters

class Description:
    """
    Класс для описания плагина и его функций.
    """
    def __init__(self, main_description: MainDescription, *args: FuncDescription):
        self.main_description = main_description

        self.funcs_description: Dict[str, Dict[str, FuncDescription]] = {}

        for func in args:
            self.funcs_description.update({func.command: func})

class PluginInfo:
    """
    Класс информации плагина.
    """
    def __init__(self):
        ...

def func(_filters: filters) -> Callable:
    """
    Декоратор для обработки сообщений.
    :param _filters: фильтры pyrogram
    :return: Callable
    """
    def reg(_func: Callable) -> None:
        if not inspect.isfunction(_func):
            raise ValueError('Is not a function')
        
        frame = inspect.currentframe()
        caller_frame = frame.f_back
        caller_filename = caller_frame.f_code.co_filename
        
        path_parts = os.path.normpath(caller_filename).split(os.sep)
        pack_name = path_parts[path_parts.index('plugins') + 1]

        try:
            prefixes = __find_command__(_filters)
        except KeyError:
            prefixes = None
        
        try:
            command_name = __find_command_name__(_filters)
        except KeyError:
            command_name = None
        
        if pack_name in Data.description:
            if command_name is not None and prefixes is not None:
                if command_name in Data.description[pack_name].funcs_description:
                    Data.description[pack_name].funcs_description[command_name].prefixes = prefixes
                else:
                    Data.description[pack_name].funcs_description.update({command_name: FuncDescription(command_name, prefixes=prefixes)})
        else:
            Data.description.update({pack_name: Description(MainDescription("Описание отсутствует."), FuncDescription(command_name, prefixes=prefixes))})

        Data.cache[pack_name]['funcs'].update({_func.__name__: {"func": _func, "filters": _filters, "prefixes": prefixes, "command_name": command_name, "type": "default"}})
    return reg

def private_func(_filters: filters=None) -> Callable:
    """
    Декоратор для обработки сообщений в личном чате.
    Не имеет параметров.
    :return: Callable

    !Не рекомендуется к использованию.
    """
    def reg(_func: Callable) -> None:
        if not inspect.isfunction(func):
            raise ValueError('Is not a function')

        frame = inspect.currentframe()
        caller_frame = frame.f_back
        caller_filename = caller_frame.f_code.co_filename

        path_parts = os.path.normpath(caller_filename).split(os.sep)
        pack_name = path_parts[path_parts.index('plugins') + 1]

        try:
            prefixes = __find_command__(_filters)
        except KeyError:
            prefixes = None
        
        try:
            command_name = __find_command_name__(_filters)
        except KeyError:
            command_name = None
        
        if pack_name in Data.description:
            if command_name is not None and prefixes is not None:
                if command_name in Data.description[pack_name]:
                    Data.description[pack_name].funcs_description[command_name].prefixes = prefixes

        Data.cache[pack_name]['funcs'].update({_func.__name__: {"func": _func, "filters": _filters, "prefixes": prefixes, "command_name": command_name, "type": "private"}})
    return reg

def chat_func(_filters: filters=None) -> Callable:
    """
    Декоратор для обработки сообщений в чате.
    Не имеет параметров.
    :return: Callable

    !Не рекомендуется к использованию.
    """
    def reg(_func: Callable) -> None:
        if not inspect.isfunction(func):
            raise ValueError('Is not a function')

        frame = inspect.currentframe()
        caller_frame = frame.f_back
        caller_filename = caller_frame.f_code.co_filename

        path_parts = os.path.normpath(caller_filename).split(os.sep)
        pack_name = path_parts[path_parts.index('plugins') + 1]

        try:
            prefixes = __find_command__(_filters)
        except KeyError:
            prefixes = None
        
        try:
            command_name = __find_command_name__(_filters)
        except KeyError:
            command_name = None
        
        if pack_name in Data.description:
            if command_name is not None and prefixes is not None:
                if command_name in Data.description[pack_name]:
                    Data.description[pack_name].funcs_description[command_name].prefixes = prefixes

        Data.cache[pack_name]['funcs'].update({_func.__name__: {"func": _func, "filters": _filters, "prefixes": prefixes, "command_name": command_name, "type": "chat"}})
    return reg

def channel_func(_filters: filters=None) -> Callable:
    """
    Декоратор для обработки сообщений в канале чате.
    Не имеет параметров.
    :return: Callable

    !Не рекомендуется к использованию.
    """
    def reg(_func: Callable) -> None:
        if not inspect.isfunction(func):
            raise ValueError('Is not a function')

        frame = inspect.currentframe()
        caller_frame = frame.f_back
        caller_filename = caller_frame.f_code.co_filename

        path_parts = os.path.normpath(caller_filename).split(os.sep)
        pack_name = path_parts[path_parts.index('plugins') + 1]

        try:
            prefixes = __find_command__(_filters)
        except KeyError:
            prefixes = None
        
        try:
            command_name = __find_command_name__(_filters)
        except KeyError:
            command_name = None
        
        if pack_name in Data.description:
            if command_name is not None and prefixes is not None:
                if command_name in Data.description[pack_name]:
                    Data.description[pack_name].funcs_description[command_name].prefixes = prefixes

        Data.cache[pack_name]['funcs'].update({_func.__name__: {"func": _func, "filters": _filters, "prefixes": prefixes, "command_name": command_name, "type": "channel"}})
    return reg

def all_func(_filters: filters=None) -> Callable:
    """
    Декоратор для обработки сообщений по всему чату.
    Не имеет параметров.
    :return: Callable

    !Не рекомендуется к использованию.
    """
    def reg(_func: Callable) -> None:
        if not inspect.isfunction(func):
            raise ValueError('Is not a function')

        frame = inspect.currentframe()
        caller_frame = frame.f_back
        caller_filename = caller_frame.f_code.co_filename

        path_parts = os.path.normpath(caller_filename).split(os.sep)
        pack_name = path_parts[path_parts.index('plugins') + 1]

        try:
            prefixes = __find_command__(_filters)
        except KeyError:
            prefixes = None
        
        try:
            command_name = __find_command_name__(_filters)
        except KeyError:
            command_name = None
        
        if pack_name in Data.description:
            if command_name is not None and prefixes is not None:
                if command_name in Data.description[pack_name]:
                    Data.description[pack_name].funcs_description[command_name].prefixes = prefixes

        Data.cache[pack_name]['funcs'].update({_func.__name__: {"func": _func, "filters": _filters, "prefixes": prefixes, "command_name": command_name, "type": "all"}})
    return reg

def set_modules(modules: List) -> None:
    """
    Функция для указания сторонних библиотек.
    Вызывать перед импортами сторонних библиотек.
    :param modules: список сторонних библиотек
    :return: None
    """

    for indx, module in enumerate(modules.copy()):
        if module in Data.modules or importlib.util.find_spec(module) is not None:
            try:
                modules.pop(indx)
            except IndexError:
                pass

    download_library(modules)

    Data.modules.extend(modules)

def download_library(libs: List[str]) -> None:
    dwnld_all: bool = Data.ask_downloads

    if Data.skip_downloads:
        return
    
    _libs = []

    if not dwnld_all:
        for _lib in libs:
            user_input = input(f"Устанавливать библиотеку {_lib} ([A]ll, [Y]es, [N]o): ")
            
            if user_input.lower() == 'a':
                _libs.extend(libs)
            elif user_input.lower() == 'y':
                _libs.append(_lib)
            else:
                continue
    else:
        _libs.extend(libs)

    for _library in alive_it(_libs, title='Установка доп. модулей', spinner=styles.SPINNERS['pulse'], theme='smooth'):
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', _library], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=Data.timeout_download_lib)
        except subprocess.TimeoutExpired:
            print(f'\033[41 Превышен лимит ожидания скачивания библиотеки {_library}. Возможно библиотека не поддерживается вашим устройством или плохое интернет соединение. \033[0m')