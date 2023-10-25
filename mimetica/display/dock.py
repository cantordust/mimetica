from typing import *

# --------------------------------------
from PySide6.QtCore import (
    Qt,
    Slot,
)

from PySide6.QtWidgets import (
    QWidget,
    QDockWidget,
    QSpinBox,
    QLabel,
    QGridLayout,
    QFormLayout,
    QHBoxLayout,
    QVBoxLayout,
    QSizePolicy,
)


class Dock(QDockWidget):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        title = QLabel("Settings")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 14pt; font-weight: bold; text-align: center;")
        title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.setTitleBarWidget(title)

        self.setVisible(False)
        self.setMinimumWidth(200)
        topright = Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight

        self.grid = QFormLayout()

        # Threshold spinbox
        # ==================================================
        self.threshold = 70
        self.threshold_lbl = QLabel(self)
        self.threshold_lbl.setText(f"Threshold:")
        self.threshold_spinbox = QSpinBox(self)
        self.threshold_spinbox.setValue(self.threshold)
        self.threshold_spinbox.setRange(0, 255)
        self.grid.addRow(self.threshold_lbl, self.threshold_spinbox)
        self._update_threshold()

        # # Smoothness slider
        # # ==================================================
        # self.smoothness = 5
        # self.smoothness_lbl = QLabel(self)
        # self.smoothness_lbl.setText(f"Smoothness:")
        # self.smoothness_spinbox = QSpinBox(self)
        # self.smoothness_spinbox.setValue(self.smoothness)
        # self.smoothness_spinbox.setRange(0, 50)
        # grid.addRow(self.smoothness_lbl, self.smoothness_spinbox)
        # self._update_smoothness()

        # Set up the main widget
        # ==================================================
        self.body = QWidget()
        self.setWidget(self.body)
        self.body.setLayout(self.grid)
        self.body.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

    def _update_threshold(self):
        self.threshold = self.threshold_spinbox.value()

    # def _update_smoothness(self):
    #     self.smoothness = self.smoothness_spinbox.value()
