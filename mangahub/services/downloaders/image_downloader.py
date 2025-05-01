import asyncio
import aiohttp
import io
from PySide6.QtCore import QObject, QThreadPool, QRunnable, Signal, QUrl
from PIL import Image

from models.images import ImageMetadata, ImageCache
from utils.image_dimensions import get_dimensions_from_bytes

from config import AppConfig


class ImageDownloadWorkerSignals(QObject):
    progress = Signal(
        str, int, int, int, int
    )  # url, percent, bytes downloaded, bytes downloaded diff, total bytes
    metadata = Signal(str, ImageMetadata)  # url, metadata
    error = Signal(str, Exception)


# TODO: Better use of async
class ImageDownloadWorker(QRunnable):
    """Worker thread for downloading an image without blocking the GUI"""

    _signals = ImageDownloadWorkerSignals()

    def __init__(
        self,
        url: str,
        callback,
        ext: str = "",
        metadata_only: bool = False,
        chunk_size: int = 8192,
        update_p: int = 1,
        convert=True,
    ):
        super().__init__()

        self.url = url
        self.ext = (
            AppConfig.ImageDownloading.PIL_SUPPORTED_EXT().get(ext.upper()) or "WEBP"
        )

        self.callback = callback
        self.metadata_only = metadata_only
        self.chunk_size = chunk_size
        self.update_p = update_p
        self.convert = convert

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
                        return (
                            None,
                            None,
                            Exception(f"Error getting response: {response.status}"),
                        )

                    size = int(response.headers.get("Content-Length", 0))
                    format = str(
                        response.headers.get("Content-Type", "").split("/")[-1]
                    )
                    image_data = bytearray()
                    downloaded = 0
                    prev_percentage = 0
                    diff = 0

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
                                size=size,
                            )
                            if self.metadata_only:
                                return None, metadata, None
                            self._signals.metadata.emit(self.url, metadata)

                        chunk_size = len(chunk)
                        diff += chunk_size
                        downloaded += chunk_size
                        image_data.extend(chunk)

                        if size > 0:
                            percentage = int(downloaded / size * 100)
                            if (
                                percentage - prev_percentage >= self.update_p
                                or percentage == 100
                            ):
                                prev_percentage = percentage
                                self._signals.progress.emit(
                                    self.url, percentage, downloaded, diff, size
                                )
                                diff = 0

                    if size > 0 and downloaded != size:
                        return (
                            None,
                            None,
                            Exception(
                                f"Size downloaded does not match with size expected: {downloaded}/{size} bytes"
                            ),
                        )

                    if self.convert:
                        image_data = io.BytesIO(image_data)
                        with image_data as f:
                            img = Image.open(f)
                            if self.ext != format:
                                img.save(
                                    f, self.ext, optimize=True
                                )  # TODO: Better conversion

                            return image_data.getvalue(), metadata, None

                    return image_data, metadata, None

        except Exception as e:
            return None, None, Exception(f"Error: {e}")


