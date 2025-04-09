import multiprocessing
from typing import ClassVar
# from enum import Enum
from .app_config_abs import Config, Setting

from loguru import logger


# TODO: Options, name, description, level
# class Config:
#     def __init__(self, name, enum: Enum=Enum):

class AppConfig(Config):
    version: Setting = Setting('Version', '0.1.0')
    dev_mode: ClassVar[bool] = True
    
    class ImageDownloading(Config):
        preferable_format: str = 'WEBP'
        
        max_threads: int = multiprocessing.cpu_count()
        chunk_size: int = 8 * 1024 * 1      # 1KB
        image_update_every: int = 10        # After image downloaded x% of size, update
        
        
        PIL_SUPPORTED_EXT: dict[str, str] = {
            'JPG': 'JPEG',
            'JPEG': 'JPEG',
            'PNG': 'PNG',
            'GIF': 'GIF',
            'BMP': 'BMP',
            'WEBP': 'WEBP',
            'ICO': 'ICO',
            'TIFF': 'TIFF',
            'TIF': 'TIFF'
        }
        
try:
    AppConfig.load()
except FileNotFoundError:
    logger.warning('Config file wasn\'t found. New one will be created.')
AppConfig.save()
print(AppConfig)