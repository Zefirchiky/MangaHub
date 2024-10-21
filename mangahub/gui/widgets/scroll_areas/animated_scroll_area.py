from PySide6.QtWidgets import (
    QScrollArea
)
from PySide6.QtCore import (
    QPropertyAnimation, QEasingCurve
)


class AnimatedScrollArea(QScrollArea):
    def __init__(self, parent=None, step_size=40, duration=100):
        super().__init__(parent)
        self.verticalScrollBar().setSingleStep(step_size)

        self.step_size = step_size
        self.duration = duration

        self.prev_delta = 0
        self.accumulated_scroll = 0
        self.animation_running = False

        self.animation = QPropertyAnimation(self.verticalScrollBar(), b"value")
        self.animation.setDuration(duration)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def scrollEvent(self, event):
        delta = event.angleDelta().y()

        # If scroll is opposite, stop the animation
        if not self.prev_delta == delta:
            self.accumulated_scroll = 0
        else:
            self.accumulated_scroll += -delta / 120 * self.step_size

        target_value = self.verticalScrollBar().value() + self.accumulated_scroll

        # If the animation is already running, update the end value smoothly
        self.animation.stop()
        if self.animation_running:
            self.animation.setStartValue(self.animation.currentValue())
        else:
            self.animation.setStartValue(self.verticalScrollBar().value())
        self.animation.setEndValue(target_value)
        self.animation.start()

        self.animation_running = True
        self.animation.finished.connect(self.on_animation_finished)

        self.prev_delta = delta
        
        event.accept()

    def on_animation_finished(self):
        self.accumulated_scroll = 0
        self.animation_running = False