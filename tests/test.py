from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QWidget, QMainWindow, QApplication
from PySide6.QtCore import QTimer, QRunnable, Slot, Signal, QObject, QThreadPool

import sys
import time
import traceback


class WorkerSignals(QObject):
    status = Signal(str)
    progress = Signal(int)
    finished = Signal()
    result = Signal(object)
    error = Signal(tuple)

class Worker(QRunnable):
    def __init__(self, fn, *args, progress_callback=False, status_callback=False, **kwargs):
        
        super().__init__()
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
            self.signals.error.emit(e)
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()            

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.threadpool = QThreadPool()
        print(f"Multithreading with maximum {self.threadpool.maxThreadCount()}")

        self.button = QPushButton("Start")
        self.button.pressed.connect(self.button_pressed)
        self.setCentralWidget(self.button)
        
    def task(self, progress_callback):
        time.sleep(1)
        progress_callback.emit(50)
        print("hello")
        time.sleep(3)
        progress_callback.emit(100)
        return("Lol")
        
    def button_pressed(self):
        worker = Worker(self.task, progress_callback=True)
        worker.signals.result.connect(print)
        worker.signals.error.connect(print)
        worker.signals.finished.connect(lambda: print("finished"))
        worker.signals.progress.connect(print)
        
        self.threadpool.start(worker)
    
    
app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()