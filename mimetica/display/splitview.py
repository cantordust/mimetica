from typing import *

# --------------------------------------
import numpy as np

# --------------------------------------
from PySide6.QtCore import Qt
from PySide6.QtCore import Slot

from PySide6.QtWidgets import QSplitter

# --------------------------------------
import pyqtgraph as pg

# --------------------------------------
from mimetica import Canvas
from mimetica import Plot
from mimetica import Layer


class SplitView(QSplitter):
    def __init__(
        self,
        canvas: Canvas,
    ):
        super().__init__()

        # Canvas
        # ==================================================
        self.canvas = canvas
        self.addWidget(self.canvas)

        self.right_panel = QSplitter(self)
        self.right_panel.setOrientation(Qt.Orientation.Vertical)
        self.addWidget(self.right_panel)

        # Switch to show or hide inactive plots
        self.show_inactive_plots = True

        # Radial profile plot
        # ==================================================
        self.radial_graph = Plot(
            title="Radial profile",
            labels={
                "left": "Density [a.u.]",
                "bottom": "Normalised radius [a.u.]",
            },
        )
        self.radial_graph.setXRange(0, 1)
        self.radial_graph.setYRange(0, 1.2)
        self.radial_plots = {}
        self.right_panel.addWidget(self.radial_graph)
        self.radial_guide = pg.InfiniteLine(0)
        self.radial_arrow = None
        self.radial_lbl = pg.InfLineLabel(
            line=self.radial_guide,
            text="",
            position=0.98,
        )

        # Phase profile plot
        # ==================================================
        self.phase_graph = Plot(
            title="Phase profile",
            labels={
                "left": "Density [a.u.]",
                "bottom": "Angle [deg]",
            },
        )
        self.phase_graph.setXRange(0, 360)
        self.phase_graph.setYRange(0, 1.2)
        self.phase_plots = {}
        self.right_panel.addWidget(self.phase_graph)
        self.phase_arrow = None
        self.phase_guide = pg.InfiniteLine(0)
        self.phase_lbl = pg.InfLineLabel(
            line=self.phase_guide,
            text="",
            position=0.98,
        )

        # Pens
        # ==================================================
        self.highlight_pen_colour = [51, 255, 51, 255]
        self.highlight_pen_width = 1.0
        self.highlight_pen = None
        self.muted_pen_colour = [147, 147, 147, 17]
        self.muted_pen_width = 0.5
        self.muted_pen = None
        self.invisible_pen_colour = [0, 0, 0, 0]
        self.invisible_pen_width = 0
        self.invisible_pen = None
        self._update_pens()

        # Current layer index & reference
        # ==================================================
        self.current_layer_idx = 0
        self.current_layer = None

        # Slots and signals
        # ==================================================
        self.canvas.update_radial_plot.connect(self._update_radial_pos)
        self.canvas.update_phase_plot.connect(self._update_phase_pos)
        self.canvas.plot.connect(
            lambda: self.plot(self.canvas.stack.layers, self.canvas.stack.current_layer)
        )
        self.canvas.highlight_plot.connect(lambda layer: self._highlight_plot(layer))

    def _update_pens(self):
        self.highlight_pen = pg.mkPen(
            color=self.highlight_pen_colour, width=self.highlight_pen_width
        )
        self.muted_pen = pg.mkPen(
            color=self.muted_pen_colour, width=self.muted_pen_width
        )
        self.invisible_pen = pg.mkPen(
            color=self.invisible_pen_colour, width=self.invisible_pen_width
        )

    @Slot(list, int)
    def plot(
        self,
        layers: List[Layer],
        current_layer_idx: int,
    ):
        self.radial_plots.clear()
        self.phase_plots.clear()

        self.radial_graph.clear()
        self.phase_graph.clear()

        for radial_plot in self.radial_plots.values():
            self.radial_graph.removeItem(radial_plot)

        for phase_plot in self.phase_plots.values():
            self.phase_graph.removeItem(phase_plot)

        # Plot all layers
        # ==================================================
        for idx, layer in enumerate(layers):
            if idx == current_layer_idx:
                pen = self.highlight_pen
                self.current_layer_idx = idx
                self.current_layer = layer
                self.phase_graph.setXRange(0.0, layer.phase_range.max())
            else:
                if self.show_inactive_plots:
                    pen = self.muted_pen
                else:
                    pen = self.invisible_pen

            # Plot the radial profile
            if layer.radial_range is not None:
                self.radial_plots[idx] = self.radial_graph.plot(
                    layer.radial_range,
                    layer.radial_profile,
                    pen=pen,
                )

            # Plot the phase profile
            if layer.phase_range is not None:
                self.phase_plots[idx] = self.phase_graph.plot(
                    layer.phase_range,
                    layer.phase_profile,
                    pen=pen,
                )

            if idx == current_layer_idx:
                self.radial_arrow = pg.CurveArrow(self.radial_plots[idx])
                self.radial_arrow.setRotation(270)
                self.radial_arrow._rotate = False
                self.phase_arrow = pg.CurveArrow(self.phase_plots[idx])
                self.phase_arrow.setRotation(270)
                self.phase_arrow._rotate = False

        # Add vertical guides
        # ==================================================
        self.radial_graph.addItem(self.radial_guide)
        self.radial_graph.addItem(self.radial_arrow)
        self.phase_graph.addItem(self.phase_guide)
        self.phase_graph.addItem(self.phase_arrow)

    @Slot(float, str)
    def _update_radial_pos(
        self,
        radius: float,
    ):
        # Find the index of the closest value in self.radial_xs
        xs = self.current_layer.radial_range
        diff = np.absolute(xs - radius)
        index = diff.argmin()
        x = xs[index]
        y = self.current_layer.radial_profile[index]
        self.radial_guide.setPos(x)
        self.radial_arrow.setIndex(index)
        self.radial_lbl.setText(f"{x.item():0.3f}|{y:0.3f}")

    @Slot(float, str)
    def _update_phase_pos(
        self,
        phase: float,
    ):
        # Find the index of the closest phase value
        xs = self.current_layer.phase_range
        diff = np.absolute(xs - phase)
        index = diff.argmin()
        x = xs[index]
        y = self.current_layer.phase_profile[index]
        self.phase_guide.setPos(x)
        self.phase_arrow.setIndex(index)
        self.phase_lbl.setText(f"{x.item():3.3f}|{y:0.3f}")

    @Slot(bool)
    def _show_inactive_plots(
        self,
        show: bool,
    ):

        self.show_inactive_plots = show
        for idx in self.radial_plots:
            if idx != self.current_layer_idx:
                if self.show_inactive_plots:
                    self.radial_plots[idx].setPen(self.muted_pen)
                    self.phase_plots[idx].setPen(self.muted_pen)
                    self.radial_plots[idx].update()
                    self.phase_plots[idx].update()
                else:
                    self.radial_plots[idx].setPen(self.invisible_pen)
                    self.phase_plots[idx].setPen(self.invisible_pen)
                    self.radial_plots[idx].update()
                    self.phase_plots[idx].update()

    @Slot(int)
    def _set_inactive_plot_opacity(
        self,
        opacity: int,
    ):

        self.muted_pen_colour[-1] = opacity
        self._update_pens()
        if self.show_inactive_plots:
            for idx in self.radial_plots:
                if idx != self.current_layer_idx:
                    self.radial_plots[idx].setPen(self.muted_pen)
                    self.phase_plots[idx].setPen(self.muted_pen)
                    self.radial_plots[idx].update()
                    self.phase_plots[idx].update()

    @Slot(int)
    def _highlight_plot(
        self,
        layer_idx: int,
    ):

        self.radial_plots[self.current_layer_idx].setPen(self.muted_pen)
        self.radial_plots[layer_idx].setPen(self.highlight_pen)
        self.radial_plots[layer_idx].update()

        self.phase_plots[self.current_layer_idx].setPen(self.muted_pen)
        self.phase_plots[layer_idx].setPen(self.highlight_pen)
        self.phase_plots[layer_idx].update()

        self.current_layer_idx = layer_idx
