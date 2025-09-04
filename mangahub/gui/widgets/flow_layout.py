from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtWidgets import (
    QApplication, QLayout, QLayoutItem, QPushButton, QSizePolicy, 
    QWidget, QVBoxLayout, QHBoxLayout, QLabel
)
import sys


class FlowLayout(QLayout):
    """
    A horizontal-first flow layout that wraps widgets to new rows.
    
    Key concepts explained:
    - QLayout is the base class for all Qt layouts
    - We override key methods to define our custom behavior
    - The layout calculates positions based on available space
    """
    
    def __init__(self, parent: QWidget | None = None, margin: int = -1, h_spacing: int = -1, v_spacing: int = -1):
        super().__init__(parent)
        
        # Store layout items and spacing
        self._item_list: list[QLayoutItem] = []
        self._h_space = h_spacing
        self._v_space = v_spacing
        
        # Set margins if provided
        if margin != -1:
            self.setContentsMargins(margin, margin, margin, margin)
    
    def addItem(self, item: QLayoutItem) -> None:
        """Add a layout item to our flow layout."""
        self._item_list.append(item)
    
    def count(self) -> int:
        """Return the number of items in the layout."""
        return len(self._item_list)
    
    def itemAt(self, index: int) -> QLayoutItem | None:
        """Return the item at the given index, or None if out of bounds."""
        if 0 <= index < len(self._item_list):
            return self._item_list[index]
        return None
    
    def takeAt(self, index: int) -> QLayoutItem | None:
        """Remove and return the item at the given index."""
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)
        return None
    
    def expandingDirections(self) -> Qt.Orientation:
        """
        Tell Qt that this layout doesn't expand in any direction.
        This means it will use its sizeHint() for sizing.
        """
        return Qt.Orientation(0)  # No expansion
    
    def hasHeightForWidth(self) -> bool:
        """
        Return True because our height depends on our width.
        When the width changes, we might need more or fewer rows.
        """
        return True
    
    def heightForWidth(self, width: int) -> int:
        """
        Calculate the required height for a given width.
        This is the core of the flow layout logic.
        """
        height = self._do_layout(QRect(0, 0, width, 0), test_only=True)
        return height
    
    def setGeometry(self, rect: QRect) -> None:
        """
        Actually position all the widgets within the given rectangle.
        This is called by Qt when the layout needs to be updated.
        """
        super().setGeometry(rect)
        self._do_layout(rect, test_only=False)
    
    def sizeHint(self) -> QSize:
        """
        Return the preferred size of this layout.
        We calculate this by laying out in a single row.
        """
        size = QSize()
        for item in self._item_list:
            size = size.expandedTo(item.sizeHint())
        
        # Add margins
        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size
    
    def minimumSize(self) -> QSize:
        """
        Return the minimum size needed for this layout.
        """
        size = QSize()
        for item in self._item_list:
            size = size.expandedTo(item.minimumSize())
        
        # Add margins
        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size
    
    def _horizontal_spacing(self) -> int:
        """Get the horizontal spacing between items."""
        if self._h_space >= 0:
            return self._h_space
        else:
            # Use default spacing from parent widget or style
            return self._smart_spacing(QSizePolicy.PushButton, Qt.Horizontal)
    
    def _vertical_spacing(self) -> int:
        """Get the vertical spacing between rows."""
        if self._v_space >= 0:
            return self._v_space
        else:
            return self._smart_spacing(QSizePolicy.PushButton, Qt.Vertical)
    
    def _smart_spacing(self, pm: QSizePolicy.ControlType, orientation: Qt.Orientation) -> int:
        """
        Get smart spacing from the parent widget's style.
        This provides platform-appropriate spacing.
        """
        parent = self.parent()
        if not parent:
            return -1
        elif parent.isWidgetType():
            return parent.style().layoutSpacing(pm, pm, orientation)
        else:
            return parent.spacing()
    
    def _do_layout(self, rect: QRect, test_only: bool) -> int:
        """
        The core layout algorithm. This is where the magic happens!
        
        Args:
            rect: The rectangle to lay out items within
            test_only: If True, just calculate height; if False, actually position items
        
        Returns:
            The total height needed
        """
        # Get the effective rectangle (accounting for margins)
        margins = self.contentsMargins()
        effective_rect = rect.adjusted(margins.left(), margins.top(), -margins.right(), -margins.bottom())
        
        x = effective_rect.x()
        y = effective_rect.y()
        line_height = 0  # Height of the current row
        
        for item in self._item_list:
            widget = item.widget()
            if not widget:
                continue
            
            # Get spacing
            space_x = self._horizontal_spacing()
            space_y = self._vertical_spacing()
            
            # Calculate next position
            next_x = x + item.sizeHint().width() + space_x
            
            # Check if we need to wrap to next row
            if next_x - space_x > effective_rect.right() and line_height > 0:
                # Move to next row
                x = effective_rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0
            
            # Position the item (only if not test_only)
            if not test_only:
                item.setGeometry(QRect(x, y, item.sizeHint().width(), item.sizeHint().height()))
            
            # Update position for next item
            x = next_x
            line_height = max(line_height, item.sizeHint().height())
        
        # Return total height needed
        return y + line_height - rect.y() + margins.bottom()