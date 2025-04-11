import multiprocessing

from loguru import logger

from .app_config_abs import Config, Setting
from resources.enums import SU, StorageUnit
from directories import LOG_DIR, CONF_FILE

logger.add(f"{LOG_DIR}/log-{{time}}.log", format="{time} {level} {message}", level="DEBUG", retention=10)


class AppConfig(Config):
    version = Setting[str]('0.1.0', 'Version')
    dev_mode = Setting[bool](True, 'Dev Mode')
    
    class ImageDownloading(Config):
        preferable_format = Setting[str]('WEBP')
        
        max_threads = Setting[int](multiprocessing.cpu_count())
        chunk_size = Setting[StorageUnit](8*SU.KB, 'Image chunk size')
        image_update_every = Setting[int](10)        # After image downloaded image_update_every% of size, update
        
        
        PIL_SUPPORTED_EXT = Setting[dict[str, str]]({
            'JPG':  'JPEG',
            'JPEG': 'JPEG',
            'PNG':  'PNG',
            'GIF':  'GIF',
            'BMP':  'BMP',
            'WEBP': 'WEBP',
            'ICO':  'ICO',
            'TIFF': 'TIFF',
            'TIF':  'TIFF'
        })
        
# try:
#     AppConfig.load(CONF_FILE)
# except FileNotFoundError:
#     logger.warning('Config file wasn\'t found. New one will be created.')
# AppConfig().save(CONF_FILE)