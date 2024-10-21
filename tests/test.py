from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QScrollArea, QScrollBar
from PySide6.QtCore import QPropertyAnimation, Qt, QEasingCurve

class AnimatedScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.prev_delta = 0
        self.animation = QPropertyAnimation(self.verticalScrollBar(), b"value")
        self.animation.setDuration(100)  # Set animation duration
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)  # Smooth easing curve
        self.accumulated_scroll = 0  # Store accumulated scroll value for smoother transitions
        self.animation_running = False

    def wheelEvent(self, event):
        # Calculate the delta based on the scroll direction
        delta = event.angleDelta().y()
        step = self.verticalScrollBar().singleStep()  # Scroll step size
        
        # Adjust the accumulated scroll value
        if not self.prev_delta == delta:
            self.accumulated_scroll = 0
        else:
            self.accumulated_scroll += -delta / 120 * step
        
        # Set up the target value based on the accumulated scroll
        target_value = self.verticalScrollBar().value() + self.accumulated_scroll

        # If the animation is already running, update the end value smoothly
        self.animation.stop()  # Stop any previous animation
        if self.animation_running:
            self.animation.setStartValue(self.animation.currentValue())
        else:
            self.animation.setStartValue(self.verticalScrollBar().value())
        self.animation.setEndValue(target_value)
        self.animation.start()

        # Set a flag to indicate that the animation is running
        self.animation_running = True
        self.animation.finished.connect(self.on_animation_finished)

        self.prev_delta = delta
        
        # Prevent the default scrolling behavior
        event.accept()

    def on_animation_finished(self):
        # Reset the accumulated scroll value and stop the animation flag
        self.accumulated_scroll = 0
        self.animation_running = False

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Create a layout and add widgets to demonstrate scrolling
        layout = QVBoxLayout()
        for i in range(50):  # Add multiple labels to fill the scroll area
            label = QLabel(f"Item {i}")
            layout.addWidget(label)

        # Create a widget to hold the layout and add it to the QScrollArea
        content_widget = QWidget()
        content_widget.setLayout(layout)

        # Create an animated scroll area and set the content widget
        scroll_area = AnimatedScrollArea()
        scroll_area.setWidget(content_widget)
        scroll_area.setWidgetResizable(True)

        # Set the layout for the main window
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

if __name__ == "__main__":
    app = QApplication([])

    window = MainWindow()
    window.show()

    app.exec()
