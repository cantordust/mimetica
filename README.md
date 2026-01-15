# Overview
Mimetica is a software package for analysing microCT scans. It can load a stack of scans and compute the radial and phase profiles of the material fraction of each layer. The results can also be exported to CSV for further analysis. Mimetica was written in Python using PySide6 as the GUI framework.

# Installation

Create a new Python environment and run

```bash
pip install mimetica
```

After that, you can launch the program from the terminal:

```bash
mimetica
```

You can see the available CLI options with the `--help` argument:

```bash
mimetica --help
```

You should see the following output:

```bash
Usage: mimetica [OPTIONS]

Input: [mutually exclusive]
  Open one or more images.
  -i, --image TEXT  Open a single image.
  -s, --stack TEXT  Open a stack (directory of images).

Other options:
  --help            Show this message and exit.
```

For instance, to open a single image or a stack (a directory of images) from the CLI:

```bash
mimetica -s <path_to_directory>
```
