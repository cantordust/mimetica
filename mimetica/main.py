from typing import *

# --------------------------------------
import sys

# --------------------------------------
from PySide6.QtGui import QAction
from PySide6.QtGui import QKeySequence
from PySide6.QtCore import Slot

from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QTabWidget

# --------------------------------------
import multiprocessing as mp

# --------------------------------------
from pathlib import Path

# --------------------------------------
from mimetica import Tab


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("Mimetica")

        # Tab widget
        # ==================================================
        self.tabs = QTabWidget()
        self.setup_tabs()
        self.setCentralWidget(self.tabs)

        # Menu
        # ==================================================
        self.menu = self.menuBar()
        self.main_menu = self.menu.addMenu("File")
        self.setup_menu()

        # Window dimensions
        # ==================================================
        geometry = self.screen().availableGeometry()

        # Slots & signals
        # ==================================================

    def setup_tabs(self):
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self._remove_tab)

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

    def open_file(
        self,
        file_name: Path = None,
    ):
        if not file_name:
            filter = [
                "BMP (*.bmp)",
                "PNG (*.png)",
                "TIFF (*.tif *.tiff)",
                "JPEG (*.jpg *.jpeg)",
            ]

            filter = ";;".join([f"*.{f}" for f in filter])

            file_name = QFileDialog.getOpenFileName(
                self,
                "Open file...",
                filter=filter,
            )[0]

        if file_name != "":
            self.open_stack([file_name])

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

        if stack == "":
            return

        paths = []
        if isinstance(stack, list):
            paths = [Path(p) for p in stack]

        elif isinstance(stack, Path):
            extensions = (
                ".bmp",
                ".tif",
                ".tiff",
                ".png",
                ".jpg",
                ".jpeg",
            )

            for file in stack.iterdir():
                if str(file).startswith("."):
                    continue

                if file.suffix.lower() in extensions:
                    paths.append(file.resolve().absolute())

        if len(paths) != 0:
            self._add_tab(paths)

    @Slot(int)
    def _remove_tab(
        self,
        pos: int,
    ):
        if pos < self.tabs.count():
            self.tabs.removeTab(pos)

    def _add_tab(
        self,
        paths: List[Path],
    ):
        tab = Tab(paths)
        name = paths[0].parent.name
        idx = self.tabs.addTab(tab, name)
        self.tabs.setCurrentIndex(idx)


def run():

    # Set the multiprocessing context
    mp.set_start_method("spawn")

    # The main feature
    app = QApplication([])
    mw = MainWindow()
    # mw.resize(1200, 800)
    mw.showMaximized()
    mw.show()
    sys.exit(app.exec())
