from typing import *

# --------------------------------------
from pathlib import Path

# --------------------------------------
from PySide6 import QtCore
from PySide6.QtCore import (
    Qt,
    Slot,
    Signal,
)

from PySide6.QtGui import (
    QMouseEvent,
)

from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QHBoxLayout,
    QScrollArea,
    QSizePolicy,
)

# --------------------------------------
import numpy as np

# --------------------------------------
import skimage as ski
import skimage.draw as skd

# --------------------------------------
import shapely.affinity as sha

# --------------------------------------
from scipy.ndimage import binary_fill_holes as bfh

# --------------------------------------
from pyqtgraph.GraphicsScene.mouseEvents import MouseClickEvent

# --------------------------------------
from mimetica import Thumbnail
from mimetica import ImageView
from mimetica import Layer
from mimetica import Stack
from mimetica import logger


class Canvas(QWidget):

    update_plots = Signal(Layer)

    def __init__(
        self,
        *args,
        **kwargs,
    ):

        super().__init__(*args, **kwargs)

        # Image viewport
        # ==================================================
        self.iv = ImageView(self)

        # Slots
        # ==================================================


        # Current stack
        # ==================================================
        self.stack = None

        # Current layer to display
        # ==================================================
        self.layer = None

        # Arrays used for displaying parts of the layer
        # ==================================================
        self.image = None
        self.centre = None
        self.stack_mbc = None
        self.layer_mbc = []
        self.contours = []
        self.spokes = []

        # Layout grid
        # ==================================================
        self.grid = QGridLayout(self)
        self.grid.addWidget(self.iv, 0, 0, 1, 2)

        # Thumbnails
        # ==================================================
        self.thumbnails = []
        self.tb_widget = QWidget()
        self.tb_scroll_area = QScrollArea(self)
        self.tb_layout = QHBoxLayout()
        self.tb_layout.setContentsMargins(0, 0, 0, 0)
        self.tb_widget.setLayout(self.tb_layout)

        self.tb_scroll_area.setFixedHeight(110)
        self.tb_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tb_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tb_scroll_area.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.tb_scroll_area.setWidgetResizable(True)
        self.tb_scroll_area.setWidget(self.tb_widget)

        self.grid.addWidget(self.tb_scroll_area, 1, 0, 1, 2)

    def set_stack(
        self,
        stack: Stack,
        auto_range: bool = False,
    ):

        self.stack = stack
        self.process(auto_range)

        # Show thumbnails
        # ==================================================
        self._update_thumbnails()

        if len(self.stack.layers) > 0:
            self.stack._update_current_layer(self.stack.layers[0])

    def set_layer(
        self,
        layer: Layer,
        auto_range: bool = False,
    ):

        self.stack._update_current_layer(layer)
        self.process(auto_range)

    def process(
        self,
        auto_range: bool = False,
    ):

        # Central point
        # ==================================================
        self._make_centre()

        # Current (selected) layer
        # ==================================================
        self._make_layer()

        # Mesh of contours and spokes
        # ==================================================
        self._make_mesh()

        # Paint the result onto the canvas
        # ==================================================
        self._draw(auto_range)

        # Emit a signal to update the plots
        # ==================================================
        self.update_plots.emit(self.stack.current_layer)

    def _draw(
        self,
        auto_range: bool = False,
    ):

        # Reset the canvas
        # ==================================================
        self.image = np.zeros(self.stack.merged.shape + (3,), dtype=np.uint32)
        layer = self.stack.current_layer

        # Draw the background
        # ==================================================
        for ch in range(self.image.shape[-1]):
            self.image[:, :, ch] += self.stack.merged

        # Draw the current layer
        # ==================================================
        self.image[:, :, 0] += self.stack.current_layer.image
        self.image[:, :, 2] += self.stack.current_layer.image

        # Draw the centre
        # ==================================================
        self.image[self.centre[0], self.centre[1], 1] += 2**16 - 1

        # Draw the minimal bounding circles
        # ==================================================
        for ch in range(self.image.shape[-1]):
            self.image[self.stack_mbc[0], self.stack_mbc[1], ch] = 2**16 - 1
        self.image[self.layer_mbc[0], self.layer_mbc[1], 1] = 2**16 - 1

        # Draw the contours
        # ==================================================
        for idx, contour in enumerate(self.contours):
            self.image[contour[0], contour[1], 1] = layer.mask[contour[0], contour[1]]

        # Draw the spokes
        # ==================================================
        for idx, spoke in enumerate(self.spokes):
            self.image[spoke[0], spoke[1], 0] = layer.mask[spoke[0], spoke[1]]

        # Set the image
        # ==================================================
        self.iv.setImage(self.image, autoRange=auto_range)

    def _make_centre(
        self,
        auto_range: bool = False,
    ):

        cx, cy = self.stack.current_layer.centre
        self.centre = skd.circle_perimeter(cy, cx, 5)

    def _make_mesh(
        self,
        auto_range: bool = False,
    ):

        # Stack MBC
        # ==================================================
        cx, cy = self.stack.centre
        self.stack_mbc = skd.circle_perimeter(cy, cx, self.stack.radius)

        # Layer MBC
        # ==================================================
        cx, cy = self.stack.current_layer.centre
        self.layer_mbc = skd.circle_perimeter(cy, cx, self.stack.current_layer.mbc_radius)

        # Contours
        # ==================================================
        self.contours.clear()
        for radius in self.stack.current_layer.radii:

            # self.radial_layer += ring
            cx, cy = self.stack.current_layer.centre
            self.contours.append(skd.circle_perimeter(cy, cx, radius))

        # Spokes
        # ==================================================
        self.spokes.clear()
        for spoke in self.stack.current_layer.spokes:
            self.spokes.append(spoke)

    def _make_layer(self):
        if self.layer is None:
            self.layer = self.stack.layers[0]

    def _update_thumbnails(self):

        while True:
            item = self.tb_layout.takeAt(0)
            if item is None or item.isEmpty():
                break
            self.tb_layout.removeWidget(item.widget())
            item.widget().deleteLater()

        self.thumbnails.clear()
        for layer in self.stack.layers:

            tb = Thumbnail(layer, 90, self)
            tb._selected.connect(self._select_layer)
            self.thumbnails.append(tb)

        for idx, tb in enumerate(self.thumbnails):
            self.tb_layout.addWidget(tb, alignment=Qt.AlignmentFlag.AlignLeft)

        self.tb_layout.addStretch()

    @Slot(str)
    def _select_layer(
        self,
        layer: Layer,
    ):
        self.set_layer(layer)

    @Slot()
    def _reset_zoom(self):

        self._draw(auto_range=True)
