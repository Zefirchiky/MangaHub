from PySide6.QtGui import QFocusEvent
from PySide6.QtWidgets import QMainWindow


class SettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Settings")

        self.resize(800, 500)

    def focusOutEvent(self, event: QFocusEvent) -> None:
        self.close()
        return super().focusOutEvent(event)