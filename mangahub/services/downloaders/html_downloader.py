import asyncio
import httpx
from PySide6.QtCore import QObject, Signal, Slot, QRunnable, QThreadPool

from loguru import logger
from utils.patterns import Singleton


class HtmlDownloaderWorkerSignals(QObject):
    finished = Signal(str, str)     # url, content
    error = Signal(str, str)        # url, error

class HtmlDownloaderWorker(QRunnable):
    signals = HtmlDownloaderWorkerSignals()
    
    def __init__(self, url):
        super().__init__()
        self.url = url
        
    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(self._download_html())
        if result.status_code != 200:
            logger.warning(f'Url {self.url} responded with code {result.status_code}')
            self.signals.error.emit(self.url, f'Url {self.url} responded with code {result.status_code}')
        else:
            logger.success(f'Url {self.url} got successfully. Final url: {result.url}')
            self.signals.finished.emit(self.url, result.text)
        
        loop.close()
        
    async def _download_html(self):
        with httpx.Client(follow_redirects=True) as client:
            return client.get(self.url)
        
class HtmlDownloaderSignals(QObject):
    downloaded = Signal(str, str)                               # url, content
    all_downloaded = Signal()

class HtmlDownloader(Singleton):
    signals = HtmlDownloaderSignals()
    worker_finished = HtmlDownloaderWorker.signals.finished     # url, content
    error = HtmlDownloaderWorker.signals.error                  # url, error
    
    def __init__(self):
        super().__init__()
        self.pool = QThreadPool()
        self.workers: dict[str, QRunnable] = {}
        
        self.worker_finished.connect(self._worker_finished)
    
    @Slot(str, str)
    def _worker_finished(self, url, result):
        self.signals.downloaded.emit(url, result)
        self.workers.pop(url)
        if not self.workers:
            self.signals.all_downloaded.emit()
    
    def download_html(self, url: str) -> HtmlDownloaderWorker:
        if url in self.workers:
            return self.workers[url]
        
        worker = HtmlDownloaderWorker(url)
        self.workers[url] = worker
        self.pool.start(worker)
        return worker
    
    def download_htmls(self, urls: list[str]) -> dict[str, QRunnable]:
        for url in urls:
            self.download_html(url)
        return self.workers