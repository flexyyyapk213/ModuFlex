import os
from loads import Data, Description
import inspect
import traceback
import logging
import subprocess
import sys
from alive_progress import alive_it, styles
import importlib.util

logging.basicConfig(filename='script.log', level=logging.WARN)

def handling_plugins():
    try:
        folders = os.listdir('plugins')

        for folder in folders:
            init_file = os.path.join('plugins', folder, '__init__.py')
            if os.path.exists(init_file):
                Data.cache.update({
                    folder: {
                        "funcs": {},
                        "classes": {}
                    }
                                })

                if os.path.exists(os.path.join('plugins', folder, '__modules__.txt')):
                    with open(os.path.join('plugins', folder, '__modules__.txt')) as modules:
                        for module in alive_it(modules.readlines(), title='Установка доп. модулей', spinner=styles.SPINNERS['pulse'], theme='smooth'):
                            if importlib.util.find_spec(module) is None:
                                subprocess.run([sys.executable, '-m', 'pip', 'install', module], stdout=subprocess.DEVNULL)
                
                md = __import__('plugins.' + folder + '.__init__')

                if hasattr(dict(md.__dict__.items())[folder], '__description__'):
                    if not isinstance(dict(md.__dict__.items())[folder].__description__, Description):
                        print(f'\033[41mОшибка в плагине {folder}: Описание не корректное\033[0m')
                        continue
                    
                    Data.description.update({folder: dict(md.__dict__.items())[folder].__description__})
                
                if hasattr(dict(md.__dict__.items())[folder], 'initialization'):
                    print(folder)
                    if not inspect.isfunction(dict(md.__dict__.items())[folder].initialization):
                        print(f'\033[41mОшибка в плагине {folder}: инициализация не корректная\033[0m')
                        continue
                    
                    print('successful')
                    Data.initializations.append(dict(md.__dict__.items())[folder].initialization)
    except Exception as e:
        traceback.print_exc()
        logging.warn(traceback.format_exc())

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
                for module in alive_it(modules.readlines(), title='Установка доп. модулей', spinner=styles.SPINNERS['pulse'], theme='smooth'):
                    if importlib.util.find_spec(module) is None:
                        subprocess.run([sys.executable, '-m', 'pip', 'install', module], stdout=subprocess.DEVNULL)
        
        md = __import__('pluging.' + pack_name + '.__init__.py')

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
        logging.warn(traceback.format_exc())