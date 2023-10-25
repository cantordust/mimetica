from typing import *

# --------------------------------------
from pathlib import Path

# --------------------------------------
from PySide6.QtCore import (
    Slot,
)

# --------------------------------------
import cv2 as cv

# --------------------------------------
import skimage as ski
import skimage.filters as skf
import skimage.measure as skm
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
from scipy.ndimage import binary_fill_holes as bfh

# --------------------------------------
import numpy as np

# --------------------------------------
from mimetica import logger
from mimetica import utils


class Layer:
    def __init__(
        self,
        path: Path,
        image: np.ndarray,
        threshold: int,
    ):
        self.path = Path(path).resolve().absolute()
        self.image = image
        self.threshold = threshold

        # Various properties of the image
        # ==================================================
        # Minimal bounding circle
        self.mbc = utils.compute_mbc(self.image)
        self.centre = np.array(list(reversed(shp.centroid(self.mbc).coords)), dtype=np.uint32)[0]
        self.mbc_radius = int(shp.minimum_bounding_radius(self.mbc))
        self.contours = []
        self.outlines = []
        self.radial_profiles = []
        self.phase_profiles = []
        self.rings = []
        self.radii = []
        self.spokes = []
        self.mask = self.make_mask()

        # Extract contour, centre, etc.
        # ==================================================
        self.process()

    def make_mask(self):

        Y, X = np.ogrid[: self.image.shape[0], : self.image.shape[1]]

        mask = np.sqrt((X - self.centre[0]) ** 2 + (Y - self.centre[1]) ** 2)

        mask = ((2**16 - 1) * np.exp(- 3 * mask / mask.max())).astype(np.uint32)

        return mask

    def process(self):
        self.compute_radial_profile()
        self.compute_phase_profile()

    def set_threshold(self, threshold: int):

        self.threshold = threshold

    # def _compute_mbc(
    #     self,
    #     reset: bool = False,
    # ):

    #     # Create contour lines from the MBC
    #     # ==================================================
    #     if reset:
    #         self.contours.clear()

    #     self.contours.append(self.mbc)

    @Slot()
    def compute_phase_profile(
        self,
        segments: int = 360,
    ):

        angles = np.linspace(0, 360, segments, endpoint=False)

        # print(f"==[ angles: {angles}")

        cx, cy = self.centre

        # Create a series of lines originating at the centre
        # and rotate them so they are evenly spaced
        ls = LineString([(cx, cy), (2 * self.image.shape[0], cy)])
        lines = [LineString(sha.rotate(ls, angle, origin=(cx, cy))) for angle in angles]

        # Compute the intersections of the lines and the bounding box.
        # That will give us the coordinates of the end points of the segments
        intersections = []
        for ln in lines:
            ict = np.array(ln.intersection(self.mbc).coords, dtype=np.uint32)[-1]
            # coords = list(ict.geoms[0].coords) + list(ict.geoms[-1].coords)
            # if isinstance(ict, (MultiLineString, GeometryCollection, MultiPoint)):
            #     coords = []
            #     for g in ict.geoms:
            #         coords.extend(g.coords)
            #     # print(f"==[ coords: {coords}")

            # elif isinstance(ict, Polygon):

            #     print(f"==[ ict: {ict.boundary.coords}")

            #     raise SystemExit()

            # else:

            # intersections.extend([list(coords) for coords in Polygon(ict).exterior.coords])
            # coords = np.array(ict.coords.xy, dtype=np.uint32)
            # print(f"==[ coords: {coords}")

            # intersections.extend(coords[0])
            # print(f"==[ coords: {cx, cy, ict}")

            spoke_coords = skd.line(cy, cx, ict[1], ict[0])

            material = np.count_nonzero(self.image[spoke_coords[0], spoke_coords[1]])
            self.spokes.append(spoke_coords)

            # print(f"==[ {idx}: {material}")

            self.phase_profiles.append(material / self.mbc_radius)

        # # Correct the order of intersections to follow the angles (0 ~ 360)
        # mid = len(intersections) // 2
        # intersections = intersections[::2] + intersections[1::2]
        # intersections = list(reversed(intersections[:mid])) + list(reversed(intersections[mid:]))
        # intersections = np.array(intersections).astype(np.uint32)

        # self.spokes = [
        #     shg.LineString(
        #         (
        #             (cx, cy),
        #             (ix, iy),
        #         )
        #     )
        #     for ix, iy in intersections
        # ]

    @Slot()
    def compute_radial_profile(
        self,
        segments: int = 32,
    ):
        factors = np.linspace(0, 1, segments, endpoint=False)

        self.contours.clear()
        self.rings.clear()
        self.radial_profiles.clear()

        outer_coords = np.array(self.mbc.exterior.coords).astype(np.uint32)
        for idx, factor in enumerate(factors):

            contour = sha.scale(self.mbc, xfact=factor, yfact=factor, origin=Point(self.centre))
            self.radii.append(int(self.mbc_radius * factor))

            # binary_layer = np.zeros_like(self.binary_layer)
            # for geom in new_poly.exterior.coords:
            inner_coords = np.array(contour.exterior.coords).astype(np.uint32)

            # binary_layer[coords[:, 0], coords[:, 1]] = 255
            self.contours.append(contour)

            # self.radial_layer += ring
            self.outlines.append(inner_coords)

            outer_mask = np.zeros_like(self.image)
            outer_mask[outer_coords[:, 0], outer_coords[:, 1]] = 1

            inner_mask = np.zeros_like(self.image)
            inner_mask[inner_coords[:, 0], inner_coords[:, 1]] = 1

            outer = bfh(outer_mask)
            inner = bfh(inner_mask)

            # print(f"==[ outer: {outer}")

            outer_mask[outer] = True
            inner_mask[inner] = True

            self.rings.append(inner)

            pixels = np.logical_xor(outer_mask, inner_mask)
            material = np.count_nonzero(self.image[pixels])

            # print(f"==[ {idx} ] material: {material}")
            # print(f"==[ {idx} ] pixels: {pixels.sum()}")

            outer = inner
            outer_coords = inner_coords

            self.radial_profiles.append(material / pixels.sum())

            ring = np.zeros_like(self.image)
            ring[pixels] = int(2**16 - 1 * np.exp(-2 * idx / len(factors)))

            self.rings.append(ring)
