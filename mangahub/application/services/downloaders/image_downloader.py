import asyncio
import httpx
import io
import time
from pathlib import Path
import logging
from PySide6.QtCore import QObject, QThreadPool, QRunnable, Signal, QUrl, Slot
from PIL import Image
import tenacity
from loguru import logger

from domain.models.images import ImageMetadata, ImageCache
from utils import ThreadingManager
from config import Config


try:
    jxl_supported = 'JXL' in Image.registered_extensions().values()  # TODO: Make it global state
    jxl_supported = True
except Exception:
    pass

class ImageDownloader(QObject):
    """
    Handles the asynchronous downloading and processing of images.
    Emits signals for progress, metadata (with dimensions), and completion.
    """
    metadata_downloaded = Signal(ImageMetadata)
    download_progress = Signal(str, str, float, int, int, int)   # url, name, percent, downloaded_bytes, diff_bytes, total_bytes
    download_finished = Signal(ImageMetadata)
    download_error = Signal(str, str, tuple)
    
    def __init__(self, client: httpx.AsyncClient, cache: ImageCache):
        super().__init__()
        self.client = client
        self.cache = cache
        
    @tenacity.retry(
        stop=tenacity.stop_after_attempt(Config.Downloading.max_retries()),
        wait=tenacity.wait_fixed(Config.Downloading.min_wait_time()),
        reraise=True,
    )
    async def _download_and_process_single_image(self, url, name):
        image_buffer = io.BytesIO()
        downloaded_bytes = 0
        prev_downloaded_bytes = 0
        diff_bytes = 0
        total_size = 0
        width, height = 0, 0
        metadata_emited = False
        
        # dt = time.perf_counter()
        try:
            async with self.client.stream('GET', url) as response:
                response.raise_for_status()
                
                if content_length := response.headers.get('Content-Length'):
                    total_size = int(content_length)
                    
                async for chunk in response.aiter_bytes(Config.Downloading.Image.chunk_size().bytes_value):
                    bytes_written = image_buffer.write(chunk)
                    downloaded_bytes += bytes_written
                    diff_bytes = downloaded_bytes - prev_downloaded_bytes
                    prev_downloaded_bytes = 0
                    
                    if not metadata_emited and downloaded_bytes > 0:
                        try:
                            img_temp = Image.open(image_buffer)
                            img_temp.verify()
                            width, height = img_temp.size
                            self.metadata_downloaded.emit(ImageMetadata(
                                url=url, name=name, width=width, height=height, size=total_size, format=img_temp.format
                            ))
                            metadata_emited = True
                        except Exception:
                            pass
                        
                    percent = (downloaded_bytes / total_size * 100) if total_size > 0 else 0
                    self.download_progress.emit(url, name, percent, downloaded_bytes, diff_bytes, total_size)
            # print('Downloading: ', time.perf_counter() - dt)
            # --- Image Optimization ---
            image_buffer.seek(0)
            original_image_bytes = image_buffer.getvalue()

            try:
                img = Image.open(io.BytesIO(original_image_bytes)).convert('RGB')   # TODO: Conversion helped greatly, but playing with it may improve perf even more
            except Exception as e:
                raise ValueError(f"Could not open image from downloaded data: {e}")
            if not metadata_emited:
                width, height = img_temp.size
                self.metadata_downloaded.emit(ImageMetadata(
                    url=url, name=name, width=img.width, height=img.height, size=len(original_image_bytes), format=img_temp.format
                ))
            # dt = time.perf_counter()
            optimized_image_buffer = io.BytesIO()
            format_to_save = '.webp'
            
            if jxl_supported:
                try:
                    img.save(optimized_image_buffer, format='JXL', lossless=True, effort=1) # TODO: Tweak params
                    format_to_save = '.jxl'
                except Exception:
                    img.save(optimized_image_buffer, format='WEBP', lossless=True, method=6, quality=100)
            else:
                img.save(optimized_image_buffer, format='WEBP', lossless=True, method=6, quality=100)
            # print('Save: ', time.perf_counter() - dt)
            name = name + format_to_save
            self.cache.add(name, optimized_image_buffer.getvalue())
            self.download_finished.emit(ImageMetadata(
                    url=url, name=name, width=img.width, height=img.height, size=len(optimized_image_buffer.getvalue()), format=format_to_save
                ))
        
            
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error {e.response.status_code} for {url}: {e.response.text}"
            logger.error(error_msg)
            raise # Re-raise for tenacity to handle retries
        except httpx.RequestError as e:
            error_msg = f"Network error during download of {url}: {e}"
            logger.error(error_msg)
            raise # Re-raise for tenacity to handle retries
        except Exception as e:
            error_msg = f"An unexpected error occurred for {url}: {e}"
            logger.error(error_msg, exc_info=True)
            raise # Re-raise for tenacity to handle retries
        

