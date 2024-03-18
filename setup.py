from setuptools import setup

setup(
    name="Mimetica",
    description="A package for radial profile analysis of microCT scans",
    author="Alexander Hadjiivanov",
    version=f"0.2.0",
    packages=["mimetica"],
    license="MIT",
    long_description=open("README.md").read(),
    entry_points={
        "console_scripts": [
            "mimetica = mimetica.main:run",
        ],
    },
)
