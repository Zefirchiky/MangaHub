from __future__ import annotations
from enum import Enum, auto

from app_status import AppStatus
from loguru import logger
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QRect, Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QWidget,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QProgressBar,
)


class MessageType(Enum):
    INFO = auto()
    SUCCESS = auto()
    WARNING = auto()
    ERROR = auto()


class Message(QFrame):
    clicked = Signal(QFrame)

    def __init__(
        self,
        parent=None,
        message_type=MessageType.ERROR,
        message=None,
        width=250,
        min_height=40,
        progress=False,
    ):
        super().__init__(parent)
        self.message_type = message_type
        self.style_ = self._get_style(message_type)
        self.setStyleSheet(self._build_style(*self.style_.values()))
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

        self.type_label = QLabel(f"{self.message_type.name}", self)
        self.type_label.setStyleSheet(
            "border: none; background-color: transparent; font-size: 10px;"
        )
        self.type_label.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )
        self.type_label.move(10, 5)

        self.root_layout = QVBoxLayout()
        self.root_layout.setContentsMargins(10, 15, 10, 10)  # Add margins
        self.root_layout.setSpacing(5)
        self.root_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.root_layout.addWidget(self.label)

        self.progress_bar: QProgressBar = None
        if progress:
            self.set_progress_bar(100)

        self.setLayout(self.root_layout)
        self.adjust_height()

    def adjust_height(self):
        label_height = self.label.sizeHint().height()
        height = label_height + 30
        if self.progress_bar:
            height += self.progress_bar.height() + 10
        self.setFixedHeight(max(self.min_height, height))

    def set_progress_bar(
        self, total: int, minimum=0, format_="auto"
    ):  # TODO: Doesn't work properly
        if not format_ == "auto":
            format_ = format_.replace("%t", str(total))
            self.progress_bar.setFormat(format_)

        if not self.progress_bar:
            self.progress_bar = QProgressBar(minimum=minimum, maximum=total)
            self.progress_bar.setFixedWidth(self.width() - 40)
            self.progress_bar.setFixedHeight(12)
            self.progress_bar.setSizePolicy(
                QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
            )
            self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.change_style(self.message_type)

            self.wrapper = QWidget()
            self.wrapper_layout = QHBoxLayout()
            self.wrapper_layout.setContentsMargins(0, 0, 0, 0)
            self.wrapper_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.wrapper_layout.addWidget(self.progress_bar)
            self.wrapper.setObjectName("BarWidget")
            self.wrapper.setStyleSheet(
                "#BarWidget { border: none; background-color: transparent; }"
            )
            self.wrapper.setLayout(self.wrapper_layout)

            self.root_layout.addWidget(self.wrapper)
            self.adjust_height()

        else:
            self.progress_bar.setMaximum(total)
            self.progress_bar.setMinimum(minimum)

        return self.progress_bar

    def _get_style(self, message_type):
        styles = {
            MessageType.INFO: {
                "border": "1px solid #bbdefb",
                "background-color": "rgba(33, 150, 243, 0.9)",
                "color": "#f8f8f8",
                "border-radius": "4px",
            },  # Blue background with light blue border
            MessageType.SUCCESS: {
                "border": "1px solid #e8f5e9",
                "background-color": "rgba(76, 175, 80, 0.9)",
                "color": "#f8f8f8",
                "border-radius": "4px",
            },  # Green background with light green border
            MessageType.WARNING: {
                "border": "1px solid #fff3e0",
                "background-color": "rgba(255, 152, 0, 0.9)",
                "color": "#f8f8f8",
                "border-radius": "4px",
            },  # Orange background with light orange border
            MessageType.ERROR: {
                "border": "1px solid #ffebee",
                "background-color": "rgba(244, 67, 54, 0.9)",
                "color": "#f8f8f8",
                "border-radius": "4px",
            },  # Red background with light red border
        }
        return styles.get(
            message_type,
            {
                "border": "1px solid #cccccc",
                "background-color": "rgba(128, 128, 128, 0.9)",
                "color": "#f8f8f8",
                "border-radius": "4px",
            },
        )  # Default gray message

    def _build_style(self, border: str, bg_color: str, color: str, border_radius: str):
        return (
            f"border: {border};"
            f"background-color: {bg_color};"
            f"color: {color};"
            f"border-radius: {border_radius};"
        )

    def change_style(self, new_style: MessageType):
        self.message_type = new_style
        self.style_ = self._get_style(new_style)
        self.setStyleSheet(self._build_style(*self.style_.values()))
        self.type_label.setText(self.message_type.name)
        if self.progress_bar:
            self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #333; /* Dark background for contrast */
                color: white; /* White text */
                border: 1px solid #555;
                border-radius: 5px;
                text-align: center;
            }}

            QProgressBar::chunk {{
                background-color: {self.style_["background-color"]};
                border-radius: 5px;
            }}
        """)

    def mousePressEvent(self, event):
        self.clicked.emit(self)
        return super().mousePressEvent(event)


class MM:
    """MessageManager class handles the gui messages.

    Use `MM.show_message()` to show a message.

    Use `MM.show_[info | success | warning | error]` to show corresponding messages

    Corresponding `loguru.logger` is called every time a message is showing"""

    _instance: MM | None = None
    _initialized = False
    queue: list[Message] = []
    MessageType = MessageType

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            # Only create a new instance if one doesn't exist and app is provided
            if args or "app" in kwargs:
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

            self.active_messages: list[Message] = []
            self.progress_messages: dict[str, Message] = {}
            self.move_anim_group = {}
            self.destroy_anim_group = {}

            logger.success("MessageManager initialized")

    @classmethod
    def finish_progress(cls, progress_name: str, wait_after=5000):
        print(f'{progress_name} is finished')
        cls._instance._finish_progress(progress_name, wait_after)

    def _finish_progress(self, progress_name: str, wait_after=5000, is_error=False):
        if message := self.progress_messages.get(progress_name):
            QTimer.singleShot(wait_after, lambda: self._destroy_message(message))
            message.change_style(
                MessageType.SUCCESS if not is_error else MessageType.ERROR
            )
        else:
            logger.warning(f"Progress message {progress_name} does not exist")

    @classmethod
    def show_progress(
        cls,
        progress_name: str,
        cur_value: int,
        total: int,
        message_text: str = "",
        format_="auto",
    ):
        return cls._instance._show_progress(
            progress_name, cur_value, total, message_text, format_
        )

    def _show_progress(
        self,
        progress_name: str,
        cur_value: int,
        total: int,
        message_text: str = "",
        format_="auto",
    ):
        if progress_name not in self.progress_messages:
            self.progress_messages[progress_name] = self.show_message(
                message_text, MessageType.INFO, -1, no_logging=True, progress=True
            )
            self.progress_messages[progress_name].set_progress_bar(
                total, format_=format_
            )
        # pbar = self.progress_messages[progress_name].progress_bar
        # pbar.setValue(cur_value)
        # if total != pbar.maximum():
        #     pbar.setMaximum(total)

        return self.progress_messages[progress_name]

    @classmethod
    def show_info(cls, message_text: str = "", duration=5000, progress=False):
        return cls.show_message(message_text, MessageType.INFO, duration, progress)

    @classmethod
    def show_success(cls, message_text: str = "", duration=5000, progress=False):
        return cls.show_message(message_text, MessageType.SUCCESS, duration, progress)

    @classmethod
    def show_warning(cls, message_text: str = "", duration=5000, progress=False):
        return cls.show_message(message_text, MessageType.WARNING, duration, progress)

    @classmethod
    def show_error(cls, message_text: str = "", duration=5000, progress=False):
        return cls.show_message(message_text, MessageType.ERROR, duration, progress)

    @classmethod
    def show_message(
        cls,
        message_text: str = "",
        message_type: MessageType | str = MessageType.ERROR,
        duration=5000,
        progress=False,
        no_logging=False,
    ):
        """Shows a message in the main window.
        If the main window is not initialized yet, the message is queued for later display.
        If the main window is initialized, the message is displayed directly.
        The message type can be one of the values in MessageType or a string that is matched against
        'info', 'i', 'success', 's', 'warning', 'w', 'error', 'e'.
        If the message type is a string, it is matched case-insensitive.
        If progress is True, the message is shown with a progress bar.
        The duration is the time in milliseconds the message is displayed.
        The message text is logged depending on the message type.
        """
        if cls._instance is None:
            raise Exception("MessageManager has not been initialized!")

        if isinstance(message_type, str):
            match message_type.lower():
                case "info" | "i":
                    message_type = MessageType.INFO
                case "success" | "s":
                    message_type = MessageType.INFO
                case "warning" | "w":
                    message_type = MessageType.INFO
                case "error" | "e":
                    message_type = MessageType.INFO

        if not no_logging:
            match message_type:
                case MessageType.INFO:
                    logger.info(message_text)
                case MessageType.SUCCESS:
                    logger.success(message_text)
                case MessageType.WARNING:
                    logger.warning(message_text)
                case MessageType.ERROR:
                    logger.error(message_text)

        if not AppStatus.main_window_initialized:
            cls.queue.append((message_type, message_text, duration, progress))
            return
        else:
            for message in cls.queue:
                cls._instance._show_message(*message)
            cls.queue.clear()
            return cls._instance._show_message(
                message_type, message_text, duration=duration, progress=progress
            )

    def _show_message(
        self,
        message_type=MessageType.ERROR,
        message_text=None,
        duration=5000,
        progress=False,
    ):
        message = Message(
            self.window,
            message_type,
            message_text,
            self.width,
            self.min_height,
            progress=progress,
        )
        message.setGeometry(
            self.x, self.window.height(), message.width(), message.height()
        )
        message.show()

        message.clicked.connect(self.destroy_message)

        self.active_messages.append(message)
        self.move_messages()

        if not duration == -1:
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
            animation.setEndValue(
                QRect(
                    -self.width - 10,
                    message.geometry().y(),
                    message.width(),
                    message.height(),
                )
            )
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
                animation.setEndValue(
                    QRect(self.x, y, message.width(), message.height())
                )
                self.move_anim_group[message] = animation
                animation.start()

    def pos_update(self):
        self.move_messages(0)
