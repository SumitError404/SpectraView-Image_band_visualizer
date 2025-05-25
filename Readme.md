# **SpectraView**

*A Desktop Application for RGB & Multi-Band Image Visualization and Analysis*

![App Screenshot](https://github.com/user-attachments/assets/ba1a96f0-f939-4b14-bb5a-82122ed4379b)

---

## 🛰️ Overview

**SpectraView** is a Python-based desktop application built with **PyQt5** that enables users to load, visualize, and perform basic analysis on **multi-band raster images** (e.g., GeoTIFFs) as well as standard image formats like JPEG and PNG.

It supports **interactive RGB band compositing**, **grayscale band viewing**, **remote sensing filters**, and **real-time image adjustments**, making it useful for satellite imagery analysts, researchers, students, and geospatial professionals.

---

## 🔍 Features

### 🗂️ **Image Support**

* Load **multi-band raster images**: `.tif`, `.tiff` (GeoTIFF)
* Load **standard images**: `.jpg`, `.jpeg`, `.png`

### 🌈 **Visualization Options**

* **Custom RGB Composite**: Choose any three bands as Red, Green, Blue
* **Single Band Viewer**: Visualize any single band in grayscale

### 🎨 **Remote Sensing Filters**

* **Natural Color**
* **False Color Infrared** (vegetation)
* **Urban/Soil Composite**
* **Water Body Enhancement**
* **NDVI** (Normalized Difference Vegetation Index)
* **SAVI** (Soil-Adjusted Vegetation Index)
* **EVI** (Enhanced Vegetation Index)

### 🧰 **Image Adjustment & Tools**

* **Real-Time Controls**:

  * Brightness
  * Contrast
  * Sharpness
* **Basic Tools**:

  * Zoom In / Zoom Out
  * Rotate 90° Clockwise
  * Center Crop
* **Save Output**:

  * Export current view (including enhancements) to `.png` or `.jpg`

### 🖥️ **User-Friendly GUI**

* Built with **PyQt5**
* Intuitive layout with clear toolbar icons and control panels

---

## 📦 Requirements

* **Python**: 3.6+
* **Libraries**:

  * `PyQt5`
  * `rasterio`
  * `numpy`
  * `Pillow`

---

## 🛠️ Installation

1. **Clone or download** the repository and ensure you have `band_visualizer.py` in your project folder.

2. **Set up a virtual environment (recommended)**:

   ```bash
   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate

   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install the required packages**:

   ```bash
   pip install PyQt5 rasterio numpy Pillow
   ```

---

## ▶️ Usage

1. **Launch the app**:

   ```bash
   python band_visualizer.py
   ```

2. **Using the GUI**:

   * 📁 **Upload Image**: Use the toolbar icon to load a `.tif`, `.jpg`, or `.png` file.
   * 🎛️ **RGB Composites**:

     * Use dropdowns to assign bands to Red, Green, Blue.
     * Click **“Show Composite RGB Image”** to visualize.
   * 🖤 **Single Band View**:

     * Choose any band from the dropdown to view in grayscale.
   * 🧪 **Apply Filters**:

     * Choose from vegetation, urban, water filters.
     * Select **“None”** to disable filtering.
   * 🎚️ **Adjustments**:

     * Move sliders for Brightness, Contrast, and Sharpness.
   * 🔧 **Toolbar Tools**:

     * Zoom, Rotate, and Crop tools for quick manipulations.
   * 💾 **Save Image**:

     * Click “Save Image” icon to export current view.

---

## 🖼️ Screenshots

<p float="left">
  <img width="494" alt="Screenshot 1" src="https://github.com/user-attachments/assets/ba1a96f0-f939-4b14-bb5a-82122ed4379b" />
  <img width="320" alt="Screenshot 2" src="https://github.com/user-attachments/assets/d31e3bb3-84af-4b60-9440-b8a6ec688eb3" />
</p>

<p float="left">
  <img width="1191" alt="Screenshot 3" src="https://github.com/user-attachments/assets/0798fee0-449c-43b3-9386-459646ceeb05" />
  <img width="1191" alt="Screenshot 4" src="https://github.com/user-attachments/assets/68b59cb0-ab83-4b6f-b1ce-3d11816bc3ab" />
</p>








