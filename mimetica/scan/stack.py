from typing import *

# --------------------------------------
from pathlib import Path

# --------------------------------------
import numpy as np

# --------------------------------------
import shapely as shp

# --------------------------------------
from concurrent.futures import ProcessPoolExecutor

# --------------------------------------
from PySide6.QtCore import Slot
from PySide6.QtCore import Signal
from PySide6.QtCore import QObject

# --------------------------------------
from mimetica import Layer
from mimetica import utils
from mimetica import logger


class Stack(QObject):
    update_progress = Signal(Path)
    set_canvas = Signal()
    abort = Signal()

    @staticmethod
    def make_layer(
        args: Dict,
    ):
        layer = Layer(
            args["path"],
        )

        # logger.info(f"Processed {layer.path} | TID: {os.getpid()}")

        return layer

    def __init__(self, paths: List[Path], threshold: int = 70, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Save the parameters
        # ==================================================
        self.paths = sorted(paths)
        self.threshold = threshold

        # Other attributes
        # ==================================================
        self.mbc = None
        self.centre = None
        self.radius = None
        self.layers = []
        self.current_layer = 0

        # Create a merged stack
        # ==================================================
        self.merged = None

    def _update_current_layer(
        self,
        layer: int = 0,
    ):
        self.current_layer = layer

    @Slot(int, int)
    def _set_centre(
        self,
        x: int,
        y: int,
    ):
        self.centre = np.array([x, y], dtype=np.int32)

    def _update_threshold(
        self,
        threshold: int,
    ):
        pass

    def _compute_mbc(self):
        self.mbc = utils.compute_mbc(self.merged).simplify(1, preserve_topology=True)
        self.centre = np.array(
            list(reversed(shp.centroid(self.mbc).coords)), dtype=np.int32
        )[0]
        self.radius = int(shp.minimum_bounding_radius(self.mbc))

    @Slot()
    def process(self):
        logger.info(f"Loading stack...")

        # Layer factory
        # ==================================================
        args = [{"path": path} for path in self.paths]

        with ProcessPoolExecutor() as executor:
            for layer in executor.map(Stack.make_layer, args):
                self.layers.append(layer)
                self.update_progress.emit(layer.path)

        self._update_current_layer()

        # Calibrate the stack based on all the images
        # ==================================================
        images = []
        for layer in self.layers:

            # print(f"==[ img_path: {img_path}")

            minval = layer.image.min()
            maxval = layer.image.max()

            if self.merged is None:
                self.merged = layer.image.copy().astype(np.uint32)
            else:
                self.merged += layer.image

        # Scale the merged stack
        # ==================================================
        minval = self.merged.min()
        maxval = self.merged.max()
        self.merged = (255 * (self.merged - minval) / (maxval - minval)).astype(
            np.ubyte
        )

        # Compute the minimal bounding circle
        # ==================================================
        self._compute_mbc()

        # Set the stack on the canvas
        # ==================================================
        self.set_canvas.emit()
