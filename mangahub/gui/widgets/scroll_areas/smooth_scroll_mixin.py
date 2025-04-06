from PySide6.QtCore import Qt, QEasingCurve, QPropertyAnimation


class SmoothScrollMixin:   
    def init_smooth_scroll(self, vertical=True):
        """Initialize smooth scrolling - call this in __init__"""
        self.scroll_bar = self.verticalScrollBar() if vertical else self.horizontalScrollBar()
        
        # Scroll state tracking
        self.prev_delta = 0
        self.accumulated_scroll = 0
        self.dscroll_amount = 0
        self.animation_running = False
        
        # Configurable parameters
        self.scale_multiplier = 1.0
        self.step_size = 150
        self.scroll_duration = 200
        self.alt_multiplier = 8
        
        self.animation = QPropertyAnimation(self.scroll_bar, b"value")
        self.animation.setDuration(self.scroll_duration)
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)
                
    def wheelEvent(self, event):
        modifiers = event.modifiers()
        if modifiers & Qt.KeyboardModifier.AltModifier:  # Use == instead of &
            step_size = self.step_size * self.alt_multiplier
            delta = event.angleDelta().x()
        elif modifiers & Qt.KeyboardModifier.ShiftModifier:  # Keep & for Shift since it works
            step_size = self.step_size * self.alt_multiplier
            delta = event.angleDelta().y()
        else:
            delta = event.angleDelta().y()
            step_size = self.step_size
        scroll_amount = round(-delta / 120 * step_size * self.scale_multiplier)    # Float error
        
        # Reset or accumulate scroll based on direction change
        if self.prev_delta != delta:
            self.accumulated_scroll = 0
        self.accumulated_scroll += scroll_amount
        
        current_value = self.scroll_bar.value()
        dcurrent_value = current_value % scroll_amount  # Snapping to nearest step (current value is any number, while accumulated scroll is fixed to steps)
        target_value = current_value + self.accumulated_scroll - dcurrent_value

        # Ensure target is within bounds
        max_value = self.scroll_bar.maximum()
        min_value = self.scroll_bar.minimum()
        target_value = max(min_value, min(max_value, target_value))

        self.animation.stop()
        
        # If running, restart animation from current value
        if self.animation_running:
            self.animation.setStartValue(self.animation.currentValue())
        else:
            self.animation.setStartValue(current_value)
            
        self.animation.setEndValue(target_value)
        self.animation.start()

        self.animation_running = True
        self.animation.finished.connect(self.on_animation_finished)
        
        self.prev_delta = delta
        event.accept()

    def on_animation_finished(self):
        self.accumulated_scroll = 0
        self.animation_running = False