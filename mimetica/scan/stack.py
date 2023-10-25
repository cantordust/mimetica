from typing import *

# --------------------------------------
from pathlib import Path

# --------------------------------------
import threading

# --------------------------------------
from multiprocessing.pool import Pool

# --------------------------------------
import numpy as np

# --------------------------------------
import skimage as ski
import skimage.measure as skm

# --------------------------------------
import cv2 as cv

# --------------------------------------
import shapely as shp
import shapely.affinity as sha
import shapely.geometry as shg
from shapely.ops import split
from shapely.ops import snap
from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely.geometry import MultiPoint
from shapely.geometry import LineString
from shapely.geometry import MultiLineString
from shapely.geometry import GeometryCollection

# --------------------------------------
from concurrent.futures import ProcessPoolExecutor

# --------------------------------------
from PySide6.QtCore import (
    QEvent,
    Slot,
    Signal,
    QObject,
)

# --------------------------------------
from mimetica import Layer
from mimetica import utils
from mimetica import logger


class Stack(QObject):

    update_progress = Signal()
    set_canvas = Signal()
    abort = Signal()

    @staticmethod
    def make_layer(
        args: Dict,
    ):
        layer = Layer(
            args["path"],
            args["image"],
            args["threshold"],
        )

        return layer


    def __init__(
        self,
        paths: List[Path],
        # smoothness: int = 5,
        threshold: int = 70,
        *args,
        **kwargs
    ):

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
        self.current_layer: Layer = None

        # Create a merged stack
        # ==================================================
        self.merged = None

    def _update_current_layer(
        self,
        layer: Layer = None,
    ):
        if layer is None:
            layer = self.layers[0]

        self.current_layer = layer

    @Slot(int, int)
    def _set_centre(
        self,
        x: int,
        y: int,
    ):
        self.centre = np.array([x, y], dtype=np.int32)

    # @Slot(bool)
    # def _find_centre(
    #     self,
    #     reset: bool = False,
    # ):

    #     # Sanity check
    #     if self.centre is not None:

    #         if not (0 < self.centre[0] < self.merged.shape[0] and 0 < self.centre[1] < self.merged.shape[1]):
    #             reset = True

    #     # Find the centre
    #     if reset or self.centre is None:
    #         properties = skm.regionprops(self.merged, self.merged)
    #         centre = properties[0].centroid
    #         self.centre = (round(centre[0]), round(centre[1]))

    def _update_threshold(
        self,
        threshold: int,
    ):
        pass

    def _compute_mbc(self):
        self.mbc = utils.compute_mbc(self.merged).simplify(1, preserve_topology=True)
        self.centre = np.array(list(reversed(shp.centroid(self.mbc).coords)), dtype=np.int32)[0]
        self.radius = int(shp.minimum_bounding_radius(self.mbc))

    Slot()
    def process(self):

        # logger.info(f'Loading stack...')

        try:

            images = []
            for img_path in self.paths:

                content = ski.io.imread(str(img_path), as_gray=True).astype(np.uint32)

                # Pad the image
                # ==================================================
                hpad = int(0.2 * content.shape[0])
                wpad = int(0.2 * content.shape[1])

                lpad, rpad = wpad, wpad
                tpad, bpad = hpad, hpad

                minval = content.min()
                maxval = content.max()
                content = ((2**16 - 1) * (content - minval) / (maxval - minval)).astype(np.uint32)
                content = np.pad(content, ((lpad, rpad), (tpad, bpad)), mode="constant", constant_values=0)

                images.append(content)

                if self.merged is None:
                    self.merged = content.copy()
                else:
                    self.merged += content

            # Scale the merged stack
            # ==================================================
            minval = self.merged.min()
            maxval = self.merged.max()
            self.merged = ((2**16 - 1) * (self.merged - minval) / (maxval - minval)).astype(np.uint32)

            # Compute the minimal bounding circle
            # ==================================================
            self._compute_mbc()

            # Layer factory
            # ==================================================
            args = [
                {
                    "path": path,
                    "image": image,
                    "threshold": self.threshold,
                }
                for (path, image) in zip(self.paths, images)
            ]

            with ProcessPoolExecutor() as executor:
                for layer in executor.map(Stack.make_layer, args):

                    self.layers.append(layer)
                    self.update_progress.emit()
                    # logger.info(f'processed {layer.path} | TID: {threading.get_ident()}')

            # The current layer
            # ==================================================
            self._update_current_layer()

            # Set the stack on the canvas
            # ==================================================
            self.set_canvas.emit()

        except Exception as e:
            logger.info(f'Exception caught: {e}')
            self.abort.emit()
