import inspect
import logging
import os
import traceback
import json

from __init__ import __version__
from loads import Data, Description, download_library
from packaging import version
from packaging.specifiers import SpecifierSet

logger = logging.getLogger(__name__)

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
                        "routes": {}
                    }
                                })
                
                if os.path.exists(os.path.join('plugins', folder, '__modules__.txt')):
                    if not Data.config['ModuFlex'].get('libs_is_dwnld', False) and Data.one_download_libs or not Data.one_download_libs:
                        with open(os.path.join('plugins', folder, '__modules__.txt')) as modules:
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
                    
                    Data.initializations.append(dict(md.__dict__.items())[folder].initialization)

                if os.path.exists(os.path.join('plugins', folder, 'manifest.json')):
                    with open(os.path.join('plugins', folder, 'manifest.json'), encoding='utf-8') as f:
                        manifest = json.load(f)
                    
                    spec = SpecifierSet(manifest['mf_version'])
                    current = version.parse(__version__)

                    if not spec.contains(current):
                        Data.cache.pop(folder)
                        try:
                            Data.description.pop(folder)
                            Data.initializations.pop()
                        except IndexError:
                            pass
        except Exception:
            traceback.print_exc()
            logger.warning(traceback.format_exc())
            Data.failed_modules += 1

def handle_plugin(pack_name: str):
    try:
        Data.cache.update({
            pack_name: {
                "funcs": {},
                "classes": {},
                "routes": {}
            }
                        })
        
        if os.path.exists(os.path.join('plugins', pack_name, '__modules__.txt')):
            with open(os.path.join('plugins', pack_name, '__modules__.txt')) as modules:
                download_library(modules.readlines())
        
        md = __import__('plugins.' + pack_name)

        if hasattr(dict(md.__dict__.items())[pack_name], '__description__'):
            if not isinstance(dict(md.__dict__.items())[pack_name].__description__, Description):
                print(f'\033[41mОшибка в плагине {pack_name}: Описание не корректное\033[0m')
                Data.failed_modules += 1
                return
            
            Data.description.update({pack_name: dict(md.__dict__.items())[pack_name].__description__})
        
        if hasattr(dict(md.__dict__.items())[pack_name], 'initialization'):
            if not inspect.isfunction(dict(md.__dict__.items())[pack_name].initialization):
                print(f'\033[41mОшибка в плагине {pack_name}: инициализация не корректная\033[0m')
                Data.failed_modules += 1
                return
            
            Data.initializations.append(dict(md.__dict__.items())[pack_name].initialization)
        
        if os.path.exists(os.path.join('plugins', pack_name, 'manifest.json')):
            with open(os.path.join('plugins', pack_name, 'manifest.json', encoding='utf-8')) as f:
                manifest = json.load(f)
            
            spec = SpecifierSet(manifest['mf_version'])
            current = version.parse(__version__)

            if not spec.contains(current):
                Data.cache.pop(pack_name)
                try:
                    Data.description.pop(pack_name)
                    Data.initializations.pop()
                except IndexError:
                    pass
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