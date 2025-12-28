from pathlib import Path

import numpy as np

from concurrent.futures import ProcessPoolExecutor

import tempfile

from PySide6.QtCore import Slot
from PySide6.QtCore import Signal
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QFileDialog

import pandas as pd

import shutil

from mimetica import conf
from mimetica import logger
from mimetica import Layer


class Stack(QObject):
    update_progress = Signal(Path)
    set_canvas = Signal()
    abort = Signal()

    @staticmethod
    def make_layer(
        path: str | Path,
    ):
        """
        Create a layer for the given image.

        Args:
            path: Path to the image file.

        Returns:
            A layer instance.
        """
        return Layer(path)

    def __init__(
        self,
        paths: list[Path],
        threshold: int = 70,
        *args,
        **kwargs,
    ):
        """
        Create a stack of images.

        Args:
            paths: A list of image paths.
            threshold: Binarisation threshold (only for RGB or greyscale images; currently unused)
        """
        super().__init__(*args, **kwargs)

        # Save the parameters
        # ==================================================
        self.paths = sorted(paths)
        self.threshold = threshold

        # Other attributes
        # ==================================================
        self.layers = []
        self.active_layer = 0

        # Create a merged stack
        # ==================================================
        self.merged: np.ndarray = None

    def _set_active_layer(
        self,
        index: int = 0,
    ):
        """
        Set the layer to the given index.

        Args:
            index: Layer index.
        """
        self.active_layer = index

    @Slot(int)
    def _compute_radial_profile(
        self,
        segments: int,
    ):
        """
        Update the radial profile with a new number of segments.

        Args:
            segments: Number of radial segments.
        """

        for layer in self.layers:
            layer.compute_radial_profile()
        self.plot.emit()

    @Slot(int)
    def _compute_phase_profile(
        self,
        segments: int,
    ):
        """
        Update the phase profile with a new number of segments.

        Args:
            segments: Number of phase segments.
        """
        for layer in self.layers:
            layer.compute_phase_profile()

        self.plot.emit()

    @Slot()
    def _export_profile_statistics(self):
        """
        Export the mean and standard deviation of the
        radial and phase profiles.
        """

        radial_profiles = np.vstack([layer.radial_profile for layer in self.layers])
        phase_profiles = np.vstack([layer.phase_profile for layer in self.layers])

        radial_mean = radial_profiles.mean(axis=0)
        radial_sd = radial_profiles.std(axis=0)
        phase_mean = phase_profiles.mean(axis=0)
        phase_sd = phase_profiles.std(axis=0)

        with tempfile.TemporaryDirectory() as td:
            tmp_fname = Path(td) / "stats.xlsx"

            with pd.ExcelWriter(tmp_fname, engine="openpyxl") as writer:

                radial_df = pd.DataFrame(
                    {
                        "Normalised radius [a.u.]": np.linspace(
                            0.0, 1.0, conf.radial_samples + 1
                        )[1:],
                        "Radial mean": radial_mean,
                        "Radial SD": radial_sd,
                    }
                )
                radial_df.to_excel(
                    writer, sheet_name="Radial profile stats", index=False
                )

                phase_df = pd.DataFrame(
                    {
                        "Angle [deg]": np.linspace(
                            0.0, 360.0, conf.phase_samples, endpoint=False
                        ),
                        "Phase mean": phase_mean,
                        "Phase SD": phase_sd,
                    }
                )
                phase_df.to_excel(writer, sheet_name="Phase profile stats", index=False)

            save_fname = QFileDialog.getSaveFileName(
                None,
                "Save file...",
                filter="xlsx (*.xlsx)",
            )[0]

            if save_fname is not None:
                save_fname = Path(save_fname)
                shutil.copy2(tmp_fname, save_fname)
                logger.info(
                    f"Statistics exported to '{save_fname.resolve().absolute()}'"
                )

    @Slot()
    def process(self):
        """
        Process a stack of images.
        """
        logger.info(f"Loading stack...")

        # Layer factory
        # ==================================================
        with ProcessPoolExecutor() as executor:
            for layer in executor.map(Stack.make_layer, self.paths):
                self.layers.append(layer)
                self.update_progress.emit(layer.path)

        self._set_active_layer()

        # Calibrate the stack based on all the images
        # ==================================================
        for layer in self.layers:

            if self.merged is None:
                self.merged = layer.image.copy().astype(np.float32)
            else:
                self.merged += layer.image

        # Scale the merged stack
        # ==================================================
        minval = self.merged.min()
        maxval = self.merged.max()
        self.merged = (255 * (self.merged - minval) / (maxval - minval)).astype(
            np.uint8
        )

        # Set the stack on the canvas
        # ==================================================
        self.set_canvas.emit()
