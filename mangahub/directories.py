from pathlib import Path
import os

'''=== WORKING DIRECTORY ==='''
STD_DIR = Path(__file__).parent
os.chdir(STD_DIR)

'''=== LOGS ==='''
LOG_DIR = STD_DIR / 'logs'

'''=== DATA ==='''
DATA_DIR = STD_DIR / 'data'

MANGA_DIR = DATA_DIR / 'manga'
STATE_DIR = DATA_DIR / 'state'

MANGA_JSON = DATA_DIR / 'manga.json'
SITES_JSON = DATA_DIR / 'sites.json'

'''=== RESOURCES ==='''
RESOURCES_DIR = STD_DIR / 'resources'

ICONS_DIR = RESOURCES_DIR / 'icons'



LOG_DIR.mkdir(exist_ok=True)

DATA_DIR.mkdir(exist_ok=True)
MANGA_DIR.mkdir(exist_ok=True)
STATE_DIR.mkdir(exist_ok=True)

RESOURCES_DIR.mkdir(exist_ok=True)
ICONS_DIR.mkdir(exist_ok=True)
