from PySide6.QtCore import Qt, QEasingCurve, QPropertyAnimation
from config import Config


class SmoothScrollMixin:
    def init_smooth_scroll(self, vertical=True):
        """Initialize smooth scrolling - call this in __init__"""
        self.scroll_bar = (
            self.verticalScrollBar() if vertical else self.horizontalScrollBar()
        )

        # Scroll state tracking
        self._prev_delta = 0
        self._accumulated_scroll = 0
        self._dscroll_amount = 0
        self._scroll_animation_running = False

        # Configurable parameters
        self.scale_multiplier = Config.UI.Scrolling.scale_multiplier()
        self.step_size = Config.UI.Scrolling.step()
        self.scroll_duration = Config.UI.Scrolling.step_duration()
        self.alt_multiplier = Config.UI.Scrolling.alt_multiplier()

        self._scroll_animation = QPropertyAnimation(self.scroll_bar, b"value")
        self._scroll_animation.setDuration(self.scroll_duration)
        self._scroll_animation.setEasingCurve(QEasingCurve.Type.OutQuad)

    def wheelEvent(self, event):
        modifiers = event.modifiers()
        if modifiers & Qt.KeyboardModifier.AltModifier:  # Use == instead of &
            step_size = self.step_size * self.alt_multiplier
            delta = event.angleDelta().x()
        elif (
            modifiers & Qt.KeyboardModifier.ShiftModifier
        ):  # Keep & for Shift since it works
            step_size = self.step_size * self.alt_multiplier
            delta = event.angleDelta().y()
        else:
            delta = event.angleDelta().y()
            step_size = self.step_size
        scroll_amount = round(
            -delta / 120 * step_size * self.scale_multiplier
        )  # Float error

        # Reset or accumulate scroll based on direction change
        if self._prev_delta != delta:
            self._accumulated_scroll = 0
        self._accumulated_scroll += scroll_amount

        current_value = self.scroll_bar.value()
        dcurrent_value = (
            current_value % scroll_amount
        )  # Snapping to nearest step (current value is any number, while accumulated scroll is fixed to steps)
        target_value = current_value + self._accumulated_scroll - dcurrent_value

        # Ensure target is within bounds
        max_value = self.scroll_bar.maximum()
        min_value = self.scroll_bar.minimum()
        target_value = max(min_value, min(max_value, target_value))

        self._scroll_animation.stop()

        # If running, restart animation from current value
        if self._scroll_animation_running:
            self._scroll_animation.setStartValue(self._scroll_animation.currentValue())
        else:
            self._scroll_animation.setStartValue(current_value)

        self._scroll_animation.setEndValue(target_value)
        self._scroll_animation.start()

        self._scroll_animation_running = True
        self._scroll_animation.finished.connect(self.on_animation_finished)

        self._prev_delta = delta
        event.accept()

    def on_animation_finished(self):
        self._accumulated_scroll = 0
        self._scroll_animation_running = False
