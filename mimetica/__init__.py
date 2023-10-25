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
from mimetica.display.chart import Chart
from mimetica.display.splitview import SplitView
from mimetica.display.tab import Tab

__all__ = [
    "Thumbnail",
    "Canvas",
    "ImageView",
    "Dock",
    "Tab",
    "Chart",
    "SplitView",
    "Layer",
    "Stack",
    "logger",
    "utils",
]
