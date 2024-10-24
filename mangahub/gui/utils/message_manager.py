from PySide6.QtWidgets import (
    QVBoxLayout,
    QFrame,
    QLabel
)
from PySide6.QtCore import (
    Qt, QRect, QTimer,
    QPropertyAnimation, QEasingCurve
)


class Message(QFrame):
    def __init__(self, parent=None, message_type='error', message=None, width=250, min_height=40):
        super().__init__(parent)
        self.setStyleSheet(self._get_style(message_type))
        # self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.SubWindow)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFixedWidth(width)
        self.setMinimumHeight(min_height)

        self.label = QLabel(f"{message_type.capitalize()}: {message}")
        self.label.setStyleSheet("border: none; background-color: transparent;")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        root_layout = QVBoxLayout()
        root_layout.addWidget(self.label)

        self.setLayout(root_layout)
        self.adjust_height()

    def adjust_height(self):
        label_height = self.label.sizeHint().height()
        min_height = 40
        self.setFixedHeight(max(min_height, label_height + 20))

    def _get_style(self, message_type):
        styles = {
            'error': """
                border: 1px solid #ffebee;
                background-color: rgba(244, 67, 54, 0.9);
                color: #f8f8f8;
                border-radius: 4px;
                """,  # Red background with light red border
            'info': """
                border: 1px solid #bbdefb;
                background-color: rgba(33, 150, 243, 0.9);
                color: #f8f8f8;
                border-radius: 4px;
                """,  # Blue background with light blue border
            'success': """
                border: 1px solid #e8f5e9;
                background-color: rgba(76, 175, 80, 0.9);
                color: #f8f8f8;
                border-radius: 4px;
                """,  # Green background with light green border
            'warning': """
                border: 1px solid #fff3e0;
                background-color: rgba(255, 152, 0, 0.9);
                color: #f8f8f8;
                border-radius: 4px;
                """,  # Orange background with light orange border
        }
        return styles.get(message_type, """
            border: 1px solid #cccccc;
            background-color: rgba(128, 128, 128, 0.9);
            color: #f8f8f8;
            border-radius: 4px;
            """)  # Default gray message
        

class MessageManager:
    _instance = None
    
    @staticmethod
    def get_instance():
        if MessageManager._instance is None:
            raise Exception("MessageManager has not been initialized!")
        return MessageManager._instance
    
    def __init__(self, app, width=250):
        if MessageManager._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            MessageManager._instance = self
            
        self.app = app
        self.window = app.gui_window
        
        self.width = width
        self.min_height = 40
        self.x = self.window.width() - self.width - 10
        
        self.active_messages = []
        self.move_anim_group = {}
        self.destroy_anim_group = {}

    def show_message(self, message_type='error', message_text=None, duration=3000):
        message = Message(self.window, message_type, message_text, self.width, self.min_height)
        message.setGeometry(self.x, self.window.height(), message.width(), message.height())
        message.show()

        self.active_messages.append(message)
        self.move_messages()

        QTimer.singleShot(duration, lambda: self.destroy_message(message))

    def destroy_message(self, message):
        if message in self.active_messages:
            if message in self.move_anim_group:
                self.move_anim_group.pop(message).stop()

            animation = QPropertyAnimation(message, b"geometry")
            animation.setDuration(150)
            animation.setEasingCurve(QEasingCurve.Type.InBack)
            animation.setStartValue(message.geometry())
            animation.setEndValue(QRect(self.x + self.width + 10, message.geometry().y(), message.width(), message.height()))
            animation.finished.connect(lambda: self._destroy_message(message))

            self.active_messages.remove(message)
            self.destroy_anim_group[message] = animation
            animation.start()

    def _destroy_message(self, message):
        message.deleteLater()
        self.move_messages()
        self.destroy_anim_group.pop(message).stop()

    def move_messages(self, time=150):
        y = self.window.height() - 5
        for message in reversed(self.active_messages):  # Recent at the bottom
            y -= message.height() + 5
            animation = QPropertyAnimation(message, b"geometry")
            animation.setDuration(time)
            animation.setStartValue(message.geometry())
            animation.setEndValue(QRect(self.x, y, message.width(), message.height()))
            self.move_anim_group[message] = animation
            animation.start()
            
    def pos_update(self):
        self.x = self.window.width() - self.width - 10      
        self.move_messages(0)  
        
        