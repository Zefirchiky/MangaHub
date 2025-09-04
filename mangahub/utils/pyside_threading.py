import traceback
from enum import Enum, auto
from typing import Callable

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot

class WorkerStatus(Enum):
    PROCESSING = auto()
    SUCCESS = auto()
    ERROR = auto()

class WorkerSignals(QObject):
    progress = Signal(int)
    finished = Signal(str)
    success = Signal(str, object)
    error = Signal(str, tuple)
    status = Signal(str, object)
    

class Worker(QRunnable):
    def __init__(self, name: str, fn, *args, **kwargs):
        super().__init__()
        self.name = name
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        
    @Slot()
    def run(self):
        try:
            self.signals.status.emit(self.name, WorkerStatus.PROCESSING)
            self.signals.success.emit(self.name, self.fn(*self.args, **self.kwargs))
            self.signals.status.emit(self.name, WorkerStatus.SUCCESS)
        except Exception as e:
            self.signals.error.emit(self.name, (type(e), str(e), traceback.format_exc()))
            self.signals.status.emit(self.name, WorkerStatus.ERROR)
        finally:
            self.signals.finished.emit(self.name)
            
            
class ThreadingManager(QObject):
    thread_pool = QThreadPool()
    workers: dict[str, QRunnable] = {}
    
    @classmethod
    def run(cls, fn: Callable, *args, name=None, **kwargs):
        name = name or f'worker_{len(cls.workers)}_{fn.__name__}'
        worker = Worker(
            name, fn, *args, **kwargs
        )
        worker.setAutoDelete(True)
        cls.thread_pool.start(worker)
        return worker

    @classmethod
    def run_worker(cls, worker: QRunnable, name=None):
        name = name or f'worker_{len(cls.workers)}_{worker.__class__.__name__}'
        worker.setAutoDelete(True)
        cls.thread_pool.start(worker)
        return worker
        
    @classmethod
    def run_bunch(cls, fn, *args, name, max_threads=1, **kwargs):
        ...