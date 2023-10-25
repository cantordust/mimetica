from typing import *

# --------------------------------------
import sys

# --------------------------------------
import threading

# --------------------------------------
from PySide6.QtCore import (
    Qt,
    Slot,
    QThread,
    Signal,
)
from PySide6.QtGui import (
    QAction,
    QKeySequence,
    QPixmap,
    QIcon,
)

from PySide6.QtWidgets import (
    QMainWindow,
    QApplication,
    QFileDialog,
    QMessageBox,
    QToolBar,
    QDockWidget,
    QProgressDialog,
    QTabWidget,
    QWidget,
    QGridLayout,
)

# --------------------------------------
from mimetica import (
    SplitView,
    Stack,
)

# --------------------------------------
from pathlib import Path

# --------------------------------------
from mimetica import Canvas
from mimetica import Dock
from mimetica import utils
from mimetica import logger


class Tab(QMainWindow):

    load_stack = Signal()

    def __init__(
        self,
        paths: List[Path],
    ):
        QMainWindow.__init__(self)

        # The display canvas
        # ==================================================
        self.canvas = Canvas()

        # Splitview widget
        # ==================================================
        self.splitview = SplitView(self.canvas)
        self.splitview.setSizes((2, 1))
        self.setCentralWidget(self.splitview)

        # Dock
        # ==================================================
        self.dock = Dock(features=QDockWidget.DockWidgetFeature.DockWidgetClosable | QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock)

        # Toolbar
        # ==================================================
        self.toolbar = QToolBar(floatable=False, movable=False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)
        self.setup_toolbar()

        # Slots & signals
        # ==================================================
        # self.dock.threshold_spinbox.valueChanged.connect(self._set_threshold)
        self.canvas.update_plots.connect(lambda layer: self.splitview.plot(layer))
        # self.dock.smoothness_spinbox.valueChanged.connect(self._set_smoothness)

        # Thread for preventing the GUI from blocking
        # ==================================================
        self.worker = QThread()
        self.worker.start()

        # The layer stack
        # ==================================================
        paths = paths
        # logger.info(f'Loading stack | TID: {threading.get_ident()}')
        self.stack = Stack(paths, self.dock.threshold)
        self.stack.update_progress.connect(lambda: self.pd.setValue(self.pd.value() + 1))
        self.load_stack.connect(self.stack.process)
        self.stack.set_canvas.connect(self.set_canvas)
        self.stack.abort.connect(self._abort)
        self.stack.moveToThread(self.worker)
        self.pd = QProgressDialog("Loading layers", "Cancel", 1, len(paths))
        self.pd.setCancelButton(None)
        self.pd.setWindowFlags(~(Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.WindowCloseButtonHint))
        self.pd.setAutoClose(True)

        # Load the tab
        # ==================================================
        self.load()

    def setup_toolbar(self):

        # Scale image button
        act_scale_image = QAction(QIcon.fromTheme("zoom-fit-best"), "Scale image to fit", self.toolbar)
        # act_scale_image.triggered.connect(self.canvas._reset_zoom)
        self.toolbar.addAction(act_scale_image)

        # # Find centre
        # act_find_centre = QAction(QIcon.fromTheme("tools-media-optical-format"), "Reset centre", self.toolbar)
        # act_find_centre.triggered.connect(lambda: self.canvas._reset_centre())
        # self.toolbar.addAction(act_find_centre)

        # # Radial profile button
        # act_radial_profile = QAction(QIcon.fromTheme("object-rotate-left"), "Plot radial profile", self.toolbar)
        # act_radial_profile.triggered.connect(self.canvas.compute_radial_profile)
        # self.toolbar.addAction(act_radial_profile)

        # # Radial plot button
        # act_plot = QAction(QIcon.fromTheme("list-add"), "Plot radial profile", self.toolbar)
        # act_plot.triggered.connect(lambda: self.splitview.plot(self.stack.current_layer))
        # self.toolbar.addAction(act_plot)

        # Dock widget toggle
        act_dock = QAction(QIcon.fromTheme("document-properties"), "Show docking panel", self.toolbar)
        act_dock.triggered.connect(self._toggle_dock)
        self.toolbar.addAction(act_dock)

    @Slot()
    def _toggle_dock(self):
        if self.dock.isVisible():
            self.dock.hide()
        else:
            self.dock.show()

    @Slot()
    def _set_threshold(
        self,
        update: bool = True,
    ):

        self.dock._update_threshold()
        self.stack._update_threshold(self.dock.threshold)

    # @Slot()
    # def _set_smoothness(
    #     self,
    #     update: bool = True,
    # ):

    #     self.dock._update_smoothness()
    #     # self.stack._update_smoothness(self.dock.smoothness)
    #     self.canvas._make_contours()

    #     for idx in range(len(self.stack.current_layer.contours)):
    #         self.stack.current_layer.contours[idx] = utils.smoothen(self.stack.current_layer.contours[idx], self.stack.smoothness)

    #     self.canvas._draw(auto_range=True)

    def load(self):

        self.load_stack.emit()

    def _abort(self):
        self.pd.close()
        self.worker.quit()

    @Slot()
    def set_canvas(self):

        self.worker.quit()
        self.canvas.set_stack(self.stack, auto_range=True)
