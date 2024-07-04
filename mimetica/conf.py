import typing as tp

# --------------------------------------
from dataclasses import dataclass

# --------------------------------------
import sys

# --------------------------------------
from loguru import logger

# --------------------------------------
from datetime import datetime

# --------------------------------------
from PySide6.QtCore import QSettings

from PySide6.QtGui import QColor

# --------------------------------------
from mimetica.version import version

logger.remove()
logger.add(sys.stdout, format="PID {process} | {message}")


settings = QSettings("Hobbes", "Mimetica")
settings.setValue("copyright", f"{datetime.now().year} Alexander Hadjiivanov")
settings.setValue("version", f"{version}")


@dataclass
class Conf:
    WindowGeometry: str = "window/geometry"
    WindowPosition: str = "window/position"
    InactivePlotColour: str = "plots/inactive/colour"
    ShowInactivePlots: str = "plots/inactive/show"
    ActivePlotColour: str = "plots/active/colour"
    InactiveSliceColour: str = "slice/inactive/colour"
    ActiveSliceColour: str = "slice/active/colour"
    StackContourColour: str = "stack/contour/colour"
    SliceContourColour: str = "slice/contour/colour"
    ShowStack: str = "stack/show"

    @property
    def window_geometry(self):
        pass

    # Show inactive plots
    # ==================================================
    @property
    def show_inactive_plots(self) -> bool:
        return settings.value(Conf.ShowInactivePlots, True, bool)

    @show_inactive_plots.setter
    def show_inactive_plots(
        self,
        value: QColor,
    ):
        settings.setValue(Conf.ShowInactivePlots, value)

    # Inactive plot colour
    # ==================================================
    @property
    def inactive_plot_colour(self) -> QColor:
        return settings.value(
            Conf.InactivePlotColour,
            QColor(147, 147, 147, 100),
            QColor,
        )

    @inactive_plot_colour.setter
    def inactive_plot_colour(
        self,
        value: QColor,
    ):
        settings.setValue(Conf.InactivePlotColour, value)

    # Active plot colour
    # ==================================================
    @property
    def active_plot_colour(self) -> QColor:
        return settings.value(
            Conf.ActivePlotColour,
            QColor(51, 255, 51, 255),
            QColor,
        )

    @active_plot_colour.setter
    def active_plot_colour(
        self,
        value: QColor,
    ):
        settings.setValue(Conf.ActivePlotColour, value)

    # Slice contour colour
    # ==================================================
    @property
    def slice_contour_colour(self) -> QColor:
        return settings.value(
            Conf.SliceContourColour,
            QColor(255, 255, 0, 255),
            QColor,
        )

    @slice_contour_colour.setter
    def slice_contour_colour(
        self,
        value: QColor,
    ):
        settings.setValue(Conf.SliceContourColour, value)

    # Stack contour colour
    # ==================================================
    @property
    def stack_contour_colour(self) -> QColor:
        return settings.value(
            Conf.StackContourColour,
            QColor(255, 0, 0, 255),
            QColor,
        )

    @stack_contour_colour.setter
    def stack_contour_colour(
        self,
        value: QColor,
    ):
        settings.setValue(Conf.StackContourColour, value)

    # Show stack
    # ==================================================
    @property
    def show_stack(self) -> bool:
        return settings.value(Conf.ShowStack, True, bool)

    @show_stack.setter
    def show_stack(
        self,
        value: QColor,
    ):
        settings.setValue(Conf.ShowStack, value)


conf = Conf()
