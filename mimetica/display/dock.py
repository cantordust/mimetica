from typing import *

# --------------------------------------
from PySide6.QtCore import Qt
from PySide6.QtCore import Signal

from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QDockWidget
from PySide6.QtWidgets import QSpinBox
from PySide6.QtWidgets import QCheckBox
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QFormLayout
from PySide6.QtWidgets import QSizePolicy


class Dock(QDockWidget):
    sig_show_inactive_plots = Signal(bool)
    sig_set_inactive_plot_opacity = Signal(int)

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

        # Show all plots checkbox
        # ==================================================
        self.show_inactive_plots = True
        self.show_inactive_plots_lbl = QLabel(self)
        self.show_inactive_plots_lbl.setText(f"Show all plots:")
        self.show_inactive_plots_cbox = QCheckBox(self)
        self.show_inactive_plots_cbox.setChecked(self.show_inactive_plots)
        self.grid.addRow(self.show_inactive_plots_lbl, self.show_inactive_plots_cbox)
        self.show_inactive_plots_cbox.stateChanged.connect(
            self._trigger_show_inactive_plots
        )

        # Plot alpha slider
        # ==================================================
        self.inactive_plot_opacity = 17
        self.inactive_plot_opacity_lbl = QLabel(self)
        self.inactive_plot_opacity_lbl.setText(f"Inactive plot opacity:")
        self.inactive_plot_opacity_spinbox = QSpinBox(self)
        self.inactive_plot_opacity_spinbox.setRange(0, 255)
        self.inactive_plot_opacity_spinbox.setSingleStep(1)
        self.inactive_plot_opacity_spinbox.setValue(self.inactive_plot_opacity)
        self.grid.addRow(
            self.inactive_plot_opacity_lbl, self.inactive_plot_opacity_spinbox
        )
        self.inactive_plot_opacity_spinbox.valueChanged.connect(
            self._trigger_set_inactive_plot_opacity
        )

        # Set up the main widget
        # ==================================================
        self.body = QWidget()
        self.setWidget(self.body)
        self.body.setLayout(self.grid)
        self.body.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

    def _trigger_show_inactive_plots(self):
        self.show_inactive_plots = self.show_inactive_plots_cbox.isChecked()
        self.sig_show_inactive_plots.emit(self.show_inactive_plots)

    def _trigger_set_inactive_plot_opacity(self):
        self.inactive_plot_opacity = self.inactive_plot_opacity_spinbox.value()
        self.sig_set_inactive_plot_opacity.emit(self.inactive_plot_opacity)
