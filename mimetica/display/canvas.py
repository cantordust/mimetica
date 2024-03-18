from typing import *

# --------------------------------------
from PySide6.QtCore import Qt
from PySide6.QtCore import Slot
from PySide6.QtCore import Signal

from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QScrollArea
from PySide6.QtWidgets import QSizePolicy

# --------------------------------------
import numpy as np

# --------------------------------------
import pyqtgraph as pg
from pyqtgraph.GraphicsScene.mouseEvents import MouseClickEvent
from pyqtgraph import SignalProxy

# --------------------------------------
from mimetica import Thumbnail
from mimetica import ImageView
from mimetica import Layer
from mimetica import Stack
from mimetica import logger
from mimetica.display.roi.contour import Contour
from mimetica.display.roi.target import Target


class Canvas(QWidget):
    plot = Signal()
    highlight_plot = Signal(int)
    update_radial_plot = Signal(float)
    update_phase_plot = Signal(float)

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        # Image viewport
        # ==================================================
        self.iv = ImageView(self)

        # Slots, signals and proxies
        # ==================================================

        # Mouse tracking for the ROI
        # ==================================================
        self.mouse_tracker = SignalProxy(
            self.iv.scene.sigMouseMoved, rateLimit=100, slot=self._mouse_coordinates
        )
        self.rad2deg = 180 / np.pi

        # Current stack
        # ==================================================
        self.stack = None

        # Arrays used for displaying parts of the layer
        # ==================================================
        self.image = None
        self.centre = None
        self.stack_mbc = None
        self.layer_mbcs = []
        self.phase_resolution = 1

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

        # Layer highlighters
        # ==================================================
        self.layer_contour_pen = pg.mkPen(color="#dd3", width=1)
        self.layer_contour = None
        self.layer_centre_pen = pg.mkPen(color="#dd3", width=1)
        self.layer_centre = None

        # Stack highlighters
        # ==================================================
        self.stack_contour_pen = pg.mkPen(color="#f03", width=1)
        self.stack_contour = None

        self.tb_scroll_area.setFixedHeight(110)
        self.tb_scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.tb_scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.tb_scroll_area.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum
        )
        self.tb_scroll_area.setWidgetResizable(True)
        self.tb_scroll_area.setWidget(self.tb_widget)

        self.grid.addWidget(self.tb_scroll_area, 1, 0, 1, 2)

    @property
    def layer(self) -> Layer:
        return self.stack.layers[self.stack.current_layer]

    def set_stack(
        self,
        stack: Stack,
        auto_range: bool = False,
    ):
        # Update the stack
        # ==================================================
        self.stack = stack
        if len(self.stack.layers) > 0:
            self.stack._update_current_layer()

        # Select the first layer
        # ==================================================
        self.select_layer(0, auto_range)

        # Update the thumbnails
        # ==================================================
        self._update_thumbnails()

    @Slot(int, bool)
    def select_layer(
        self,
        layer: int,
        auto_range: bool = False,
    ):
        # Update the layer
        # ==================================================
        self.stack._update_current_layer(layer)

        # Process the layer
        self.process(auto_range)

        # Emit a signal to highlight the relevant plots
        # ==================================================
        # with np.printoptions(threshold=np.inf):
        #     print(f"==[ layer phase profile: {self.layer.phase_profile}")

        self.highlight_plot.emit(layer)

    def process(
        self,
        auto_range: bool = False,
    ):
        # Paint the result onto the canvas
        # ==================================================
        self._draw(auto_range)

        # Set up the ROI
        # ==================================================
        self.iv.set_roi(self.layer)

        # Plot the radial and phase profiles
        # ==================================================
        self.plot.emit()

    def _draw(
        self,
        auto_range: bool = False,
    ):
        # Coordinates of the current layer and the stack
        # ==================================================
        lcx, lcy = self.layer.centre
        scx, scy = self.stack.centre

        # Reset the canvas
        # ==================================================
        self.image = np.zeros(self.stack.merged.shape + (3,))

        # Draw the background
        # ==================================================
        self.image += self.stack.merged[:, :, None] // 4

        # Draw the image
        # ==================================================
        # self.image[:, :, 0] = self.layer.image // 4
        self.image[:, :, 1] = self.layer.image // 2
        self.image[:, :, 2] = self.layer.image // 2

        # Draw the centre
        # ==================================================
        if self.layer_centre is not None:
            self.iv.removeItem(self.layer_centre)
        self.layer_centre = Target(
            (lcy + 0.5, lcx + 0.5),
            pen=self.layer_centre_pen,
        )
        self.iv.addItem(self.layer_centre)

        # Draw the minimal bounding circle for the layer
        # ==================================================
        if self.layer_contour is not None:
            self.iv.removeItem(self.layer_contour)
        self.layer_contour = Contour(
            (lcy + 0.5, lcx + 0.5),
            radius=self.layer.radius,
            pen=self.layer_contour_pen,
        )
        self.iv.addItem(self.layer_contour)

        # Draw the minimal bounding circle for the stack
        # ==================================================
        if self.stack_contour is not None:
            self.iv.removeItem(self.stack_contour)
        self.stack_contour = Contour(
            (scy + 0.5, scx + 0.5),
            radius=self.stack.radius,
            pen=self.stack_contour_pen,
        )
        self.iv.addItem(self.stack_contour)

        # Set the image
        # ==================================================
        self.iv.setImage(
            self.image,
            autoRange=auto_range,
            levels=(0, 255),
        )

    def _update_thumbnails(self):
        while True:
            item = self.tb_layout.takeAt(0)
            if item is None or item.isEmpty():
                break
            self.tb_layout.removeWidget(item.widget())
            item.widget().deleteLater()

        self.thumbnails.clear()
        for index, layer in enumerate(self.stack.layers):
            tb = Thumbnail(index, layer, 90, self)
            tb._selected.connect(self.select_layer)
            self.thumbnails.append(tb)

        for idx, tb in enumerate(self.thumbnails):
            self.tb_layout.addWidget(tb, alignment=Qt.AlignmentFlag.AlignLeft)

        self.tb_layout.addStretch()

    @Slot()
    def _reset_zoom(self):
        self._draw(auto_range=True)

    @Slot()
    def _mouse_coordinates(
        self,
        event: MouseClickEvent,
    ):
        if self.iv.radial_roi is not None:
            pos = self.iv.getView().vb.mapSceneToView(event)[0]

            cx = pos.x() - self.layer.centre[1] - 0.5
            cy = pos.y() - self.layer.centre[0] - 0.5
            r = np.sqrt(cx**2 + cy**2)
            radius = r / self.layer.radius
            r2 = 2 * r
            if radius <= 1:
                if r == 0:
                    phase = 0
                else:
                    phase = self.rad2deg * np.arccos(cx / r)
                if cy < 0:
                    phase = 360 - phase

                self.iv.radial_roi.setSize(
                    r2,
                    center=(0.5, 0.5),
                    update=True,
                    finish=True,
                )
                self.iv.phase_roi.set_end(pos)
                self.update_radial_plot.emit(radius)
                self.update_phase_plot.emit(phase)
