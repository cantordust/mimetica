from typing import *

# --------------------------------------
from pathlib import Path

# --------------------------------------
from PySide6 import QtCore
from PySide6.QtCore import Slot, Signal, QPoint

from PySide6.QtGui import (
    QPixmap,
    QIcon,
    QImage,
    QPicture,
    QMouseEvent,
)

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QGridLayout,
    QHBoxLayout,
    QSlider,
    QScrollArea,
    QScrollBar,
    QSizePolicy,
)

# --------------------------------------
import numpy as np

# --------------------------------------
import cv2 as cv

# --------------------------------------
import pyqtgraph as pg

# --------------------------------------
from mimetica import Thumbnail
from mimetica import logger


class ImageView(pg.ImageView):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.ui.histogram.hide()
        self.ui.roiBtn.hide()
        self.ui.menuBtn.hide()
