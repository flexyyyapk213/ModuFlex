import inspect
import logging
import os
import traceback
import json
from packaging import version
from packaging.specifiers import SpecifierSet
from threading import Thread
import importlib
from typing import List, Optional

from __init__ import __version__
from loads import Data, Description, download_library

from watchdog.events import FileSystemEventHandler
from pyrogram.client import Client

logger = logging.getLogger(__name__)

class HotReload(FileSystemEventHandler):
    def __init__(self, client: Client) -> None:
        self.client = client

    def on_any_event(self, event) -> None:
        if event.is_directory:
            return

        if event.event_type in ('modified', 'created', 'moved') and not event.src_path.endswith(".pyc"):
            parts_path: List[str] = os.path.normpath(str(event.src_path)).split(os.sep)

            pack_name: str = parts_path[parts_path.index("plugins") + 1]
            Data.__clear_plugin__(pack_name)
            importlib.reload(importlib.import_module("plugins." + pack_name))
            handle_plugin(pack_name, self.client)

def handle_plugin(pack_name: str, client: Optional[Client]=None):
    try:
        Data.cache.update({
            pack_name: {
                "funcs": {},
                "classes": {},
                "routes": {},
                "initialization": None
            }
                        })
        
        if os.path.exists(os.path.join('plugins', pack_name, '__modules__.txt')):
            with open(os.path.join('plugins', pack_name, '__modules__.txt'), encoding='utf-8') as modules:
                download_library(modules.readlines())
        
        md = importlib.import_module('plugins.' + pack_name)

        if hasattr(md, '__description__'):
            if not isinstance(md.__description__, Description):
                print(f'\033[41mОшибка в плагине {pack_name}: Описание не корректное\033[0m')
                Data.failed_modules += 1
                return
            
            update_command_information(md.__description__, pack_name)
        
        if hasattr(md, 'initialization'):
            if not inspect.isfunction(md.initialization):
                print(f'\033[41mОшибка в плагине {pack_name}: инициализация не корректная\033[0m')
                Data.failed_modules += 1
                return
            
            Data.cache[pack_name]["initialization"] = md.initialization
        
        if os.path.exists(os.path.join('plugins', pack_name, 'manifest.json')):
            with open(os.path.join('plugins', pack_name, 'manifest.json'), encoding='utf-8') as f:
                manifest = json.load(f)
            
            spec = SpecifierSet(manifest['mf_version'])
            current = version.parse(__version__)

            if not spec.contains(current):
                Data.cache.pop(pack_name)
                try:
                    Data.description.pop(pack_name)
                except KeyError:
                    pass

        if Data.cache.get(pack_name, {}).get("initialization", None) is not None and client is not None:
            Thread(target=Data.cache[pack_name]["initialization"], args=(client,)).start()
    except Exception:
        traceback.print_exc()
        logger.warning(traceback.format_exc())
        Data.failed_modules += 1

def handling_plugins():
    folders = os.listdir('plugins')

    for folder in folders:
        if ' ' in folder:
            continue

        handle_plugin(folder)

def update_command_information(description: Description, plugin_name: str):
    if plugin_name not in Data.description:
        Data.description.update({plugin_name: description})
        return
    
    Data.description[plugin_name].main_description.description = description.main_description.description

    for command in description.funcs_description.values():
        if command.command in Data.description[plugin_name].funcs_description:
            if command.description is not None: Data.description[plugin_name].funcs_description[command.command].description = command.description
            Data.description[plugin_name].funcs_description[command.command].hyphen = command.hyphen
            Data.description[plugin_name].funcs_description[command.command].parameters = command.parameters
        else:
            Data.description[plugin_name].funcs_description.update({command.command: command})