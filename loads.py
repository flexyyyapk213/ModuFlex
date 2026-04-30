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
from utils import __find_command__, __find_command_name__
from alive_progress import alive_it, styles
import subprocess
import sys
from datetime import datetime
from quart import Blueprint
from wasmexecutor import WasmExecutor
import re
import warnings

logger = logging.getLogger(__name__)

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
    'download_library',
    'sandbox_exec',
    'ChatType',
    'route'
]

PACKAGE_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9_\-\.\=]+$')

class ScriptState(int, Enum):
    started = 0
    restart = 1
    error = -1
    exit = 2

class MappingConfig(dict):
    """
    Класс для управления настройками (конфигом) конкретного плагина.

    Изменения автоматически сохраняются в файл configuration.json.
    """
    def __init__(self, plugin_name: str, keys: List[str]):
        self.plugin_name = plugin_name
        self._keys = keys
        self._dict = Data.config[plugin_name]

        for key in keys:
            self._dict = self._dict[key]
    
    def __setitem__(self, key, value, /) -> None:
        self._dict[key] = value

        self._save()
    
    def __getitem__(self, key, /) -> "MappingConfig":
        if type(self._dict[key]) == dict:
            return MappingConfig(self.plugin_name, self._keys + [key])
        else:
            return self._dict[key]
    
    def __delitem__(self, key, /) -> None:
        del self._dict[key]

        self._save()
    
    def update(self, _dict: Dict) -> None:
        self._dict.update(_dict)

        self._save()
    
    def keys(self):
        return self._dict.keys()
    
    def values(self):
        return self._dict.values()
    
    def items(self):
        return self._dict.items()
    
    def clear(self):
        self._dict.clear()

        self._save()
    
    def popitem(self) -> Tuple:
        _item = self._dict.popitem()

        self._save()

        return _item
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._dict})"

    def __len__(self) -> int:
        return self._dict.__len__()
    
    def pop(self, key):
        _item = self._dict.pop(key)

        self._save()

        return _item

    def copy(self):
        return self._dict.copy()
    
    def get(self, key, default=None):
        return MappingConfig(self.plugin_name, key) if self._dict.get(key, default) != default else default
    
    def _save(self) -> None:
        with open('configuration.json', 'w', encoding='utf-8') as f:
            _cfg = json.dumps(Data.config, ensure_ascii=False)
            f.write(_cfg)
    
    def setdefault(self, _dict: Dict) -> None:
        """
        Гарантирует, что в конфиге есть все поля, что указаны в _dict.
        Если ключа нет (или тип не совпадает), он добавляется с соответствующим значением.

        Args:
            _dict (Dict): Cловарь "ключ: значение" с дефолтными параметрами.
        """
        if not self._dict:
            self.update(_dict)
        else:
            for key in _dict:
                if key not in _dict:
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
    timeout_download_lib: int = 120

    experimental = False

    # Крайне рекомендуется использовать эту песочницу, для выполнения любого кода, вместо exec/eval
    sandbox_executor = WasmExecutor()

    DEFAULT_MODUFLEX_CONFIG = {'dwnlds_libs_date': (datetime.now()).strftime('%Y-%m-%d'), 'libs_is_dwnld': False}

    try:
        with open('configuration.json', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        with open('configuration.json', 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False)
            config = {}
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
        Возвращает конфиг для указанного плагина, либо словарь всех конфигов.

        Если plugin_name не задан, возвращается копия всех конфигов для чтения.
        Если plugin_name соответствует вызывающему плагину, выдается управляющий MappingConfig для редактирования.

        Args:
            plugin_name (Optional[str]): Имя плагина(можно передать __file__ для удобства). Если не указано, будет возвращён весь конфиг (копия, нельзя изменять).
        Returns:
            Union[MappingConfig, dict]: Управляющий MappingConfig или копия конфига.
        """
        if 'plugins' in plugin_name:
            _path_parts = os.path.normpath(plugin_name).split(os.sep)
            plugin_name = _path_parts[_path_parts.index('plugins') + 1]
        
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
                return MappingConfig(plugin_name, [])
            else:
                return copy.deepcopy(Data.config[plugin_name])
        else:
            return copy.deepcopy(Data.config)
    
    @classmethod
    def __save_config__(cls):
        with open('configuration.json', 'w', encoding='utf-8') as f:
            _cfg = json.dumps(Data.config, ensure_ascii=False)
            f.write(_cfg)

class Module:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        class_filename = inspect.getfile(cls)
        path_parts = os.path.normpath(class_filename).split(os.sep)
        pack_name = path_parts[path_parts.index('plugins') + 1]

        _cls = cls()
        
        if id(_cls) not in Data.cache[pack_name]['classes']:
            Data.cache[pack_name]['classes'].update({id(_cls): {"class": _cls, "methods": {}}})
        
        if 'blueprint' not in Data.cache[pack_name]['routes']:
            bp = Blueprint(name=pack_name, import_name=pack_name, template_folder=os.path.join('plugins', pack_name, 'templates'), static_folder=os.path.join('plugins', pack_name, 'static'), url_prefix='/' + pack_name)

            Data.cache[pack_name]['routes'].update({"blueprint": bp, "funcs": {}, "methods": {}})

        for func in cls.__dict__.values():
            if hasattr(func, '_type'):
                if func._type == 'route':
                    Data.cache[pack_name]['routes']['methods'][id(func)] = {"method": func, "class_id": id(_cls), "parameters": {"rule": "/" + func.parameters[0], **func.parameters[1]}}
                else:
                    Data.cache[pack_name]['classes'][id(_cls)]['methods'].update({func.__name__: {"method": func, "filters": func.filters, "prefixes": func.prefixes, "command_name": func.command_name, "type": func._type}})

class chatType(str, Enum):
    """
    Перечисление возможных типов получателей чата.

    Атрибуты:
        DEFAULT: Обычный чат (по умолчанию)
        PRIVATE: Личные сообщения
        CHAT: Групповой чат
        CHANNEL: Канал
        ALL: Все чаты
    """
    DEFAULT = "default"
    PRIVATE = "private"
    CHAT = "chat"
    CHANNEL = "channel"
    ALL = "all"

class MainDescription:
    """
    Главное описание для плагина (используется в help/списке плагинов).

    Args:
        description (str): Описание плагина (строка).
    """
    def __init__(self, description: str) -> None:
        self.description = description

class FuncDescription:
    """
    Описание конкретной команды плагина.

    Args:
        `command` (str): Название (ключ) команды (пример: 'start').
        `description` (str): Описание (что делает команда).
        `hyphen` (str): Символ-разделитель между командой и описанием (обычно ' - ').
        `prefixes` (Union[Tuple, List], optional): Допустимые префиксы для команды (пример: ['/', '!']).
        `parameters` (Union[Tuple, List], optional): Параметры команды (позиционные или именованные).
        `parameters_style` (Union[Tuple, List, str]): Символы скобок параметров.
    """
    def __init__(
        self, 
        command: str, 
        description: str=None, 
        hyphen: str=' - ', 
        prefixes: Union[Tuple, List]=None, 
        parameters: Union[Tuple, List]=None,
        parameters_style: Union[Tuple, List, str]=None
    ) -> None:
        if parameters is None:
            parameters = []
        
        if prefixes is None:
            prefixes = ['/']
        
        if parameters_style is None:
            parameters_style = ('{', '}')
        
        if len(parameters_style) == 1:
            parameters_style = (parameters_style[0], parameters_style[0])
        
        if isinstance(parameters_style, str):
            parameters_style = (parameters_style, parameters_style)

        self.command = command
        self.description = description
        self.hyphen = hyphen
        self.prefixes = prefixes
        self.parameters = parameters
        self.parameters_style = parameters_style

class Description:
    """
    Описание плагина и всех его функций/команд.

    Args:
        main_description (MainDescription): Главное описание плагина.
        *args (FuncDescription): Описания его функций/команд.
    """
    def __init__(self, main_description: MainDescription, *args: FuncDescription):
        self.main_description = main_description

        self.funcs_description: Dict[str, Dict[str, FuncDescription]] = {}

        for func in args:
            self.funcs_description.update({func.command: func})

def func(_filters: filters, description: str=None) -> Callable:
    """
    Декоратор для регистрации обработчика сообщений (команды).

    Args:
        _filters (filters): Фильтры pyrogram для отбора сообщений.
        description (str): Описание команды.
    Returns:
        Callable: Зарегистрированная функция-обработчик.
    """
    def reg(_func: Callable) -> None:
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
                    Data.description[pack_name].funcs_description[command_name].description = description
                else:
                    Data.description[pack_name].funcs_description.update({command_name: FuncDescription(command_name, prefixes=prefixes, description=description)})
        else:
            Data.description.update({pack_name: Description(MainDescription("Описание отсутствует."), FuncDescription(command_name, prefixes=prefixes, description=description))})
        
        if caller_frame.f_code.co_name != '<module>':
            _func._type = 'default'
            _func.prefixes = prefixes
            _func.command_name = command_name
            _func.pack_name = pack_name
            _func.filters = _filters

            del frame
            return _func
        else:
            Data.cache[pack_name]['funcs'].update({id(_func): {"func": _func, "filters": _filters, "prefixes": prefixes, "command_name": command_name, "type": "default"}})
        
        del frame
    return reg

def private_func(_filters: filters=None, description: str='Описание отсутствует.') -> Callable:
    """
    Декоратор для регистрации обработчика сообщений в личных сообщениях.

    Внимание: Использование не рекомендуется. Старая система, лучше использовать универсальный декоратор func.

    Args:
        _filters (filters, optional): Фильтры pyrogram (или None).
        description (str): Описание команды.
    Returns:
        Callable: Зарегистрированная функция-обработчик.
    """
    warnings.warn('The "private_func" function is deprecated, use "func" instead.', DeprecationWarning, 2)
    def reg(_func: Callable) -> None:
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
                    Data.description[pack_name].funcs_description[command_name].description = description
                else:
                    Data.description[pack_name].funcs_description.update({command_name: FuncDescription(command_name, prefixes=prefixes, description=description)})
        else:
            Data.description.update({pack_name: Description(MainDescription("Описание отсутствует."), FuncDescription(command_name, prefixes=prefixes, description=description))})
        
        if caller_frame.f_code.co_name != '<module>':
            _func._type = 'private'
            _func.prefixes = prefixes
            _func.command_name = command_name
            _func.pack_name = pack_name
            _func.filters = _filters

            del frame
            return _func
        else:
            Data.cache[pack_name]['funcs'].update({id(_func): {"func": _func, "filters": _filters, "prefixes": prefixes, "command_name": command_name, "type": "default"}})
        
        del frame
    return reg

def chat_func(_filters: filters=None, description: str='Описание отсутствует.') -> Callable:
    """
    Декоратор для регистрации обработчика сообщений из чата (не ЛС).

    Внимание: Использование не рекомендуется. Старая система, лучше использовать универсальный декоратор func.

    Args:
        _filters (filters, optional): Фильтры pyrogram (или None).
        description (str): Описание команды.
    Returns:
        Callable: Зарегистрированная функция-обработчик.
    """
    warnings.warn('The "chat_func" function is deprecated, use "func" instead.', DeprecationWarning, 2)
    def reg(_func: Callable) -> None:
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
                    Data.description[pack_name].funcs_description[command_name].description = description
                else:
                    Data.description[pack_name].funcs_description.update({command_name: FuncDescription(command_name, prefixes=prefixes, description=description)})
        else:
            Data.description.update({pack_name: Description(MainDescription("Описание отсутствует."), FuncDescription(command_name, prefixes=prefixes, description=description))})
        
        if caller_frame.f_code.co_name != '<module>':
            _func._type = 'chat'
            _func.prefixes = prefixes
            _func.command_name = command_name
            _func.pack_name = pack_name
            _func.filters = _filters

            del frame
            return _func
        else:
            Data.cache[pack_name]['funcs'].update({id(_func): {"func": _func, "filters": _filters, "prefixes": prefixes, "command_name": command_name, "type": "default"}})
        
        del frame
    return reg

def channel_func(_filters: filters=None, description: str='Описание отсутствует.') -> Callable:
    """
    Декоратор для регистрации обработчика сообщений из канала.

    Внимание: Использование не рекомендуется. Старая система, лучше использовать универсальный декоратор func.

    Args:
        _filters (filters, optional): Фильтры pyrogram (или None).
        description (str): Описание команды.
    Returns:
        Callable: Зарегистрированная функция-обработчик.
    """
    warnings.warn('The "channel_func" function is deprecated, use "func" instead.', DeprecationWarning, 2)
    def reg(_func: Callable) -> None:
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
                    Data.description[pack_name].funcs_description[command_name].description = description
                else:
                    Data.description[pack_name].funcs_description.update({command_name: FuncDescription(command_name, prefixes=prefixes, description=description)})
        else:
            Data.description.update({pack_name: Description(MainDescription("Описание отсутствует."), FuncDescription(command_name, prefixes=prefixes, description=description))})
        
        if caller_frame.f_code.co_name != '<module>':
            _func._type = 'channel'
            _func.prefixes = prefixes
            _func.command_name = command_name
            _func.pack_name = pack_name
            _func.filters = _filters

            del frame
            return _func
        else:
            Data.cache[pack_name]['funcs'].update({id(_func): {"func": _func, "filters": _filters, "prefixes": prefixes, "command_name": command_name, "type": "default"}})
        
        del frame
    return reg

def all_func(_filters: filters=None, description: str='Описание отсутствует.') -> Callable:
    """
    Декоратор для регистрации обработчика сообщений для всех чатов/типов.

    Внимание: Использование не рекомендуется. Старая система, лучше использовать универсальный декоратор func.

    Args:
        _filters (filters, optional): Фильтры pyrogram (или None).
        description (str): Описание команды.
    Returns:
        Callable: Зарегистрированная функция-обработчик.
    """
    warnings.warn('The "all_func" function is deprecated, use "func" instead.', DeprecationWarning, 2)
    def reg(_func: Callable) -> None:
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
                    Data.description[pack_name].funcs_description[command_name].description = description
                else:
                    Data.description[pack_name].funcs_description.update({command_name: FuncDescription(command_name, prefixes=prefixes, description=description)})
        else:
            Data.description.update({pack_name: Description(MainDescription("Описание отсутствует."), FuncDescription(command_name, prefixes=prefixes, description=description))})

        if caller_frame.f_code.co_name != '<module>':
            _func._type = 'all'
            _func.prefixes = prefixes
            _func.command_name = command_name
            _func.pack_name = pack_name
            _func.filters = _filters

            del frame
            return _func
        else:
            Data.cache[pack_name]['funcs'].update({id(_func): {"func": _func, "filters": _filters, "prefixes": prefixes, "command_name": command_name, "type": "default"}})
        
        del frame
    return reg

def route(rule: str, **options) -> Callable:
    """
    Декоратор для регистрации HTTP-роута (маршрута web-интерфейса плагина).

    Args:
        rule (str): URL-маршрут (например: '/settings').
        **options: Дополнительные параметры для Blueprint.route.
    Returns:
        Callable: Зарегистрированная функция-обработчик.
    """
    def reg(_func: Callable) -> None:
        frame = inspect.currentframe()
        caller_frame = frame.f_back
        caller_filename = caller_frame.f_code.co_filename
        
        path_parts = os.path.normpath(caller_filename).split(os.sep)
        pack_name = path_parts[path_parts.index('plugins') + 1]

        if caller_frame.f_code.co_name != '<module>':
            _func._type = 'route'
            _func.pack_name = pack_name
            _func.parameters = (rule, options)

            del frame
            return _func
        else:
            if 'blueprint' not in Data.cache[pack_name]['routes']:
                bp = Blueprint(name=pack_name, import_name=pack_name, template_folder=os.path.join('plugins', pack_name, 'templates'), static_folder=os.path.join('plugins', pack_name, 'static'), url_prefix='/' + pack_name)

                Data.cache[pack_name]['routes'].update({"blueprint": bp, "funcs": {}, "methods": {}})
            
            Data.cache[pack_name]['routes']['funcs'][id(_func)] = {"func": _func, "parameters": {"rule": rule, **options}}
        
    return reg

def set_modules(modules: List) -> None:
    """
    Указывает внешние (сторонние) библиотеки для установки через pip, если требуется.

    Крайне рекомендуется использовать только для особых случаев (есть лучший способ - смотри contribution.md).
    Вызывать перед импортом этих библиотек.

    Args:
        modules (List[str]): Список имён сторонних библиотек (строки).
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
            if not PACKAGE_NAME_PATTERN.match(_lib):
                logger.error(f'Не допустимая библиотека {_lib}')
                continue
            
            user_input = input(f"Устанавливать библиотеку {_lib} ([A]ll, [Y]es, [N]o): ")
            
            if user_input.lower() == 'a':
                _libs.extend(libs)
                break
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

def sandbox_exec(code: str, _globals: Optional[Dict]=None, _locals: Optional[Dict]=None):
    """
    Выполняет указанный Python-код в изолированной среде (песочнице WebAssembly).

    Args:
        `code` (str): Строка с исходным кодом Python для выполнения.
        `_globals` (Optional[Dict]): Глобальные переменные для среды выполнения.
        `_locals` (Optional[Dict]): Локальные переменные для среды выполнения.

    Returns:
        Result: Результат выполнения кода, включая вывод, ошибки и дополнительные параметры.
    """
    return Data.sandbox_executor.run_code(code, _globals, _locals)