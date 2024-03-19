# Overview
Mimetica is a software package for analysing microCT scans. It can load a stack of scans and compute the radial and phase density profiles of each layer. The results can also be exported to CSV for further analysis. Mimetica was written in Python using PySide6 as the GUI framework.

# Installation
After cloning this repository, Mimetica can be installed using Conda using the provided `environment.yml` file.

```bash
$> git clone <mimetica-repo> mimetica
$> cd mimetica
$> conda env create -f environment.yml
$> conda activate mimetica
$> mimetica
```

The last command launches the program. A more user-friendly launcher is on the ToDo list.
