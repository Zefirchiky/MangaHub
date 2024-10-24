import os

STD_DIR = os.path.abspath(os.path.dirname(__file__))
os.chdir(STD_DIR)

MANGA_JSON = os.path.join(STD_DIR, 'data', 'manga.json')
SITES_JSON = os.path.join(STD_DIR, 'data', 'sites.json')

ICONS_DIR = os.path.join(STD_DIR, 'resources', 'icons')
MANGA_DIR = os.path.join(STD_DIR, 'data', 'manga')