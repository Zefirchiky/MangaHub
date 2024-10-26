from PySide6.QtCore import QPropertyAnimation, QEasingCurve


class SmoothScrollMixin:   
    def init_smooth_scroll(self):
        """Initialize smooth scrolling - call this in __init__"""
        # Scroll state tracking
        self.prev_delta = 0
        self.accumulated_scroll = 0
        self.animation_running = False
        
        # Configurable parameters
        self.scale_multiplier = 1.0
        self.step_size = 100
        self.scroll_duration = 200
        
        self.animation = QPropertyAnimation(self.verticalScrollBar(), b"value")
        self.animation.setDuration(self.scroll_duration)
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)
                
    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        
        # Reset or accumulate scroll based on direction change
        if self.prev_delta != delta:
            self.accumulated_scroll = 0
        
        scroll_amount = -delta / 120 * self.step_size
        self.accumulated_scroll += scroll_amount * self.scale_multiplier
        
        current_value = self.verticalScrollBar().value()
        target_value = current_value + self.accumulated_scroll

        # Ensure target is within bounds
        max_value = self.verticalScrollBar().maximum()
        min_value = self.verticalScrollBar().minimum()
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