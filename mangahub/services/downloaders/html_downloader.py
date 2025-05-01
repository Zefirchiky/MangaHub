import asyncio
import httpx
from PySide6.QtCore import QObject, Signal, QRunnable, QThreadPool

from loguru import logger

class HtmlDownloaderWorkerSignals(QObject):
    finished = Signal(str, str)    # url, content

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
        else:
            logger.success(f'Url {self.url} got successfully')
            self.signals.finished.emit(self.url, result.text)
        
        loop.close()
        
    async def _download_html(self):
        with httpx.Client() as client:
            return client.get(self.url)
        
        
class HtmlDownloader:
    finished = HtmlDownloaderWorker.signals.finished    # url, content
    
    def __init__(self):
        self.pool = QThreadPool()
        self.workers: dict[str, QRunnable] = {}
        
        self.finished.connect(self._worker_finished)
    
    def _worker_finished(self, url, result):
        self.workers.pop(url)
    
    def get_html(self, url: str) -> HtmlDownloaderWorker:
        worker = HtmlDownloaderWorker(url)
        self.workers[url] = worker
        self.pool.start(worker)
        return worker
    
    def get_htmls(self, urls: list[str]) -> dict[str, QRunnable]:
        for url in urls:
            self.get_html(url)
        return self.workers