from __future__ import annotations
from enum import Enum, auto

from app_status import AppStatus
from loguru import logger
from PySide6.QtCore import (QEasingCurve, QPropertyAnimation, QRect, Qt,
                            QTimer, Signal)
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy


class MessageType(Enum):
    INFO = auto()
    SUCCESS = auto()
    WARNING = auto()
    ERROR = auto()

class Message(QFrame):
    clicked = Signal(QFrame)
    
    def __init__(self, parent=None, message_type=MessageType.ERROR, message=None, width=250, min_height=40):
        super().__init__(parent)
        self.setStyleSheet(self._get_style(message_type))
        self.setFixedWidth(width)
        self.setMinimumHeight(min_height)
        
        self.min_height = min_height
        
        self.label = QLabel(f"{message}")
        self.label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.label.setStyleSheet("border: none; background-color: transparent;")
        self.label.setFixedWidth(width - 20)
        self.label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        
        self.type_label = QLabel(f"{message_type.name}", self)
        self.type_label.setStyleSheet("border: none; background-color: transparent; font-size: 10px;")
        self.type_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.type_label.move(10, 5)

        root_layout = QHBoxLayout()
        root_layout.addWidget(self.label)

        self.setLayout(root_layout)
        self.adjust_height()
        
    def adjust_height(self):
        label_height = self.label.sizeHint().height()
        self.setFixedHeight(max(self.min_height, label_height + 30))

    def _get_style(self, message_type):
        styles = {
            MessageType.ERROR: """
                border: 1px solid #ffebee;
                background-color: rgba(244, 67, 54, 0.9);
                color: #f8f8f8;
                border-radius: 4px;
                """,  # Red background with light red border
            MessageType.INFO: """
                border: 1px solid #bbdefb;
                background-color: rgba(33, 150, 243, 0.9);
                color: #f8f8f8;
                border-radius: 4px;
                """,  # Blue background with light blue border
            MessageType.SUCCESS: """
                border: 1px solid #e8f5e9;
                background-color: rgba(76, 175, 80, 0.9);
                color: #f8f8f8;
                border-radius: 4px;
                """,  # Green background with light green border
            MessageType.WARNING: """
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
        
    def mousePressEvent(self, event):
        self.clicked.emit(self)
        return super().mousePressEvent(event)
        

class MM:
    """MessageManager class handles the gui messages.
    Use MM.show_message() to show a message."""
    _instance: MM | None = None
    _initialized = False
    queue: list[Message] = []
    MessageType = MessageType
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            # Only create a new instance if one doesn't exist and app is provided
            if args or 'app' in kwargs:
                cls._instance = super().__new__(cls)
            else:
                raise Exception("First MM instantiation requires 'app' parameter!")
        return cls._instance
    
    def __init__(self, app=None, width=400):
        # Only initialize if this is a new instance
        if not self._initialized:
            self._initialized = True
            self.app = app
            self.window = app.gui_window
            
            self.width = width
            self.min_height = 40
            self.x = 10
            
            self.active_messages = []
            self.move_anim_group = {}
            self.destroy_anim_group = {}

            logger.success("MessageManager initialized")
    
    @classmethod
    def show_message(cls, message_type: MessageType=MessageType.ERROR, message_text=None, duration=5000, progress=False):
        if cls._instance is None:
            raise Exception("MessageManager has not been initialized!")
        if not AppStatus.main_window_initialized:
            cls.queue.append((message_type, message_text, progress, duration))
            return 
        else:
            for message in cls.queue:
                cls._instance._show_message(*message)
            cls.queue.clear()
            return cls._instance._show_message(message_type, message_text, duration=duration)
    
    def _show_message(self, message_type=MessageType.ERROR, message_text=None, duration=5000, progress=False):
        message = Message(self.window, message_type, message_text, self.width, self.min_height)
        message.setGeometry(self.x, self.window.height(), message.width(), message.height())
        message.show()
        
        message.clicked.connect(self.destroy_message)

        self.active_messages.append(message)
        self.move_messages()
        
        QTimer.singleShot(duration, lambda: self.destroy_message(message))
        
        return message

    def destroy_message(self, message: Message):
        if message in self.active_messages:
            if message in self.move_anim_group:
                self.move_anim_group.pop(message).stop()

            animation = QPropertyAnimation(message, b"geometry")
            animation.setDuration(150)
            animation.setEasingCurve(QEasingCurve.Type.InBack)
            animation.setStartValue(message.geometry())
            animation.setEndValue(QRect(-self.width - 10, message.geometry().y(), message.width(), message.height()))
            animation.finished.connect(lambda: self._destroy_message(message))

            self.active_messages.remove(message)
            self.destroy_anim_group[message] = animation
            animation.start()

    def _destroy_message(self, message):
        if message in self.active_messages:
            self.active_messages.remove(message)
        if message in self.destroy_anim_group:
            self.destroy_anim_group[message].stop()
            self.destroy_anim_group.pop(message)
        message.deleteLater()
        self.move_messages()

    def move_messages(self, time=150):
        y = self.window.height() - 5
        for message in reversed(self.active_messages):  # Recent at the bottom
            if message:
                y -= message.height() + 5
                animation = QPropertyAnimation(message, b"geometry")
                animation.setDuration(time)
                animation.setStartValue(message.geometry())
                animation.setEndValue(QRect(self.x, y, message.width(), message.height()))
                self.move_anim_group[message] = animation
                animation.start()
            
    def pos_update(self):
        self.move_messages(0)  
        
        