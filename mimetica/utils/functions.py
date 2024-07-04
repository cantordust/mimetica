import typing as tp

# --------------------------------------
import cv2 as cv

# --------------------------------------
import skimage.morphology as skmorph

# --------------------------------------
import shapely as shp
from shapely.geometry import Polygon

# --------------------------------------
import numpy as np

# --------------------------------------
from PySide6.QtGui import QColor
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QColorDialog


def make_contour(image: np.ndarray):
    contours, hierarchy = cv.findContours(
        image, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE
    )
    contours = [c[:, 0] for c in contours]
    return Polygon(contours[0]).simplify(1, preserve_topology=True)


def smoothen(
    contour: Polygon,
    smoothness: int,
):
    return Polygon(
        contour.buffer(
            smoothness,
            join_style=1,
            single_sided=True,
        ).buffer(
            -smoothness,
            join_style=1,
            single_sided=True,
        )
    )


def compute_mbc(image: np.ndarray):

    return shp.minimum_bounding_circle(
        make_contour(skmorph.convex_hull_image(image).astype(np.ubyte))
    )


def as_rgba(colour: QColor) -> str:
    """
    Convert a QColor isntance (including opacity) into RGBA format
    suitable for use in a stylesheet.

    The R, G and B values are between 0 and 255, and the opacity
    is between 0 and 1.

    Args:
        colour (QColor):
            A QColor instance.

    Returns:
        str:
            RGBA-formatted string.
    """
    return ",".join(
        str(c)
        for c in [
            colour.red(),
            colour.green(),
            colour.blue(),
            colour.alphaF(),
        ]
    )


def as_hex(colour: QColor) -> str:
    """
    Convert a QColor isntance (including opacity) into hex format.

    Args:
        colour (QColor):
            A QColor instance.

    Returns:
        str:
            The hex representation.
    """
    return "#" + "".join(
        [
            f"{colour.red():02X}",
            f"{colour.green():02X}",
            f"{colour.blue():02X}",
            f"{colour.alpha():02X}",
        ]
    )


def get_colour(
    initial: QColor = None,
    parent: QObject = None,
    title: str = "Pick a colour",
) -> QColor:
    """
    Get a QColor from a QColorDialog.

    Returns:
        QColor:
            The selected colour.
    """

    return QColorDialog.getColor(
        initial,
        parent,
        title,
        QColorDialog.ColorDialogOption.ShowAlphaChannel,
    )
