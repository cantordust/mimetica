import pyqtgraph as pg
from PySide6.QtGui import QPainter
from PySide6.QtGui import QColor


class Contour(pg.CircleROI):
    """
    Circular contour subclass.
    """

    def __init__(self, pos, radius, **args):

        args.setdefault("movable", False)
        args.setdefault("resizable", False)
        args.setdefault("removable", False)
        args.setdefault("rotatable", False)
        args.setdefault("pen", pg.mkPen(color=QColor(255, 0, 0, 255), width=1.5))

        super().__init__(pos, 1, **args)
        for h in self.getHandles():
            self.removeHandle(h)

        self.setSize(2 * radius, (0.5, 0.5), update=True, finish=True)
