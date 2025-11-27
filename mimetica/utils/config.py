from dataclasses import dataclass


from datetime import datetime


from PySide6.QtCore import QSettings
from PySide6.QtGui import QColor
# import sys
# from omegaconf import OmegaConf
# from platformdirs import PlatformDirs

# from pyqtgraph.parametertree import ParameterTree


@dataclass
class Conf(QSettings):
    WindowGeometry: str = "window/geometry"
    WindowPosition: str = "window/position"
    InactivePlotColour: str = "plots/inactive/colour"
    ShowInactivePlots: str = "plots/inactive/show"
    ActivePlotColour: str = "plots/active/colour"
    InactiveSliceColour: str = "slice/inactive/colour"
    ActiveSliceColour: str = "slice/active/colour"
    StackContourColour: str = "stack/contour/colour"
    SliceContourColour: str = "slice/contour/colour"
    ShowStack: bool = "stack/show"
    RadialSegments: int = "slice/contour/radial_segments"
    PhaseSegments: int = "slice/contour/phase_segments"

    def __init__(self, *args, **kwargs):
        super().__init__("Hobbes Research", "Mimetica", *args, **kwargs)
        self.setValue(
            "Copyright", f"{datetime.now().year} Alexander Hadjiivanov"
        )
        # self.ptree = ParameterTree(showHeader=True)

    @property
    def window_geometry(self):
        pass

    # Show inactive plots
    @property
    def show_inactive_plots(self) -> bool:
        return self.value(Conf.ShowInactivePlots, True, bool)

    @show_inactive_plots.setter
    def show_inactive_plots(
        self,
        value: QColor,
    ):
        self.setValue(Conf.ShowInactivePlots, value)

    # Inactive plot colour
    @property
    def inactive_plot_colour(self) -> QColor:
        return self.value(
            Conf.InactivePlotColour,
            QColor(147, 147, 147, 100),
            QColor,
        )

    @inactive_plot_colour.setter
    def inactive_plot_colour(
        self,
        value: QColor,
    ):
        self.setValue(Conf.InactivePlotColour, value)

    # Active plot colour
    @property
    def active_plot_colour(self) -> QColor:
        return self.value(
            Conf.ActivePlotColour,
            QColor(51, 255, 51, 255),
            QColor,
        )

    @active_plot_colour.setter
    def active_plot_colour(
        self,
        value: QColor,
    ):
        self.setValue(Conf.ActivePlotColour, value)

    # Slice contour colour
    @property
    def slice_contour_colour(self) -> QColor:
        return self.value(
            Conf.SliceContourColour,
            QColor(255, 255, 0, 255),
            QColor,
        )

    @slice_contour_colour.setter
    def slice_contour_colour(
        self,
        value: QColor,
    ):
        self.setValue(Conf.SliceContourColour, value)

    # Stack contour colour
    @property
    def stack_contour_colour(self) -> QColor:
        return self.value(
            Conf.StackContourColour,
            QColor(255, 0, 0, 255),
            QColor,
        )

    @stack_contour_colour.setter
    def stack_contour_colour(
        self,
        value: QColor,
    ):
        self.setValue(Conf.StackContourColour, value)

    # Show stack
    @property
    def show_stack(self) -> bool:
        return self.value(Conf.ShowStack, True, bool)

    @show_stack.setter
    def show_stack(
        self,
        value: bool,
    ):
        self.setValue(Conf.ShowStack, value)

    # Radial segments
    @property
    def radial_segments(self) -> int:
        return self.value(Conf.RadialSegments, 256, int)

    @radial_segments.setter
    def radial_segments(
        self,
        value: int,
    ):
        self.setValue(Conf.RadialSegments, value)

    # Phase segments
    @property
    def phase_segments(self) -> int:
        return self.value(Conf.PhaseSegments, 360, int)

    @phase_segments.setter
    def phase_segments(
        self,
        value: int,
    ):
        self.setValue(Conf.PhaseSegments, value)


conf = Conf()
