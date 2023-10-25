from typing import *

# --------------------------------------
import sys

# --------------------------------------
from PySide6.QtCore import (
    Qt,
    Slot,
    QThread,
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
from mimetica import Tab
from mimetica import utils


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("Mimetica")

        # # The display canvas
        # # ==================================================
        # self.canvas = Canvas()

        # # Splitview widget
        # # ==================================================
        # self.splitview = SplitView(self.canvas)
        # self.splitview.setSizes((1, 1))
        # self.setCentralWidget(self.splitview)

        # Tab widget
        # ==================================================
        self.tabs = QTabWidget()
        self.setup_tabs()
        self.setCentralWidget(self.tabs)

        # Status bar
        # ==================================================
        self.pixmap = QPixmap()
        self.status = self.statusBar()
        self.status.showMessage("Ready")
        self.setup_statusbar()

        # Menu
        # ==================================================
        self.menu = self.menuBar()
        self.main_menu = self.menu.addMenu("File")
        self.setup_menu()

        # # Toolbar
        # # ==================================================
        # self.toolbar = QToolBar(floatable=False, movable=False)
        # self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)

        # Window dimensions
        # ==================================================
        geometry = self.screen().availableGeometry()

        # Slots & signals
        # ==================================================
        # self.dock.threshold_spinbox.valueChanged.connect(self._set_threshold)
        # self.canvas.update_plots.connect(lambda layer: self.splitview.plot(layer))
        # self.dock.smoothness_spinbox.valueChanged.connect(self._set_smoothness)


    def setup_tabs(self):

        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self._remove_tab)
        # self.tabs.addTab(Tab(), "34")
        # self.tabs.addTab(Tab(), "53")
        # self.tabs.addTab(Tab(), "19")

    def setup_menu(self):

        # Main menu
        # ==================================================

        # Open file
        act_open_file = QAction("Open file", self)
        act_open_file.triggered.connect(self.open_file)
        self.main_menu.addAction(act_open_file)

        # Open stack
        act_open_stack = QAction("Open stack", self)
        act_open_stack.triggered.connect(self.open_stack)
        self.main_menu.addAction(act_open_stack)

        # Exit
        act_exit = QAction("Exit", self)
        act_exit.setShortcut(QKeySequence.Quit)
        act_exit.triggered.connect(self.close)
        self.main_menu.addAction(act_exit)

    def setup_statusbar(self):

        pass

    def open_file(
        self,
        file: Path = None,
    ):

        if not file:
            filter = [
                "BMP (*.bmp)",
                "PNG (*.png)",
                "TIFF (*.tif *.tiff)",
                "JPEG (*.jpg *.jpeg)",
            ]

            filter = ";;".join([f"*.{f}" for f in filter])

            file = QFileDialog.getOpenFileName(
                self,
                "Open file...",
                filter=filter,
            )[0]

            if file == "":
                QMessageBox.information(
                    self,
                    self.windowTitle(),
                    f"Invalid file name",
                )
                return

        self.open_stack([file])

    def open_stack(
        self,
        stack: Path = None,
    ):

        if not stack:

            stack = QFileDialog.getExistingDirectory(
                self,
                "Open stack...",
            )
            stack = Path(stack)

        if stack.is_file():
            QMessageBox("Please select a valid stack")
            return

        extensions = (
            ".bmp",
            ".tif",
            ".tiff",
            ".png",
            ".jpg",
            ".jpeg",
        )

        paths = []
        for file in stack.iterdir():
            if str(file).startswith("."):
                continue

            if file.suffix.lower() in extensions:
                paths.append(file.resolve().absolute())

        if len(paths) == 0:
            QMessageBox("The specified path does not contain any images.")
            return

        self._add_tab(paths)

    # @Slot()
    # def _toggle_dock(self):
    #     if self.dock.isVisible():
    #         self.dock.hide()
    #     else:
    #         self.dock.show()

    # @Slot()
    # def _set_threshold(
    #     self,
    #     update: bool = True,
    # ):

    #     self.dock._update_threshold()
    #     self.stack._update_threshold(self.dock.threshold)

    @Slot(int)
    def _remove_tab(
        self,
        pos: int,
    ):
        if pos < self.tabs.count():
            self.tabs.removeTab(pos)

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

    def _add_tab(
        self,
        paths: List[Path],
    ):

        tab = Tab(paths)
        # self.stack = Stack(paths[:10])
        # self.canvas.set_stack(self.stack, auto_range=True)
        name = paths[0].parent.name
        idx = self.tabs.addTab(tab, name)
        self.tabs.setCurrentIndex(idx)


def run():
    app = QApplication([])

    mw = MainWindow()
    mw.resize(1200, 800)
    mw.show()

    root_dir = Path(__file__).parent.parent.parent
    stack = root_dir / "local/image_stacks/34"

    # mw.open_stack(stack)

    sys.exit(app.exec())
