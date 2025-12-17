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
        pad = 2
        self.image = np.pad(
            image,
            ((pad, pad), (pad, pad)),
            mode="constant",
            constant_values=0,
        )

        # Image properties
        # ==================================================
        # Minimal bounding circle
        self.mbc, self.mbr = utils.compute_minimal_bounding_circle(self.image)
        # Use np.roll to swap h and w for the centre.
        self.centre = np.roll(
            np.array(self.mbc.centroid.xy, dtype=np.uint32).flatten(), 1
        )
        self.radius = int(shp.minimum_bounding_radius(self.mbc))
        self.radial_range = np.empty([])
        self.radial_profile = np.empty([])
        self.phase_range = np.empty([])
        self.phase_profile = np.empty([])

        # Extract contour, centre, etc.
        # ==================================================
        self.process()

    def make_mask(self) -> np.ndarray:
        """
        Create a mask for this layer.

        Returns:
            A mask as a NumPy array.
        """
        Y, X = np.meshgrid[: self.image.shape[0], : self.image.shape[1]]
        mask = np.sqrt((X - self.centre[0]) ** 2 + (Y - self.centre[1]) ** 2)
        mask = np.exp(-3 * mask / mask.max())
        return mask

    def process(self):
        """
        Process this layer.
        For now, this is limited to computing the radial and phase profiles.
        """
        self.compute_radial_profile()
        self.compute_phase_profile()

    @Slot()
    def compute_radial_profile(self):
        # Create an empty array
        self.radial_profile = np.zeros((conf.radial_samples,))
        self.radial_range = np.linspace(0, 1, len(self.radial_profile))
        self.radii = np.linspace(1.0, self.radius, conf.radial_samples)

        for idx, radius in enumerate(self.radii):
            # Create a virtual circle with the right radius
            rr, cc = skd.circle_perimeter(
                self.centre[0], self.centre[1], int(radius), method="andres"
            )
            # Find out how much material is sampled by the circle
            # and compute the density
            circle = self.image[rr, cc]
            material = np.count_nonzero(circle)
            self.radial_profile[idx] = material / circle.size

    @Slot()
    def compute_phase_profile(self):
        # Coordinates of the central point
        (cx, cy) = self.centre

        # Get the coordinates of each pixel of the MBC
        # (cont_xs, cont_ys) = skd.circle_perimeter(cx, cy, self.radius)

        # Compute the angles from the pixel coordinates.
        # _cont_xs = cont_xs - cx
        # _cont_ys = cont_ys - cy
        # ratios = _cont_xs / np.sqrt(_cont_xs**2 + _cont_ys**2)
        # angles = np.arccos(ratios)
        # angles = np.where(_cont_ys < 0, 2 * np.pi - angles, angles)
        angles = conf.phase_samples

        # X and Y datasets for the phase profile
        self.phase_range = np.linspace(0, 360, angles, endpoint=False)
        self.phase_profile = np.zeros_like(self.phase_range)

        # Draw lines ('spokes') from the centre to the MBC, each rotated by
        # an angle determined by the number of phase samples.
        spokes = [
            shp.affinity.rotate(
                shp.LineString(
                    [
                        shp.Point(*self.centre),
                        shp.Point(self.centre[0], self.centre[1] + self.mbr + 1),
                    ],
                ),
                angle,
                origin=shp.Point(*self.centre),
            )
            for angle in range(angles)
        ]

        mbc_rr, mbc_cc = utils.draw_sorted_circle(self.centre, self.mbr)

        circle = shp.LineString(zip((mbc_rr).tolist(), (mbc_cc).tolist()))
        endpoints = [
            np.array(spoke.intersection(circle).coords.xy, dtype=np.uint32)
            .flatten()
            .tolist()
            for spoke in spokes
        ]

        # Compute the X and Y coordinates for the pixels
        # corresponding to the angles calculated above
        # end_xs = (self.radius * np.cos(angles) + cx).astype(np.int32)
        # end_ys = (self.radius * np.sin(angles) + cy).astype(np.int32)

        # for idx, (end_x, end_y) in enumerate(zip(cont_ys, cont_xs)):
        for idx, angle in enumerate(self.phase_range):
            (end_x, end_y) = endpoints[idx]
            # Create a virtual line from the centre to the contour
            rr, cc = np.array(skd.line(cx, cy, end_x, end_y))
            # Find out how much material is sampled by the line
            # and compute the density
            line = self.image[rr, cc]
            material = np.count_nonzero(line)
            self.phase_profile[idx] = material / line.size
