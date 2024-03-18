import sys

# --------------------------------------
from loguru import logger

logger.remove()
logger.add(sys.stdout, format="PID {process} | {message}")
# --------------------------------------

from mimetica.scan.layer import Layer
from mimetica.scan.stack import Stack
from mimetica.display.dock import Dock
from mimetica.display.thumbnail import Thumbnail
from mimetica.display.image import ImageView
from mimetica.display.canvas import Canvas
from mimetica.display.plot import Plot
from mimetica.display.splitview import SplitView
from mimetica.display.tab import Tab

# --------------------------------------
import pyqtgraph
# pyqtgraph.setConfigOption('imageAxisOrder', 'row-major')

__all__ = [
    "Thumbnail",
    "Canvas",
    "ImageView",
    "Dock",
    "Tab",
    "Plot",
    "SplitView",
    "Layer",
    "Stack",
    "logger",
    "utils",
]
