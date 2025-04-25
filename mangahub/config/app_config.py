import multiprocessing
import builtins
import sys

from loguru import logger
from rich import print
from rich.console import Console
import rich.traceback

from .app_config_abs import Config, Setting, Level, SettingType
from resources.enums import SU, StorageSize
from directories import LOG_DIR, CONF_FILE

builtins.print = print

logger.add(f"{LOG_DIR}/latest.log", level="DEBUG", backtrace=True, diagnose=True, retention=1, mode='w')
logger.add(f"{LOG_DIR}/log-{{time}}.log", level="DEBUG", backtrace=False, diagnose=False, retention=2, mode='w')

console = Console()
def custom_exception_handler(exc_type: type[BaseException], exc_value: BaseException, traceback):
    logger.opt(exception=(exc_type, exc_value, traceback)).error("An error occurred:")
    
    console.print("\n[bold red]An exception occurred:[/bold red]")
    rich_traceback = rich.traceback.Traceback.from_exception(
        exc_type, exc_value, traceback, 
        show_locals=True, 
        word_wrap=True, 
        indent_guides=True
    )
    console.print(rich_traceback)
    
    console.print(f"[dim]Full error details logged to {f"{LOG_DIR}\\latest.log"}[/dim]")

sys.excepthook = custom_exception_handler


class AppConfig(Config):
    version = Setting[str]('0.1.0', 'Version', level=Level.USER | Level.READ_ONLY)
    dev_mode = Setting[bool](True, 'Dev Mode', level=Level.USER)
    debug_mode = Setting[bool](True, 'Debug Mode', level=Level.USER_DEV)
    
    class ImageDownloading(Config):
        convert_image = Setting[bool](True, 'Convert Image')
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
        class MangaViewer(Config):
            image_loading_intervals = Setting[int](100, 'Load Images in UI with Intervals', 'ms')
            placeholder_loading_intervals = Setting[int](5, 'Load Placeholders in UI with Intervals', 'ms')
            
            set_size_with_every_placeholder = Setting[bool](True, 'Set MangaViewer\'s Scene Size with Every Placeholder Added', level=Level.USER | Level.ADVANCED)
            cull_height_multiplier = Setting[float](2.0, 'Cull Viewport Height Multiplier', level=Level.USER | Level.ADVANCED, type_=SettingType.PERFORMANCE | SettingType.COSMETIC)
            cull_scene_cooldown = Setting[int](250, 'Scene Culling Minimum Cooldown', 'ms', level=Level.USER | Level.ADVANCED, type_=SettingType.PERFORMANCE)
        
    class Scrolling(Config):
        step = Setting[int](150, 'Step', 'px', type_=SettingType.COSMETIC | SettingType.QOL)
        step_duration = Setting[int](200, 'Step Duration', 'ms', type_=SettingType.COSMETIC | SettingType.QOL)
        alt_multiplier = Setting[int](8, 'Alt Step Multiplier', type_=SettingType.QOL)
        
        scale_multiplier = Setting[float](1.5, 'Step Scale Multiplier', level=Level.DEVELOPER, type_=SettingType.PERFORMANCE)
        
    class Caching(Config):
        class Image(Config):
            max_ram = Setting[StorageSize](100*SU.MB, 'Max Ram for Images')
            max_disc = Setting[StorageSize](500*SU.MB, 'Max Disc Space for Images')
        
        
print(f"MangaHub v{AppConfig.version()}")
        
try:
    AppConfig.load(CONF_FILE)
except FileNotFoundError:
    logger.warning('Config file wasn\'t found. New one will be created.')