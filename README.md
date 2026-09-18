# ![P4Struct Icon](./images/app%20icon.ico) P4Struct —— Program for Structural Design
![Version](https://img.shields.io/badge/Version-1.0-yellow.svg) [![License](https://img.shields.io/badge/License-AGPLv3.0-green.svg)](LICENSE) [![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/) [![uv](https://img.shields.io/badge/uv-0.9+-orange.svg)](https://docs.astral.sh/uv/)
## 1. Description
## 1. Description
An **open-source** structural design software. P4Struct is built on a multi-layered architecture that couples an interactive interface with a database system, enabling efficient data management and workflow execution. Taking mesh models as input, P4Struct enables a complete design workflow encompassing **preprocessing, finite element analysis, topology optimization, and post-processing**, ultimately generating STL models.

![Core modules of P4Struct](./images/core%20modules.png "Core modules of P4Struct")

## 2. Core functionalities

- 🎨 Modern GUI built with PySide6
- 🎨 Interactive visualization built with VTK
- 🎨 Pre/post-processing workflow
- 💾 Data management with SQLite3 and H5py
- 📊 FEA:
    - ⚡2D/3D linear elastic
    - ⚡multiple element types(truss\plane\solid\shell)
    - ⚡multiple analysis steps
    - ⚡PARDISO slover
    - ⚡Loop-level parallelism
- 🧩 Topology optimization
    - ⚡SIMP\RAMP
    - ⚡strain energy\volume\von Mises stress
    - ⚡ADAM\MMA\GCMMA
    - ⚡filters
    - ⚡binarization
    - ⚡smoothing
    - ⚡STL export

## 3. Download

⚠️***Because the repository contains large files, downloading the ZIP file directly will not give you the complete content.***

    Solution 1: Use Git and LFS to download.
    
    Solution 2: Navigate to the main page of the large file and download it individually (i.e., click 'Download raw file')

## 4. Installation

### 4.1 Source Code

See .\doc\Install.

### 4.2 Executable File

Step 1: Download the compressed file 'P4SINC.zip' and extract it to any disk that you assigned.

Step 2: Find the 'P4Struct.exe' file, create a shortcut to the desktop, and then double-click it to run (Run as administrator for the first time).

Step 3: By default, a working directory named 'P4STemp' is created in the installation package directory for storing files.  

Step 4: Finally, you can start using it (The operation video is in the "video demo" folder.).

## 5. Examples

See .\examples.

## 6. Contact information
This is an initial version which may contain bugs.

Please contact us promptly if you encounter any issues.

E-mail: <jihuaiwang@outlook.com>

## 7. Reference

《P4Struct: An integrated topology optimization software framework with a unified design workflow》
