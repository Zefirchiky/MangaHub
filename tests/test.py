import asyncio
import aiohttp
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Callable
from PySide6.QtCore import QObject, Signal, QThreadPool, QRunnable, QSize
import os
import time
from dataclasses import dataclass

@dataclass
class ImageMetadata:
    url: str
    width: int = 0
    height: int = 0
    size: int = 0
    format: str = ""
    cached_path: Optional[str] = None

class ImageDownloadWorker(QRunnable):
    """Worker thread for downloading an image without blocking the GUI"""
    
    def __init__(self, url: str, save_path: Path, callback: Callable, metadata_only: bool = False):
        super().__init__()
        self.url = url
        self.save_path = save_path
        self.callback = callback
        self.metadata_only = metadata_only
        
    def run(self):
        try:
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run the download task
            result = loop.run_until_complete(self._download_image())
            
            # Call the callback with the result
            self.callback(result)
            
            # Clean up
            loop.close()
        except Exception as e:
            # Handle exceptions and pass to callback
            self.callback((None, str(e)))
    
    async def _download_image(self) -> Path | None, dict:
        """Download image or just its metadata based on metadata_only flag"""
        try:
            async with aiohttp.ClientSession() as session:
                # First request with HEAD to get metadata without downloading the full image
                async with session.head(self.url) as response:
                    if response.status != 200:
                        return None, f"Failed to get metadata: {response.status}"
                    
                    # Extract image size and other metadata
                    content_length = int(response.headers.get('Content-Length', 0))
                    content_type = response.headers.get('Content-Type', '')
                    
                    # If we only need metadata, return here
                    if self.metadata_only:
                        # We'll determine width/height when we download a small portion
                        return self.save_path, {
                            'size': content_length,
                            'format': content_type,
                            'url': self.url
                        }
                
                # If we need the full image, download it
                async with session.get(self.url) as response:
                    if response.status != 200:
                        return None, f"Failed to download image: {response.status}"
                    
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
                    
                    # Stream the content to a file
                    with open(self.save_path, 'wb') as f:
                        while True:
                            chunk = await response.content.read(8192)  # Read in 8kb chunks
                            if not chunk:
                                break
                            f.write(chunk)
                    
                    return self.save_path, None
                    
        except Exception as e:
            return None, str(e)

class ImageDownloader(QObject):
    """Manages parallel downloading of images"""
    
    metadata_ready = Signal(str, dict)  # url, metadata
    image_downloaded = Signal(str, Path)  # url, local path
    download_error = Signal(str, str)    # url, error message
    download_progress = Signal(str, int, int)  # url, bytes downloaded, total bytes
    
    def __init__(self, cache_dir: str = "cache", max_concurrent: int = 4):
        super().__init__()
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True, parents=True)
        
        # Create thread pool for downloads
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(max_concurrent)
        
        # Track ongoing downloads to prevent duplicates
        self._ongoing_downloads = set()
        self._metadata_cache = {}  # url -> metadata
    
    def _get_cache_path(self, url: str) -> Path:
        """Generate a unique file path for caching an image"""
        # Create a filename based on the URL (you might want to use a hash instead)
        filename = url.split('/')[-1]
        # Add a timestamp to prevent collisions
        timestamp = int(time.time() * 1000)
        cache_file = f"{timestamp}_{filename}"
        return self.cache_dir / cache_file
    
    def _download_completed(self, url: str, result: Tuple[Optional[Path], Optional[str]]):
        """Callback when a download is complete"""
        self._ongoing_downloads.remove(url)
        
        path, error = result
        if error:
            self.download_error.emit(url, error)
        else:
            self.image_downloaded.emit(url, path)
    
    def _metadata_completed(self, url: str, result: Tuple[Optional[Path], Optional[dict]]):
        """Callback when metadata retrieval is complete"""
        self._ongoing_downloads.remove(url)
        
        path, metadata = result
        if isinstance(metadata, dict):
            self._metadata_cache[url] = metadata
            self.metadata_ready.emit(url, metadata)
        else:
            # metadata is actually an error message in this case
            self.download_error.emit(url, metadata)
    
    def get_metadata(self, url: str):
        """Get image metadata without downloading the full image"""
        if url in self._ongoing_downloads:
            return
        
        if url in self._metadata_cache:
            # Use cached metadata if available
            self.metadata_ready.emit(url, self._metadata_cache[url])
            return
            
        self._ongoing_downloads.add(url)
        cache_path = self._get_cache_path(url)
        
        # Create and start worker
        worker = ImageDownloadWorker(
            url=url,
            save_path=cache_path,
            callback=lambda result: self._metadata_completed(url, result),
            metadata_only=True
        )
        self.thread_pool.start(worker)
    
    def download_image(self, url: str):
        """Download an image in a separate thread"""
        if url in self._ongoing_downloads:
            return
            
        self._ongoing_downloads.add(url)
        cache_path = self._get_cache_path(url)
        
        # Create and start worker
        worker = ImageDownloadWorker(
            url=url,
            save_path=cache_path,
            callback=lambda result: self._download_completed(url, result)
        )
        self.thread_pool.start(worker)
    
    def download_multiple(self, urls: List[str], metadata_first: bool = True):
        """Download multiple images, optionally getting metadata first"""
        if metadata_first:
            # First get metadata for all images
            for url in urls:
                self.get_metadata(url)
        
        # Then download the actual images
        for url in urls:
            self.download_image(url)
            
            
            
            
            
            
            
            
            
            
            
