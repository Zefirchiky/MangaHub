from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QApplication
from PySide6.QtCore import Qt, QPointF
import sys

class ZoomableGraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self._zoom_factor = 1.15  # How much to zoom per step
        self._current_zoom = 1.0   # Track current zoom level
        self._zoom_min = 0.05      # Minimum zoom limit (5%)
        self._zoom_max = 20.0      # Maximum zoom limit (2000%)

    def wheelEvent(self, event):
        """Zoom in or out using the mouse wheel, centered around the mouse position."""
        # Get the position of the mouse in the view's coordinate system
        mouse_view_pos = event.position()
        # Map the mouse position to the scene's coordinate system
        mouse_scene_pos = self.mapToScene(mouse_view_pos.toPoint())

        # Determine whether we're zooming in or out
        if event.angleDelta().y() > 0:  # Zoom in
            zoom_factor = self._zoom_factor
        else:  # Zoom out
            zoom_factor = 1 / self._zoom_factor

        # Calculate the new zoom level
        new_zoom = self._current_zoom * zoom_factor

        # Enforce zoom limits
        if new_zoom < self._zoom_min or new_zoom > self._zoom_max:
            return  # Do nothing if zoom level is out of bounds

        # Apply the scaling (zoom in or out)
        self.scale(zoom_factor, zoom_factor)
        self._current_zoom = new_zoom

        # After scaling, reposition the view so the mouse stays in the same place
        # Get the position of the mouse after the zoom
        mouse_view_pos_after = self.mapToScene(mouse_view_pos.toPoint())
        
        # Translate the view to keep the mouse point stable
        delta = mouse_view_pos_after - mouse_scene_pos
        self.translate(delta.x(), delta.y())

# Setup the application and scene
app = QApplication(sys.argv)
scene = QGraphicsScene()

# Add a large rectangle to the scene (could be any item or image)
scene.addRect(0, 0, 500, 500)
scene.addRect(100, 500, 500, 400)

# Create the zoomable view and show the scene
view = ZoomableGraphicsView(scene)
view.show()

sys.exit(app.exec())

