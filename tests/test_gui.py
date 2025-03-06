from PySide6.QtWidgets import QWidget, QScrollArea, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy, QWidgetItem, QLayout
from PySide6.QtCore import Qt, QSize, QRect, QPoint

class MediaCard(QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setMinimumSize(150, 200)  # Set minimum size for the card
        
        layout = QVBoxLayout(self)
        label = QLabel(title)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        # Style the card
        self.setStyleSheet("""
            background-color: #f0f0f0;
            border-radius: 8px;
            margin: 0px;
        """)

class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=10, spacing=10):
        super().__init__(parent)
        self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)
        self._items = []
        print(self.spacing())

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientations(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._doLayout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        
        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def _doLayout(self, rect, testOnly):
        # Get the margins
        margins = self.contentsMargins()
        
        # Effective rectangle accounting for margins
        effectiveRect = rect.adjusted(
            margins.left(), 
            margins.top(), 
            -margins.right(), 
            -margins.bottom()
        )
        
        x = effectiveRect.x()
        y = effectiveRect.y()
        lineHeight = 0
        spacing = self.spacing()
        
        for item in self._items:
            # Get the width and height of this item
            itemWidth = item.sizeHint().width()
            itemHeight = item.sizeHint().height()
            
            # Check if we need to move to the next row
            nextX = x + itemWidth
            if nextX > effectiveRect.right() + 1 and lineHeight > 0:
                x = effectiveRect.x()
                y = y + lineHeight + spacing
                nextX = x + itemWidth
                lineHeight = 0
            
            # Position the item if not just testing
            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            
            # Update position and line height
            x = nextX + spacing
            lineHeight = max(lineHeight, itemHeight)
        
        # Return the overall height of the layout
        return y + lineHeight - rect.y() + margins.bottom()

class Dashboard(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        
        # Create a container widget and set it as the scroll area's widget
        container = QWidget()
        self.setWidget(container)
        
        # Use the custom FlowLayout for the container
        self.flowLayout = FlowLayout(container, margin=20, spacing=0)
        container.setLayout(self.flowLayout)
        
        # Set vertical scrollbar policy
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    
    def addMediaCard(self, card):
        self.flowLayout.addItem(QWidgetItem(card))
        card.setParent(self.widget())
        
        
from PySide6.QtWidgets import QApplication, QMainWindow
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Media Dashboard")
        self.resize(800, 600)
        
        # Create the dashboard
        self.dashboard = Dashboard()
        self.setCentralWidget(self.dashboard)
        
        # Add some media cards
        for i in range(13):
            card = MediaCard(f"Media {i+1}")
            self.dashboard.addMediaCard(card)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())