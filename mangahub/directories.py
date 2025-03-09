import os
import sys
from pathlib import Path


'''=== WORKING DIRECTORY ==='''
if getattr(sys, 'frozen', False):   # we are running in executable mode
    STD_DIR = Path(sys.argv[0]).parent
    print(f'Exe detected, working directory: {STD_DIR}')
else:   # we are running in a normal Python environment
    STD_DIR = Path(__file__).parent
    
os.chdir(STD_DIR)
            

'''=== CONFIGS ==='''
CONF_DIR = STD_DIR / 'config'
NOVELS_CONF_DIR = CONF_DIR / 'novels'

'''=== LOGS ==='''
LOG_DIR = STD_DIR / 'logs'

'''=== DATA ==='''
DATA_DIR = STD_DIR / 'data'

NOVELS_DIR = DATA_DIR / 'novels'
MANGA_DIR = DATA_DIR / 'manga'
STATE_DIR = DATA_DIR / 'state'

NOVELS_JSON = DATA_DIR / 'novels.json'
MANGA_JSON = DATA_DIR / 'manga.json'
SITES_JSON = DATA_DIR / 'sites.json'

'''=== RESOURCES ==='''
RESOURCES_DIR = STD_DIR / 'resources'

ICONS_DIR = RESOURCES_DIR / 'icons'
IMAGES_DIR = RESOURCES_DIR / 'img'
BACKGROUNDS_DIR = RESOURCES_DIR / 'background'


'''=== CREATE FOLDERS ==='''
LOG_DIR.mkdir(exist_ok=True)

DATA_DIR.mkdir(exist_ok=True)
MANGA_DIR.mkdir(exist_ok=True)
STATE_DIR.mkdir(exist_ok=True)

RESOURCES_DIR.mkdir(exist_ok=True)
ICONS_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(exist_ok=True)
BACKGROUNDS_DIR.mkdir(exist_ok=True)