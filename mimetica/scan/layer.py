from pathlib import Path

from PySide6.QtCore import Slot

import skimage as ski
import skimage.draw as skd

import shapely as shp

import numpy as np

from mimetica import conf
from mimetica import utils


class Layer:
    def __init__(
        self,
        path: Path,
    ):
        self.path = Path(path).resolve().absolute()

        image = ski.io.imread(str(self.path), as_gray=True)
        image = np.fliplr(image.T)

        # Pad the image to accommodate for the contour
        # ==================================================
        hpad = 1
        wpad = 1

        lpad, rpad = wpad, wpad
        tpad, bpad = hpad, hpad

        self.image = np.pad(
            image,
            ((lpad, rpad), (tpad, bpad)),
            mode="constant",
            constant_values=0,
        )

        # Image properties
        # ==================================================
        # Minimal bounding circle
        self.mbc = utils.compute_minimal_bounding_circle(self.image)
        self.centre = np.array(list(shp.centroid(self.mbc).coords), dtype=np.int32)[0]
        self.radius = int(shp.minimum_bounding_radius(self.mbc))
        self.radial_range = np.empty([])
        self.radial_profile = np.empty([])
        self.phase_range = np.empty([])
        self.phase_profile = np.empty([])

        # Extract contour, centre, etc.
        # ==================================================
        self.process()

    def make_mask(self):
        Y, X = np.meshgrid[: self.image.shape[0], : self.image.shape[1]]
        mask = np.sqrt((X - self.centre[0]) ** 2 + (Y - self.centre[1]) ** 2)
        mask = np.exp(-3 * mask / mask.max())
        return mask

    def process(self):
        self.compute_radial_profile()
        self.compute_phase_profile()

    @Slot()
    def compute_radial_profile(self):
        # Create an empty array
        self.radial_profile = np.zeros((conf.radial_segments,))
        self.radial_range = np.linspace(0, 1, len(self.radial_profile))
        self.radii = np.linspace(1.0, self.radius, conf.radial_segments)

        for idx, radius in enumerate(self.radii):
            # Create a virtual circle with the right radius
            rr, cc = skd.circle_perimeter(self.centre[0], self.centre[1], int(radius))
            # Get the segment of the image covered by that circle
            circle = self.image[rr, cc]
            # Find out how much material there is in that segment
            material = np.count_nonzero(circle)
            # Compute the radial profile
            self.radial_profile[idx] = material / circle.size

    @Slot()
    def compute_phase_profile(self):
        # Coordinates of the central point
        (cx, cy) = self.centre

        # Get the coordinates of each pixel of the MBC
        (cont_xs, cont_ys) = skd.circle_perimeter(cx, cy, self.radius)

        # Compute the angles from the pixel coordinates.
        _cont_xs = cont_xs - cx
        _cont_ys = cont_ys - cy
        ratios = _cont_xs / np.sqrt(_cont_xs**2 + _cont_ys**2)
        angles = np.arccos(ratios)
        angles = np.where(_cont_ys < 0, 2 * np.pi - angles, angles)

        # Due to aliasing, we should eliminate duplicate
        # coordinates which produce the same angles.
        # As a side effect, this sorts the angles.
        angles = np.unique(angles)

        # X and Y datasets for the phase profile
        self.phase_profile = np.zeros_like(angles)
        self.phase_range = 180 * angles / np.pi

        # Compute the X and Y coordinates for the pixels
        # corresponding to the angles calculated above
        end_xs = (self.radius * np.cos(angles) + cx).astype(np.int32)
        end_ys = (self.radius * np.sin(angles) + cy).astype(np.int32)

        # for idx, (end_x, end_y) in enumerate(zip(cont_ys, cont_xs)):
        for idx, (_, end_x, end_y) in enumerate(zip(angles, end_xs, end_ys)):

            # Create a virtual line from the centre to the contour
            rr, cc = np.array(skd.line(cx, cy, end_x, end_y))
            # Get the segment of the image covered by the line
            line = self.image[rr, cc]
            # Find out how much material there is in that segment
            material = np.count_nonzero(line)
            # Compute the phase profile
            self.phase_profile[idx] = material / line.size
