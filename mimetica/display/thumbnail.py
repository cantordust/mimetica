from typing import *

# --------------------------------------
import numpy as np

# --------------------------------------
from PySide6.QtCore import QEvent, Signal
from PySide6.QtGui import (
    QPixmap,
    QImage,
)
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
)

# --------------------------------------
from mimetica import Layer

class Thumbnail(QLabel):

    _selected = Signal(Layer)

    def __init__(
        self,
        layer: Layer,
        scale: int = 75,
        parent: QWidget = None,
    ):
        super().__init__(parent)

        self.layer = layer

        (height, width) = layer.image.shape
        qimg = QImage((layer.image.astype(np.uint8)).data, height, width, width, QImage.Format.Format_Indexed8)
        pxm = QPixmap(qimg).scaledToHeight(scale)
        self.setPixmap(pxm)
        self.setFixedHeight(scale)

    def mousePressEvent(
        self,
        event: QEvent,
    ):
        self._selected.emit(self.layer)
