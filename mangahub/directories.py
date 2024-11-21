from pathlib import Path
import os

STD_DIR = Path(__file__).parent
os.chdir(STD_DIR)

LOG_DIR = STD_DIR / 'logs'

MANGA_JSON = STD_DIR / 'data' / 'manga.json'
SITES_JSON = STD_DIR / 'data' / 'sites.json'

ICONS_DIR = STD_DIR / 'resources' / 'icons'
MANGA_DIR = STD_DIR / 'data' / 'manga'

STATE_DIR = STD_DIR / 'data' / 'state'


LOG_DIR.mkdir(exist_ok=True)
ICONS_DIR.mkdir(exist_ok=True)
MANGA_DIR.mkdir(exist_ok=True)
STATE_DIR.mkdir(exist_ok=True)