class ImageCache:
    """Manages caching of downloaded images"""
    
    def __init__(self, max_size_mb: int = 500):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.current_size_bytes = 0
        self._cache = {}  # url -> (path, size, last_accessed)
    
    def add(self, url: str, path: Path, size_bytes: int):
        """Add an image to the cache"""
        # If adding would exceed max cache size, remove least recently used items
        if self.current_size_bytes + size_bytes > self.max_size_bytes:
            self._evict_lru(size_bytes)
        
        # Add to cache with current timestamp
        self._cache[url] = (path, size_bytes, time.time())
        self.current_size_bytes += size_bytes
    
    def get(self, url: str) -> Optional[Path]:
        """Get an image from the cache if it exists and update its access time"""
        if url in self._cache:
            path, size, _ = self._cache[url]
            # Update access time
            self._cache[url] = (path, size, time.time())
            return path
        return None
    
    def _evict_lru(self, required_space: int):
        """Remove least recently used items to free up space"""
        # Sort by access time (oldest first)
        sorted_items = sorted(self._cache.items(), key=lambda x: x[1][2])
        
        # Remove items until we have enough space
        space_freed = 0
        items_to_remove = []
        
        for url, (path, size, _) in sorted_items:
            items_to_remove.append(url)
            space_freed += size
            if space_freed >= required_space:
                break
        
        # Remove the items
        for url in items_to_remove:
            path, size, _ = self._cache[url]
            del self._cache[url]
            self.current_size_bytes -= size
            
            # Optionally delete the file from disk
            try:
                os.remove(path)
            except OSError:
                pass  # Ignore errors when removing files
            
            
            
            
            
            
            
            
            
            
            
            
from PySide6.QtGui import QColor, QPixmap, QPainter, QLinearGradient, QFont
from PySide6.QtCore import Qt

