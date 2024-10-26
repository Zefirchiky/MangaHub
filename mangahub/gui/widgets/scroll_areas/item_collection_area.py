from .smooth_scroll_area import SmoothScrollArea


class ItemCollectionArea(SmoothScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Custom initialization for item collection
        self.step_size = 80  # Customize scroll step
        self.scroll_duration = 150  # Customize animation duration