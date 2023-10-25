from typing import *

# --------------------------------------
from pathlib import Path

# --------------------------------------
import cv2 as cv

# --------------------------------------
import skimage as ski
import skimage.filters as skf
import skimage.measure as skm
import skimage.morphology as skmorph
import skimage.draw as skd

# --------------------------------------
import shapely as shp
import shapely.affinity as sha
import shapely.geometry as shg
from shapely.ops import split
from shapely.ops import snap
from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely.geometry import MultiPoint
from shapely.geometry import LineString
from shapely.geometry import MultiLineString
from shapely.geometry import GeometryCollection

# --------------------------------------
import time

# --------------------------------------
from scipy.ndimage import binary_fill_holes as bfh

# --------------------------------------
import numpy as np

# --------------------------------------
from mimetica import logger


def make_contour(image: np.ndarray):
    contours, hierarchy = cv.findContours(image, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    contours = [c[:, 0] for c in contours]
    return Polygon(contours[0]).simplify(1, preserve_topology=True)

def smoothen(contour: Polygon, smoothness: int):
    return Polygon(contour.buffer(smoothness, join_style=1, single_sided=True).buffer(-smoothness, join_style=1, single_sided=True))

def compute_mbc(image: np.ndarray):

    return shp.minimum_bounding_circle(make_contour(skmorph.convex_hull_image(image).astype(np.uint8)))
