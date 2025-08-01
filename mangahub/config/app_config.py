import multiprocessing
import builtins
import sys

from loguru import logger
from rich import print
from rich.console import Console
import rich.traceback
import pillow_jxl

from easy_config_hub import Config_, DirectoriesConfig_, Setting, Level, SettingType
from resources.enums import SU, StorageSize


class Config(Config_):
    version = Setting[str]("0.1.0", "Version", level=Level.USER | Level.READ_ONLY)
    dev_mode = Setting[bool](True, "Dev Mode", level=Level.USER)
    debug_mode = Setting[bool](True, "Debug Mode", level=Level.USER_DEV)

    class Downloading(Config_):
        max_retries = Setting[int](3, "Maximum Download Retries")
        min_wait_time = Setting[int](1, "Minimum Time between Retries")
        
        class Chapter(Config_):
            time_wait_before_loading = Setting[int](300, "Time to Wait before Attempting to Download Chapter", 'ms')
        
        class Image(Config_):
            convert_image = Setting[bool](True, "Convert Image")
            preferable_format = Setting[str]("WEBP", "Converted Images Format")

            max_threads = Setting[int](multiprocessing.cpu_count(), "Max Download Threads")
            chunk_size = Setting[StorageSize](
                8 * SU.KB, "Image chunk size", strongly_typed=False
            )
            image_update_every = Setting[int](
                10, "Image Update Percentage", "%"
            )  # After image downloaded image_update_every% of size, update

            PIL_SUPPORTED_EXT = Setting[dict[str, str]](
                {
                    "JPG": "JPEG",
                    "JPEG": "JPEG",
                    "PNG": "PNG",
                    "GIF": "GIF",
                    "BMP": "BMP",
                    "WEBP": "WEBP",
                    "ICO": "ICO",
                    "TIFF": "TIFF",
                    "TIF": "TIFF",
                },
                "Formats that PIL supports",
            )

    class UI(Config_):
        class Scrolling(Config_):
            step = Setting[int](
                150, "Step", "px", type_=SettingType.COSMETIC | SettingType.QOL
            )
            step_duration = Setting[int](
                200, "Step Duration", "ms", type_=SettingType.COSMETIC | SettingType.QOL
            )
            alt_multiplier = Setting[int](8, "Alt Step Multiplier", type_=SettingType.QOL)

            scale_multiplier = Setting[float](
                1.5,
                "Step Scale Multiplier",
                level=Level.DEVELOPER,
                type_=SettingType.PERFORMANCE,
            )
            
    class Performance(Config_):
        class MangaViewer(Config_):
            image_loading_intervals = Setting[int](
                100, "Load Images in UI with Intervals", "ms"
            )
            placeholder_loading_intervals = Setting[int](
                10, "Load Placeholders in UI with Intervals", "ms"
            )

            set_size_with_every_placeholder = Setting[bool](
                True,
                "Set MangaViewer's Scene Size with Every Placeholder Added",
                level=Level.USER | Level.ADVANCED,
                type_=SettingType.PERFORMANCE | SettingType.COSMETIC,
            )
            cull_height_multiplier = Setting[float](
                2.0,
                "Cull Viewport Height Multiplier",
                level=Level.USER | Level.ADVANCED,
                type_=SettingType.PERFORMANCE | SettingType.COSMETIC,
            )
            cull_scene_cooldown = Setting[int](
                250,
                "Scene Culling Minimum Cooldown",
                "ms",
                level=Level.USER | Level.ADVANCED,
                type_=SettingType.PERFORMANCE,
            )
            

    class Caching(Config_):
        class Image(Config_):
            max_ram = Setting[StorageSize](00 * SU.MB, "Max Ram for Images")
            max_disc = Setting[StorageSize](500 * SU.MB, "Max Disc Space for Images")
            
    class DataProcessing(Config_):
        class UrlParsing(Config_):
            replace_symbols = Setting[dict[str, str]]({
                ' ': '-',
                "'": '',
            })

    class Dirs(DirectoriesConfig_):
        STD_DIR = DirectoriesConfig_.STD_DIR

        """=== CONFIGS ==="""
        CONF = STD_DIR / "config"
        CONF_JSON = CONF / "config.json"
        NOVELS_CONF = CONF / "novels"

        """=== LOGS ==="""
        LOG = STD_DIR / "logs"

        """=== CACHE ==="""
        CACHE = STD_DIR / "cache"
        IMAGES_CACHE = CACHE / "images"

        """=== DATA ==="""
        DATA = STD_DIR / "data"

        NOVELS = DATA / "novels"
        MANGA = DATA / "manga"
        STATE = DATA / "state"

        NOVELS_JSON = DATA / "novels.json"
        MANGA_JSON = DATA / "manga.json"
        SITES_JSON = DATA / "sites.json"
        
        NOVEL_DRAFT = NOVELS / "draft.md"

        """=== RESOURCES ==="""
        RESOURCES = STD_DIR / "resources"

        ICONS = RESOURCES / "icons"
        IMAGES = RESOURCES / "img"
        BACKGROUNDS = RESOURCES / "background"


builtins.print = print

logger.add(
    f"{Config.Dirs.LOG}/latest.log",
    level="DEBUG",
    backtrace=True,
    diagnose=True,
    retention=1,
    mode="w",
)
logger.add(
    f"{Config.Dirs.LOG}/log-{{time}}.log",
    level="DEBUG",
    backtrace=False,
    diagnose=False,
    retention=2,
    mode="w",
)

console = Console()


def custom_exception_handler(
    exc_type: type[BaseException], exc_value: BaseException, traceback
):
    logger.opt(exception=(exc_type, exc_value, traceback)).error("An error occurred:")

    console.print("\n[bold red]An exception occurred:[/bold red]")
    rich_traceback = rich.traceback.Traceback.from_exception(
        exc_type,
        exc_value,
        traceback,
        show_locals=True,
        word_wrap=True,
        indent_guides=True,
    )
    console.print(rich_traceback)

    console.print(
        f"[dim]Full error details logged to {f'{Config.Dirs.LOG}\\latest.log'}[/dim]"
    )


sys.excepthook = custom_exception_handler

print(f"MangaHub v{Config.version()}")

try:
    Config.load(Config.Dirs.CONF_JSON)
except FileNotFoundError:
    logger.warning("Config file wasn't found. New one will be created.")
