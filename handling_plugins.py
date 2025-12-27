import os
from loads import Data, Description, download_library
import inspect
import traceback
import logging
from __init__ import __version__
from packaging import version
from packaging.specifiers import SpecifierSet

logging.basicConfig(filename='script.log', level=logging.WARN)

def handling_plugins():
    folders = os.listdir('plugins')

    for folder in folders:
        try:
            # То есть, папка с именем: 'Plugin name' не будет считаться как плагин
            if ' ' in folder:
                continue
            
            init_file = os.path.join('plugins', folder, '__init__.py')
            if os.path.exists(init_file):
                Data.cache.update({
                    folder: {
                        "funcs": {},
                        "classes": {}
                    }
                                })

                if os.path.exists(os.path.join('plugins', folder, '__modules__.txt')):
                    if not Data.config['ModuFlex'].get('libs_is_dwnld', False) or Data.config['ModuFlex'].get('libs_is_dwnld', False) and not Data.one_download_libs:
                        with open(os.path.join('plugins', folder, '__modules__.txt')) as modules:
                            download_library(modules.readlines())

                md = __import__('plugins.' + folder + '.__init__')

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
                
                if hasattr(dict(md.__dict__.items())[folder], '__ModuFlex_version__'):
                    if isinstance(dict(md.__dict__.items())[folder].__ModuFlex_version__, str):
                        spec = SpecifierSet(dict(md.__dict__.items())[folder].__ModuFlex_version__)
                        current = version.parse(__version__)

                        if not spec.contains(current):
                            Data.cache.pop(folder)
                            Data.description.pop(folder)
                            Data.initializations.pop()
        except Exception as e:
            traceback.print_exc()
            logging.warning(traceback.format_exc())
            Data.failed_modules += 1

def handle_plugin(pack_name: str):
    try:
        Data.cache.update({
            pack_name: {
                "funcs": {},
                "classes": {}
            }
                        })
        
        if os.path.exists(os.path.join('plugins', pack_name, '__modules__.txt')):
            with open(os.path.join('plugins', pack_name, '__modules__.txt')) as modules:
                download_library(modules.readlines())        
        
        md = __import__('plugins.' + pack_name + '.__init__')

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
        
        if hasattr(dict(md.__dict__.items())[pack_name], '__ModuFlex_version__'):
            if isinstance(dict(md.__dict__.items())[pack_name].__ModuFlex_version__, str):
                spec = SpecifierSet(dict(md.__dict__.items())[pack_name].__ModuFlex_version__)
                current = version.parse(__version__)

                if not spec.contains(current):
                    Data.cache.pop(pack_name)
                    Data.description.pop(pack_name)
                    Data.initializations.pop()
    except Exception as e:
        traceback.print_exc()
        logging.warning(traceback.format_exc())
        Data.failed_modules += 1

def update_command_information(description: Description, plugin_name: str):
    if plugin_name not in Data.description:
        Data.description.update({plugin_name: description})
    
    Data.description[plugin_name].main_description.description = description.main_description.description

    for command in description.funcs_description.values():
        if command.command in Data.description[plugin_name].funcs_description:
            Data.description[plugin_name].funcs_description[command.command].description = command.description
            Data.description[plugin_name].funcs_description[command.command].hyphen = command.hyphen
            Data.description[plugin_name].funcs_description[command.command].parameters = command.parameters
        else:
            Data.description[plugin_name].funcs_description.update({command.command: command})