class PlaceholderGenerator:
    """Generates placeholder images"""
    
    @staticmethod
    def create_placeholder(width: int, height: int, text: str = "", color: QColor = QColor(200, 200, 200)):
        """Create a placeholder image with dimensions and optional text"""
        # Create a pixmap
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # Paint a gradient background
        painter = QPainter(pixmap)
        gradient = QLinearGradient(0, 0, width, height)
        gradient.setColorAt(0, color.lighter(120))
        gradient.setColorAt(1, color.darker(120))
        painter.fillRect(0, 0, width, height, gradient)
        
        # Add text for dimensions if no text provided
        if not text:
            text = f"{width}x{height}"
        
        # Draw the text
        font = QFont("Arial", 12)
        painter.setFont(font)
        painter.setPen(QColor(0, 0, 0, 180))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, text)
        
        painter.end()
        return pixmap
    
    @staticmethod
    def create_loading_placeholder(width: int, height: int, progress: int = 0):
        """Create a placeholder showing loading progress"""
        pixmap = QPixmap(width, height)
        pixmap.fill(QColor(230, 230, 230))
        
        painter = QPainter(pixmap)
        
        # Draw progress bar
        if progress > 0:
            progress_height = height // 20
            progress_y = height // 2 - progress_height // 2
            
            # Background
            painter.fillRect(10, progress_y, width - 20, progress_height, QColor(180, 180, 180))
            
            # Actual progress
            progress_width = int((width - 20) * (progress / 100))
            painter.fillRect(10, progress_y, progress_width, progress_height, QColor(100, 180, 100))
            
        # Draw text
        font = QFont("Arial", 14)
        painter.setFont(font)
        painter.setPen(QColor(80, 80, 80))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, f"Loading... {progress}%")
        
        painter.end()
        return pixmap
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
class ChapterImageLoader(QObject):
    """Manages loading of chapter images and preloading of adjacent chapters"""
    
    chapter_loaded = Signal(int)  # chapter_index
    image_loaded = Signal(int, int, Path)  # chapter_index, image_index, image_path
    placeholder_ready = Signal(int, int, QPixmap)  # chapter_index, image_index, placeholder
    
    def __init__(self, image_downloader: ImageDownloader, image_cache: ImageCache):
        super().__init__()
        self.downloader = image_downloader
        self.cache = image_cache
        self.placeholder_generator = PlaceholderGenerator()
        
        # Connect signals
        self.downloader.metadata_ready.connect(self._on_metadata_ready)
        self.downloader.image_downloaded.connect(self._on_image_downloaded)
        
        # Map of URL to (chapter_index, image_index)
        self._url_mapping = {}
        
        # Keep track of loaded chapters
        self._loaded_chapters = set()
        
        # Current chapter being viewed
        self.current_chapter_index = 0
    
    def load_chapter(self, chapter_index: int, urls: List[str]):
        """Load all images for a chapter"""
        # Store the URL mapping for this chapter
        for image_index, url in enumerate(urls):
            self._url_mapping[url] = (chapter_index, image_index)
        
        # Start downloading metadata for placeholders
        for url in urls:
            self.downloader.get_metadata(url)
        
        # Mark this chapter as loaded (in terms of requesting downloads)
        self._loaded_chapters.add(chapter_index)
        
        # Preload adjacent chapters
        self._preload_adjacent_chapters(chapter_index)
    
    def set_current_chapter(self, chapter_index: int):
        """Set the current chapter being viewed and manage preloading"""
        if chapter_index == self.current_chapter_index:
            return
            
        self.current_chapter_index = chapter_index
        self._preload_adjacent_chapters(chapter_index)
    
    def _preload_adjacent_chapters(self, chapter_index: int):
        """Preload the chapters before and after the current chapter"""
        # We'll preload chapters [chapter_index+1, chapter_index+2]
        # This assumes chapters are indexed sequentially
        
        # Logic to determine which chapters to preload would go here
        # For now, we'll just preload the next two chapters
        chapters_to_preload = [chapter_index + 1, chapter_index + 2]
        
        # Your code to get URLs for these chapters would go here
        # For example:
        # for preload_index in chapters_to_preload:
        #     urls = self._get_chapter_urls(preload_index)
        #     if urls:
        #         self.load_chapter(preload_index, urls)
    
    def _on_metadata_ready(self, url: str, metadata: dict):
        """Handle when image metadata is available"""
        if url not in self._url_mapping:
            return
            
        chapter_index, image_index = self._url_mapping[url]
        
        # Create a placeholder based on the metadata
        width = metadata.get('width', 800)  # Default if not available
        height = metadata.get('height', 1200)  # Default if not available
        
        # Create and emit placeholder
        placeholder = self.placeholder_generator.create_placeholder(width, height)
        self.placeholder_ready.emit(chapter_index, image_index, placeholder)
    
    def _on_image_downloaded(self, url: str, path: Path):
        """Handle when an image has been downloaded"""
        if url not in self._url_mapping:
            return
            
        chapter_index, image_index = self._url_mapping[url]
        
        # Add to cache
        file_size = os.path.getsize(path)
        self.cache.add(url, path, file_size)
        
        # Emit signal that image is loaded
        self.image_loaded.emit(chapter_index, image_index, path)