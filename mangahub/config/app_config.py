import multiprocessing

from loguru import logger

from .app_config_abs import Config, Setting, Level
from resources.enums import SU, StorageSize
from directories import LOG_DIR, CONF_FILE

logger.add(f"{LOG_DIR}/log-{{time}}.log", format="{time} {level} {message}", level="DEBUG", retention=10)


class AppConfig(Config):
    version = Setting[str]('0.1.0', 'Version', level=Level.USER | Level.READ_ONLY)
    dev_mode = Setting[bool](False, 'Dev Mode', level=Level.USER)
    
    class ImageDownloading(Config):
        convert_image = Setting[bool](False, 'Convert Image')
        preferable_format = Setting[str]('WEBP', 'Converted Images Format')
        
        max_threads = Setting[int](multiprocessing.cpu_count(), 'Max Download Threads')
        chunk_size = Setting[StorageSize](8*SU.KB, 'Image chunk size', strongly_typed=False)
        image_update_every = Setting[int](10, 'Image Update Percentage', '%')        # After image downloaded image_update_every% of size, update
        
        
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
        }, 'Formats that PIL supports')
        
    class UI(Config):
        image_loading_intervals = Setting[int](100, 'Load Images in UI with Intervals', 'ms')
        placeholder_loading_intervals = Setting[int](40, 'Load Placeholders in UI with Intervals', 'ms')
        
    class Scrolling(Config):
        step = Setting[int](150, 'Step', 'px')
        step_duration = Setting[int](200, 'Step Duration', 'ms')
        alt_multiplier = Setting[int](8, 'Alt Step Multiplier')
        
        scale_multiplier = Setting[float](1.0, 'Step Scale Multiplier', level=Level.DEVELOPER)
        
        
try:
    AppConfig.load(CONF_FILE)
except FileNotFoundError:
    logger.warning('Config file wasn\'t found. New one will be created.')