import shutil
import os
import subprocess
from pyrogram import filters
from typing import Optional, List

CONFLICTS = [
    filters.all,
    filters.private,
    filters.channel,
    filters.group
]

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

def __find_command__(_filters: filters) -> Optional[List[str]]:
    if type(_filters).__name__ == 'CommandFilter':
        if isinstance(_filters.prefixes, list): return _filters.prefixes
        else: return list(_filters.prefixes)
    
    if type(_filters.__dict__['other']).__name__ == 'CommandFilter':
        if isinstance(_filters.__dict__['other'].prefixes, list): return _filters.__dict__['other'].prefixes
        else: return list(_filters.__dict__['other'].prefixes)
    elif type(_filters.__dict__['base']).__name__ == 'CommandFilter':
        if isinstance(_filters.__dict__['base'].prefixes, list): return _filters.__dict__['other'].prefixes
        else: return list(_filters.__dict__['base'].prefixes)
    elif type(_filters.__dict__['base']).__name__ in ['AndFilter', 'OrFilter']:
        return __find_command__(_filters.__dict__['base'])
    else:
        return None

def __find_conflict__(_filters: filters) -> bool:
    if _filters == None:
        return False
    
    if any(_filters == conflict for conflict in CONFLICTS):
        return True
    elif not dict(_filters.__dict__).get('base', False):
        return False

    if any(_filters.__dict__['base'] == conflict for conflict in CONFLICTS):
        return True
    elif any(_filters.__dict__['other'] == conflict for conflict in CONFLICTS):
        return True
    elif type(_filters.__dict__['base']).__name__ in ['AndFilter', 'OrFilter']:
        return __find_conflict__(_filters.__dict__['base'])
    else:
        return False