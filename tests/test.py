from typing import Callable, Optional, List, Any, Tuple
import traceback

from PySide6.QtCore import QRunnable, Slot, Signal, QObject, QThreadPool, QEventLoop

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
    def __init__(self, 
                 num: int, 
                 fn: Callable, 
                 *args, 
                 progress_callback: bool = False, 
                 status_callback: bool = False, 
                 **kwargs):

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
            self.signals.result.emit((self.num, result))
        except Exception as e:
            self.signals.error.emit((type(e), str(e), traceback.format_exc()))
        finally:
            self.signals.finished.emit()


class BatchWorker(QObject):
    def __init__(self):
        super().__init__()
        self.threadpool = QThreadPool.globalInstance()
        self.signals = BatchWorkerSignals()
        self._workers = []
        self._results = []
        self.processed_items = 0

    def process_batch(
        self,
        fn: Callable,
        items: List[Any],
        *args,
        blocking: bool = True,
        progress_workers_callback: Optional[Callable[[int], None]] = None,
        status_workers_callback: Optional[Callable[[str], None]] = None,
        **kwargs
    ) -> List[Any]:

        self._results = [None] * len(items)
        loop = QEventLoop() if blocking else None
        
        for item in items:
            worker = Worker(
                fn,
                item,
                *args,
                progress_callback=bool(progress_workers_callback),
                status_callback=bool(status_workers_callback),
                **kwargs
            )
            worker.signals.result.connect(self._handle_result)
            worker.signals.error.connect(self._handle_error)
            
            if progress_workers_callback:
                worker.signals.progress.connect(progress_workers_callback)
            if status_workers_callback:
                worker.signals.status.connect(status_workers_callback)
        
        if blocking:
            loop.exec_()
            return self._results
        return []

    def _handle_result(self, result: Tuple[int, Any]):
        num, value = result
        self._results[num] = value
        self.processed_items += 1
        self.signals.item_completed.emit((num, value))
        self.signals.progress.emit(int((self.processed_items / len(self._results)) * 100))
        
        if self.processed_items == len(self._results):
            self.signals.all_completed.emit(self._results)

    def _handle_error(self, error: Tuple[type, str, str]):
        self.signals.error.emit(error)
        self.signals.status.emit(f"Error occurred: {error[1]}")

    def cancel(self):
        self._workers.clear()
        self._results.clear()
        self.signals.status.emit("Operation cancelled")
