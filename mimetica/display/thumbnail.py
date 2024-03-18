from typing import *

# --------------------------------------
from PySide6.QtCore import QEvent
from PySide6.QtCore import Signal

from PySide6.QtGui import QPixmap
from PySide6.QtGui import QImage

from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QLabel

# --------------------------------------
from mimetica import Layer


class Thumbnail(QLabel):

    _selected = Signal(int)

    def __init__(
        self,
        index: int,
        layer: Layer,
        scale: int = 75,
        parent: QWidget = None,
    ):
        super().__init__(parent)

        self.index = index
        self.layer = layer

        (height, width) = layer.image.shape

        qimg = QImage(layer.path)
        pxm = QPixmap(qimg).scaledToHeight(scale)
        self.setPixmap(pxm)
        self.setFixedHeight(scale)

    def mousePressEvent(
        self,
        event: QEvent,
    ):
        self._selected.emit(self.index)
