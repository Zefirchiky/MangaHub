from PySide6.QtWidgets import QLayout
from PySide6.QtCore import Qt, QSize, QRect, QPoint


class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)
        self._items = []

    def addItem(self, item) -> None:    # Basic for QLayout
        self._items.append(item)

    def count(self) -> int:    # Basic for QLayout
        return len(self._items)

    def itemAt(self, index):    # Basic for QLayout, to get item at index
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index):    # Basic for QLayout, to take item at index
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self):      # Doesn't expand by default
        return Qt.Orientations(0)

    def hasHeightForWidth(self):    # Height depends on width
        return True

    def heightForWidth(self, width):    # Calculates height for given width
        height = self._doLayout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):  # No fucking clue how that works
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        
        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def _doLayout(self, rect, testOnly):
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
            itemWidth = item.sizeHint().width()
            itemHeight = item.sizeHint().height()
            
            nextX = x + itemWidth
            if nextX > effectiveRect.right() + 1 and lineHeight > 0:    # If next item is out of bounds
                x = effectiveRect.x()    # Reset x
                y = y + lineHeight + spacing   # Move y to next line, by the biggest height
                nextX = x + itemWidth
                lineHeight = 0
            
            if not testOnly:    # Only returns height
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            
            # Update position and line height
            x = nextX + spacing
            lineHeight = max(lineHeight, itemHeight)
        
        # Return the overall height of the layout
        return y + lineHeight - rect.y() + margins.bottom()