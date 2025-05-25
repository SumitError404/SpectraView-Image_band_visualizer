# SpectraView  -->RGB and Multi-Band Image Visualizer

A desktop application built with Python and PyQt5 to load, visualize, and perform basic analysis on multi-band raster images (like GeoTIFF) and standard image formats. It allows users to map spectral bands to RGB channels, view individual bands, apply common remote sensing filters, adjust image properties, and perform basic manipulations.

## Features

* **Load Multiple Formats:** Opens multi-band GeoTIFFs (`.tif`, `.tiff`), JPEG (`.jpg`, `.jpeg`), and PNG (`.png`) files using Rasterio.
* **Custom RGB Composites:** Interactively select source bands for Red, Green, and Blue display channels.
* **Single Band View:** Display any individual band in grayscale.
* **Predefined Filters:** Apply common filters and indices:
    * Natural Color
    * False Color Infrared (Vegetation Highlight)
    * Urban/Soil Composite
    * Water Bodies Enhancement
    * NDVI (Normalized Difference Vegetation Index)
    * SAVI (Soil-Adjusted Vegetation Index)
    * EVI (Enhanced Vegetation Index)
* **Image Adjustments:** Real-time sliders for Brightness, Contrast, and Sharpness.
* **Basic Manipulations:** Toolbar actions for Zoom In/Out, Rotate (90° clockwise), and Center Crop.
* **Save Current View:** Export the displayed image (with all adjustments) to PNG or JPG format.
* **Interactive GUI:** User-friendly interface built with PyQt5.

## Requirements

* **Python:** 3.6+
* **Libraries:**
    * `PyQt5`
    * `rasterio`
    * `numpy`
    * `Pillow`

## Installation

1.  **Get the script:** Ensure you have the `band_visualizer.py` Python script file in a directory on your computer.

2.  **Create and activate a virtual environment (Recommended):**
    Open your terminal or command prompt, navigate to the directory containing the script, and run:

    ```bash
    # For Linux/macOS
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```
    *(You only need to create the `venv` once. Activate it each time you want to run the script in a new terminal session.)*

3.  **Install the required libraries:**
    With your virtual environment activated, run:
    ```bash
    pip install PyQt5 rasterio numpy Pillow
    ```

## Usage

1.  **Run the application:**
    Navigate to the directory containing the script in your terminal (make sure your virtual environment is activated) and run:
    ```bash
    python band_visualizer.py
    ```

2.  **Using the Tool:**
    * Click **"Upload Image"** (toolbar icon) to load a supported image file. A dialog confirms the number of bands loaded.
    * To view an **RGB composite**: Select bands using the "Red:", "Green:", and "Blue:" dropdowns, then click the **"Show Composite RGB Image"** button.
    * To view a **single band**: Select a band from the "View Single Band:" dropdown. The display updates automatically.
    * To apply a **filter**: Choose one from the "Apply Filter:" dropdown. The display updates automatically. Select "None" to disable filters.
    * Use the **sliders** to adjust Brightness, Contrast, and Sharpness.
    * Use the **toolbar buttons** (Zoom In, Zoom Out, Rotate, Crop Center) to manipulate the view.
    * Click **"Save Image"** (toolbar icon) to save the currently displayed image to a PNG or JPG file.
