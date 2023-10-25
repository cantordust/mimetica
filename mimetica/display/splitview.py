from typing import *

# --------------------------------------
from pathlib import Path

# --------------------------------------
import numpy as np

# --------------------------------------
from PySide6.QtCore import (
    Qt,
    Slot,
    QStandardPaths,
)
from PySide6.QtWidgets import (
    QSplitter,
)

# --------------------------------------
from mimetica import (
    Canvas,
    Chart,
    Layer,
)


class SplitView(QSplitter):
    def __init__(
        self,
        canvas: Canvas,
    ):
        super().__init__()

        # Canvas
        self.canvas = canvas
        self.addWidget(self.canvas)

        self.right_panel = QSplitter(self)
        self.right_panel.setOrientation(Qt.Orientation.Vertical)
        self.addWidget(self.right_panel)

        self.radial_chart = Chart(
            title="Radial profile",
            labels={
                "left": "Density [a.u.]",
                "bottom": "Normalised radius [a.u.]",
            },
        )
        self.right_panel.addWidget(self.radial_chart)

        self.phase_chart = Chart(
            title="Phase profile",
            labels={
                "left": "Density [a.u.]",
                "bottom": "Angle [deg]",
            },
        )
        self.phase_chart.setXRange(0, 360)
        self.right_panel.addWidget(self.phase_chart)

    @Slot(Layer)
    def plot(
        self,
        layer: Layer,
    ):
        self.radial_chart.clear()
        self.phase_chart.clear()

        # Plot the radial profile
        xs = np.linspace(0, 1, len(self.canvas.contours))
        self.radial_chart.plot(xs, layer.radial_profiles)

        # Plot the phase profile
        xs = np.linspace(0, 360, len(layer.phase_profiles), endpoint=False)
        self.phase_chart.plot(xs, layer.phase_profiles)
