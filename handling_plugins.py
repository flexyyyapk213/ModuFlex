import os
from loads import Data, Description, download_library
import inspect
import traceback
import logging

logging.basicConfig(filename='script.log', level=logging.WARN)

def handling_plugins():
    folders = os.listdir('plugins')

    for folder in folders:
        try:
            # То есть, папка с именем: Plugin name не будет считаться как плагин
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
                        continue
                    
                    Data.description.update({folder: dict(md.__dict__.items())[folder].__description__})
                
                if hasattr(dict(md.__dict__.items())[folder], 'initialization'):
                    if not inspect.isfunction(dict(md.__dict__.items())[folder].initialization):
                        print(f'\033[41mОшибка в плагине {folder}: инициализация не корректная\033[0m')
                        continue
                    
                    Data.initializations.append(dict(md.__dict__.items())[folder].initialization)
        except Exception as e:
            traceback.print_exc()
            logging.warning(traceback.format_exc())

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
        md = __import__('plugins.' + pack_name + '.__init__.py')

        if hasattr(dict(md.__dict__.items())[pack_name], '__description__'):
            if not isinstance(dict(md.__dict__.items())[pack_name].__description__, Description):
                print(f'\033[41mОшибка в плагине {pack_name}: Описание не корректное\033[0m')
                return
            
            Data.description.update({pack_name: dict(md.__dict__.items())[pack_name].__description__})
        
        if hasattr(dict(md.__dict__.items())[pack_name], 'initialization'):
            if not inspect.isfunction(dict(md.__dict__.items())[pack_name].initialization):
                print(f'\033[41mОшибка в плагине {pack_name}: инициализация не корректная\033[0m')
                return
            
            Data.initializations.append(dict(md.__dict__.items())[pack_name].initialization)
    except Exception as e:
        traceback.print_exc()
        logging.warning(traceback.format_exc())