class ImageDownloader(QObject):
    """Manages parallel downloading of images"""

    metadata_downloaded = ImageDownloadWorker._signals.metadata
    image_downloaded = Signal(str, str, ImageMetadata)  # url, name.ext, metadata
    overall_download_progress = Signal(
        int, int, int, int
    )  # len(urls), percent, current bytes, total bytes
    download_progress = ImageDownloadWorker._signals.progress
    download_error = ImageDownloadWorker._signals.error
    finished = Signal(int)

    def __init__(self, cache: ImageCache, max_threads: int = 0):
        super().__init__()
        self.cache = cache

        self.pool = QThreadPool()
        if not max_threads:
            self.pool.setMaxThreadCount(AppConfig.ImageDownloading.max_threads())
        else:
            self.pool.setMaxThreadCount(max_threads)

        self.workers = {}

        self.counted_urls = set()
        self.total_bytes = 0
        self.total_bytes_is_known = False
        self.current_bytes = 0
        self.percent = 0
        self.download_progress.connect(
            lambda url, percent, downloaded, diff, total: self._update_overall_progress(
                url, diff, total
            )
        )

    def _update_overall_progress(self, url: str, diff: int, total: int):
        if not self.total_bytes_is_known and url not in self.counted_urls:
            self.total_bytes += total
            self.counted_urls.add(url)
        self.current_bytes += diff

        if self.total_bytes > 0:  # Avoid division by zero
            percent = int(self.current_bytes / self.total_bytes * 100)
            if (
                percent >= self.percent + 1 or percent == 100
            ):  # TODO: Update every 1% change   Add setting for this
                self.percent = percent
                self.overall_download_progress.emit(
                    len(self.counted_urls),
                    percent,
                    self.current_bytes,
                    self.total_bytes,
                )

    def _metadata_downloaded(self, url, name, result, emit_finish):
        _, metadata, err = result
        if err:
            self.download_error.emit(url, err)
            return
        self.workers.pop(name)
        if emit_finish and not self.workers:
            self.finished.emit(0)
        self.metadata_downloaded.emit(url, metadata)

    def _image_downloaded(self, url, name, result, emit_finish):
        image, metadata, err = result
        if err:
            self.download_error.emit(url, err)
            return
        self.workers.pop(name)
        if emit_finish and not self.workers:
            self.finished.emit(self.total_bytes)
        self.cache.add_image(name, image, metadata.size)
        self.image_downloaded.emit(url, name, metadata)

    def download_metadata(self, url: str, name: str = "", emit_finish=True):
        url_ = QUrl(url)
        if not url_.isValid():
            self.download_error.emit(url, "Url is not valid")
        url = url_.toString()

        # Finds or creates name and preferable extension
        ext = AppConfig.ImageDownloading.preferable_format()
        if name:
            if "." in name:
                name, ext = name.split(".")
        else:
            name, _ = url.split("/")[-1].split(".")
        name, ext = str(name), str(ext)
        name = f"{name}.{ext.lower()}"

        worker = ImageDownloadWorker(
            url=url,
            ext=ext,
            callback=lambda result: self._metadata_downloaded(
                url, name, result, emit_finish
            ),
            chunk_size=AppConfig.ImageDownloading.chunk_size().bytes_value,
            metadata_only=True,
        )
        self.workers[name] = worker
        self.pool.start(worker)

    def download_image(
        self,
        url: str,
        name: str = "",
        update_percentage=1,
        convert=True,
        emit_finish=True,
    ):
        url_ = QUrl(url)
        if not url_.isValid():
            self.download_error.emit(url, "Url is not valid")
        url = url_.toString()

        # Finds or creates name and preferable extension
        ext = AppConfig.ImageDownloading.preferable_format()
        if name:
            if "." in name:
                name, ext = name.split(".")
        else:
            name, _ = url.split("/")[-1].rsplit(".", 1)
        name, ext = str(name), str(ext)
        name = f"{name}.{ext.lower()}"

        worker = ImageDownloadWorker(
            url=url,
            ext=ext,
            callback=lambda result: self._image_downloaded(
                url, name, result, emit_finish
            ),
            chunk_size=AppConfig.ImageDownloading.chunk_size().bytes_value,
            update_p=update_percentage,
            convert=convert,
        )
        self.workers[name] = worker
        self.pool.start(worker)

    def download_images(
        self,
        urls: dict[str, str],
        update_percentage=10,
        metadata_only=False,
        convert=True,
        total_bytes=0,
    ):
        """Downloads images async.

        Args:
            urls (dict[str, str]): Dictionary of urls and their preferable names. If extension is not in the name, preferable one will be used (check AppConfig.ImageDownloading.preferable_format)
            update_percentage (int, optional): ImageDownloader will emit download_progress signal every x%. Defaults to 10.
            metadata_only (bool, optional): Will only download metadata, emits metadata_downloaded. Defaults to False.
        """
        if total_bytes:
            self.total_bytes = total_bytes
            self.total_bytes_is_known = True
        else:
            self.total_bytes = 0
            self.total_bytes_is_known = False
        self.counted_urls = set()
        self.current_bytes = 0
        self.percent = 0

        if metadata_only:
            for url, name in urls.items():
                self.download_metadata(url, emit_finish=False)

        else:
            for url, name in urls.items():
                self.download_image(
                    url, name, update_percentage, convert=convert, emit_finish=True
                )
