from typing import *

# --------------------------------------
import cv2 as cv

# --------------------------------------
import skimage.morphology as skmorph

# --------------------------------------
import shapely as shp
from shapely.geometry import Polygon

# --------------------------------------
import numpy as np


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
