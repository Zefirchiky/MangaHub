import traceback
from typing import Any, Callable, List, Optional, Tuple

from loguru import logger
from PySide6.QtCore import (QEventLoop, QObject, QRunnable, QThreadPool,
                            Signal, Slot)


class WorkerSignals(QObject):
    progress = Signal(int)
    finished = Signal()
    result = Signal(object)
    error = Signal(tuple)
    status = Signal(str)

class BatchWorkerSignals(QObject):
    item_completed = Signal(object)
    all_completed = Signal(list)
    progress = Signal(int)
    error = Signal(tuple)
    status = Signal(str)

class Worker(QRunnable):
    def __init__(
        self,
        num: int,
        fn: Callable,
        *args,
        progress_callback: bool=False, 
        status_callback: bool=False, 
        **kwargs
    ):
        
        super().__init__()
        self.num = num
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        
        if progress_callback:
            self.kwargs["progress_callback"] = self.signals.progress
        if status_callback:
            self.kwargs["status_callback"] = self.signals.status
        
    @Slot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception as e:
            self.signals.error.emit((type(e), str(e), traceback.format_exc()))
        else:
            self.signals.result.emit((self.num, result))
        finally:
            self.signals.finished.emit()
            
class BatchWorker(QObject):
    def __init__(self):
        super().__init__()
        self.threadpool = QThreadPool().globalInstance()
        self.signals = BatchWorkerSignals()
        self._workers = []
        self._results = []
        
    def process_batch(
        self,
        fn: Callable,
        items: List[Any],
        *args,
        blocking: bool = True,
        progress_workers_callback: Optional[Callable[[int], None]] = None,
        status__workers_callback: Optional[Callable[[str], None]] = None,
        **kwargs
    ) -> List[Any]:
        
        fn_name = fn.__qualname__
        
        self._results = [None for _ in range(len(items))]
        self._workers = []
        total_items = len(items)
        self.processed_items = 0
        
        loop = QEventLoop() if blocking else None
        
        def handle_result(result):
            num, result = result
            self.processed_items += 1
            self._results[num] = result
            self.signals.item_completed.emit((num, result))
            self.signals.progress.emit(int(self.processed_items / total_items * 100))
            
            # Check if all items are processed
            if self.processed_items >= total_items:
                self.signals.all_completed.emit(self._results)
                if loop:
                    loop.quit()
                logger.success(f"Batch processing completed: {fn_name} - [{items[0]} - {len(items)}]")
                return self._results
        
        for i, item in enumerate(items):
            worker = Worker(
                i,
                fn,
                item,
                *args,
                progress_callback=bool(progress_workers_callback),
                status_callback=bool(status__workers_callback),
                **kwargs
            )
            worker.signals.result.connect(handle_result)
            worker.signals.error.connect(self._handle_error)
            
            if progress_workers_callback:
                worker.signals.progress.connect(progress_workers_callback)
            if status__workers_callback:
                worker.signals.status.connect(status__workers_callback)
            
            self._workers.append(worker)
            self.threadpool.start(worker)
            
        if blocking:
            loop.exec()     # type: ignore
            return self._results
            
        return []
    
    def _handle_error(self, error: Tuple[type, str, str]):
        self.signals.error.emit(error)
        self.signals.status.emit(f"Error occurred: {error[1]}")
        logger.error(f"Error occurred: {error[1]}")
    
    def cancel(self):
        self._workers.clear()
        self._results.clear()
        self.signals.status.emit("Operation cancelled")