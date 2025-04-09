import asyncio
import aiohttp
import io
from tqdm.asyncio import tqdm_asyncio as tqdm
from pathlib import Path
from PySide6.QtCore import QObject, QThreadPool, QRunnable, Signal, QUrl
from PIL import Image
from icecream import ic

from models.images import ImageMetadata
from utils.image_dimensions import get_dimensions_from_bytes

from directories import IMAGES_CACHE_DIR
from config import AppConfig


class ImageDownloadWorkerSignals(QObject):
    progress = Signal(str, int, int, int)  # url, percent, bytes downloaded, total bytes
    error = Signal(str, Exception)
    

class ImageDownloadWorker(QRunnable):
    """Worker thread for downloading an image without blocking the GUI"""
    _signals = ImageDownloadWorkerSignals()
    
    def __init__(self, url: str, save_path: Path, callback, ext: str='', metadata_only: bool = False, chunk_size: int=8192, update_p: int=1):
        super().__init__()
        
        self.url = url
        self.ext = AppConfig.ImageDownloading.PIL_SUPPORTED_EXT.get(ext.upper()) or 'WEBP'
        
        self.callback = callback
        self.metadata_only = metadata_only
        self.chunk_size = chunk_size
        self.update_p = update_p
    
    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(self._download_image())
        
        self.callback(result)
        
        loop.close()

    async def _download_image(self):
        try:
            async with aiohttp.ClientSession() as session:            
                async with session.get(self.url) as response:
                    if response.status != 200:
                        self._signals.error.emit(self.url, Exception(f'Error getting response: {response.status}'))
                        return
                    
                    size = int(response.headers.get("Content-Length", 0))
                    format = str(response.headers.get("Content-Type", '').split('/')[-1])
                    image_data = bytearray()
                    downloaded = 0
                    prev_percentage = 0
                    
                    if AppConfig.dev_mode:
                        pbar = tqdm(
                            total=size,
                            unit='B',
                            unit_scale=True,
                            desc=f"Downloading {self.url}",
                            disable=False
                        )
                    
                    async for chunk in response.content.iter_chunked(self.chunk_size):
                        if not chunk:
                            break
                        
                        if downloaded == 0:
                            w, h = get_dimensions_from_bytes(chunk)
                            metadata = ImageMetadata(
                                url=self.url,
                                width=w,
                                height=h,
                                format=format,
                                size=size
                            )
                            if self.metadata_only:
                                return metadata, None
                            
                        chunk_size = len(chunk)
                        downloaded += chunk_size
                        image_data.extend(chunk)
                        
                        if AppConfig.dev_mode:
                            pbar.update(chunk_size)
                        if size > 0:
                            percentage = int(downloaded / size * 100)
                            if percentage - prev_percentage >= self.update_p or percentage == 100:
                                prev_percentage = percentage
                                self._signals.progress.emit(
                                    self.url, percentage, downloaded, size
                                )
                    
                    if AppConfig.dev_mode:
                        pbar.close()
                    
                    if size > 0 and downloaded != size:
                        self._signals.error.emit(self.url, Exception(f'Size downloaded does not match with size expected: {downloaded}/{size} bytes'))
                        return
                    
                    image_data = io.BytesIO(image_data)
                    with image_data as f:
                        img = Image.open(f)
                        if self.ext != format:
                            img.save(f, self.ext)
                            
                        return image_data.getvalue(), None
                        
                
        except Exception as e:
            self._signals.error.emit(self.url, Exception(f'Error: {e}'))
            return
        

class ImageDownloader(QObject):
    """Manages parallel downloading of images"""
    
    metadata_ready = Signal(str, dict)  # url, metadata
    image_downloaded = Signal(str, bytes)  # url, local path
    download_error = Signal(str, str)    # url, error message
    download_progress = Signal(str, int, int)  # url, bytes downloaded, total bytes

    def __init__(self, cache: Path=IMAGES_CACHE_DIR, max_threads: int=''):
        super().__init__()
        self.cache = cache
        self.cache.mkdir(exist_ok=True)
        
        self.pool = QThreadPool()
        if not max_threads:
            self.pool.setMaxThreadCount(AppConfig.ImageDownloading.max_threads)
        else:
            self.pool.setMaxThreadCount(max_threads)
        
    def _image_downloaded(self, url, filepath, result):
        image, error = result
        if error:
            self.download_error.emit(url, image)
        with open(filepath, 'wb') as f:
            f.write(image)
        self.image_downloaded.emit(url, image)
        
    def download_metadata(self, url):
        pass
        
    def download_image(self, url: str, name: str='', update_percentage = 1):
        if not QUrl(url).isValid():
            self.download_error.emit(url, 'Url is not valid')
            
        # Finds or creates name and preferable extension
        ext = AppConfig.ImageDownloading.preferable_format
        if name:
            if '.' in name:
                name, ext = name.split('.')
        else:
            name, _ = url.split('/')[-1].split('.')
        name, ext = str(name), str(ext)
        filepath = self.cache / f'{name}.{ext.lower()}'
            
        worker = ImageDownloadWorker(
            url        = url,
            save_path  = self.cache,
            ext        = ext,
            callback   = lambda result: self._image_downloaded(url, filepath, result),
            chunk_size = AppConfig.ImageDownloading.chunk_size,
            update_p   = update_percentage
        )
        self.download_progress = worker._signals.progress
        self.download_error = worker._signals.error
        self.pool.start(worker)

    