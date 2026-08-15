import inspect
import logging
import os
import traceback
import json
from packaging import version
from packaging.specifiers import SpecifierSet
from threading import Thread
import importlib

from __init__ import __version__
from loads import Data, Description, download_library

from watchdog.events import FileSystemEventHandler, DirModifiedEvent, FileModifiedEvent
from pyrogram import Client

logger = logging.getLogger(__name__)

class HotReload(FileSystemEventHandler):
    def __init__(self, client: Client) -> None:
        self.client = client

    def on_any_event(self, event) -> None:
        if event.is_directory:
            return

        if event.event_type in ('modified', 'created', 'moved') and not event.src_path.endswith(".pyc"):
            parts_path = os.path.normpath(event.src_path).split(os.sep)

            pack_name: str = parts_path[parts_path.index("plugins") + 1]
            Data.__clear_plugin__(pack_name)
            importlib.reload(importlib.import_module("plugins." + pack_name))
            handle_plugin(pack_name, self.client)


def handling_plugins():
    folders = os.listdir('plugins')

    for folder in folders:
        try:
            if ' ' in folder:
                continue
            
            init_file = os.path.join('plugins', folder, '__init__.py')
            if os.path.exists(init_file):
                Data.cache.update({
                    folder: {
                        "funcs": {},
                        "classes": {},
                        "routes": {},
                        "initialization": None
                    }
                                })
                
                if os.path.exists(os.path.join('plugins', folder, '__modules__.txt')):
                    if not Data.config['ModuFlex'].get('libs_is_dwnld', False) and Data.one_download_libs or not Data.one_download_libs:
                        with open(os.path.join('plugins', folder, '__modules__.txt'), encoding='utf-8') as modules:
                            download_library(modules.readlines())

                md = __import__('plugins.' + folder)

                if hasattr(dict(md.__dict__.items())[folder], '__description__'):
                    if not isinstance(dict(md.__dict__.items())[folder].__description__, Description):
                        print(f'\033[41mОшибка в плагине {folder}: Описание не корректное\033[0m')
                        Data.failed_modules += 1
                        continue
                    
                    update_command_information(dict(md.__dict__.items())[folder].__description__, folder)
                
                if hasattr(dict(md.__dict__.items())[folder], 'initialization'):
                    if not inspect.isfunction(dict(md.__dict__.items())[folder].initialization):
                        print(f'\033[41mОшибка в плагине {folder}: инициализация не корректная\033[0m')
                        Data.failed_modules += 1
                        continue
                    
                    Data.cache[folder]["initialization"] = dict(md.__dict__.items())[folder].initialization

                if os.path.exists(os.path.join('plugins', folder, 'manifest.json')):
                    with open(os.path.join('plugins', folder, 'manifest.json'), encoding='utf-8') as f:
                        manifest = json.load(f)
                    
                    spec = SpecifierSet(manifest['mf_version'])
                    current = version.parse(__version__)

                    if not spec.contains(current):
                        Data.cache.pop(folder)
                        try:
                            Data.description.pop(folder)
                        except KeyError:
                            pass
        except Exception:
            traceback.print_exc()
            logger.warning(traceback.format_exc())
            Data.failed_modules += 1

def handle_plugin(pack_name: str, client: Client):
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
        
        md = __import__('plugins.' + pack_name)

        if hasattr(dict(md.__dict__.items())[pack_name], '__description__'):
            if not isinstance(dict(md.__dict__.items())[pack_name].__description__, Description):
                print(f'\033[41mОшибка в плагине {pack_name}: Описание не корректное\033[0m')
                Data.failed_modules += 1
                return
            
            update_command_information(dict(md.__dict__.items())[pack_name].__description__, pack_name)
        
        if hasattr(dict(md.__dict__.items())[pack_name], 'initialization'):
            if not inspect.isfunction(dict(md.__dict__.items())[pack_name].initialization):
                print(f'\033[41mОшибка в плагине {pack_name}: инициализация не корректная\033[0m')
                Data.failed_modules += 1
                return
            
            Data.cache[pack_name]["initialization"] = dict(md.__dict__.items())[pack_name].initialization
        
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

        if Data.cache.get(pack_name, {}).get("initialization", None) is not None:
            Thread(target=Data.cache[pack_name]["initialization"], args=(client,)).start()
    except Exception:
        traceback.print_exc()
        logger.warning(traceback.format_exc())
        Data.failed_modules += 1

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