class ImageDownloaderWorker(QRunnable):
    """
    QRunnable to execute ImageDownloader tasks in a separate thread.
    """
    def __init__(self, client: httpx.AsyncClient, cache: ImageCache, urls: list[str], names: list[str]):
        super().__init__()
        self.client = client
        self.urls = urls
        self.names = names
        # ImageDownloader instance will emit signals
        self.downloader = ImageDownloader(client, cache)

        # We don't connect signals directly here, but expose them for the Main Window
        # The MainWindow will connect to these signals
        self.metadata_downloaded = self.downloader.metadata_downloaded
        self.download_progress = self.downloader.download_progress
        self.download_finished = self.downloader.download_finished
        self.download_error = self.downloader.download_error
        
    @Slot()
    def run(self):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        try:
            tasks = [self.downloader._download_and_process_single_image(url, name)
                     for url, name in zip(self.urls, self.names)]
            
            results = loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Task for {self.urls[i]} failed in worker: {result}")
            
        except Exception as e:
            logger.critical(f"ImageDownloaderWorker: Unhandled exception in worker thread for URLs {self.urls}: {e}", exc_info=True)
            for url in self.urls: # Fallback to emit error for all URLs if a critical error
                self.downloader.download_error.emit(url, f"Critical internal error: {e}")
                
        finally:
            loop.close()
            

class ImageDownloadManager(QObject):
    metadata_downloaded = Signal(ImageMetadata)
    downloaded = Signal(ImageMetadata)
    download_error = Signal(str, str, tuple)
    overall_progress = Signal(str, str, float, int, int, int)
    all_downloaded = Signal()
    
    def __init__(self, cache: ImageCache):
        super().__init__()
        self.cache = cache
        self.thread_pool = QThreadPool(maxThreadCount=Config.Downloading.Image.max_threads())
        
    def _add_to_overall_progress(self, url, name, percent, downloaded, diff, total):
        pass
    
    def _image_downloaded(self, metadata: ImageMetadata):
        if not self.thread_pool.activeThreadCount():
            self.all_downloaded.emit()
    
    def download_images_sep_thread(self, urls: list[str], names: list[str]=None, cache: ImageCache=None) -> ImageDownloaderWorker:
        """
        Downloads a list of images in separate threads.

        Args:
            urls: list of URLs to download
            names: list of names to associate with the downloaded images (optional)
            cache: cache to store the downloaded images (optional)

        Returns:
            ImageDownloaderWorker: worker object that can be used to track the progress
        """
        client = httpx.AsyncClient(timeout=10, follow_redirects=True)
        worker = ImageDownloaderWorker(client, cache or self.cache, urls, names or urls)
        worker.setAutoDelete(True)
        worker.metadata_downloaded.connect(self.metadata_downloaded.emit)
        worker.download_finished.connect(self.downloaded.emit)
        worker.download_finished.connect(self._image_downloaded)
        worker.download_error.connect(self.download_error.emit)
        self.thread_pool.start(worker)
        return worker

# cache = ImageCache(Config.Dirs.CACHE, 0)
# d = ImageDownloadManager(cache)
# dt = time.perf_counter()
# d.download_images_sep_thread(['https://asurascans.imagemanga.online/aHR0cHM6Ly9nZy5hc3VyYWNvbWljLm5ldC9zdG9yYWdlL21lZGlhLzEyMjc1OC9jb252ZXJzaW9ucy8wMS1vcHRpbWl6ZWQud2VicA/aHR0cHM6Ly9hc3VyYWNvbWljLm5ldC9zZXJpZXMvbmFuby1tYWNoaW5lLWFkZDgxMmY2'], ['test']).download_finished.connect(lambda: print(time.perf_counter() - dt))