from setuptools import setup

# --------------------------------------
import enum


class Version(enum.IntEnum):
    MAJOR = 0
    MINOR = 1
    PATCH = 0


setup(
    name="Mimetica",
    author="Chris Broeckhoven | Alexander Hadjiivanov",
    version=f"{Version.MAJOR}.{Version.MINOR}.{Version.PATCH}",
    packages=["mimetica"],
    install_requires=[
        "pyside6",
        "loguru",
        "python-decouple",
        "numpy",
        "dotmap",
        "pyqtgraph",
        "opencv-python",
        "scikit-image[optional]",
        "shapely",
        "scipy",
    ],
    license="MIT",
    long_description=open("README.md").read(),
    entry_points={
        "console_scripts": [
            "mimetica = mimetica.main:run",
        ],
    },
)
