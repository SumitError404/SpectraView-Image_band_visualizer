from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QComboBox, QFileDialog,
    QVBoxLayout, QHBoxLayout, QScrollArea, QMessageBox, QSlider, QToolBar, QAction
)
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5.QtCore import Qt, QSize
from PIL import Image, ImageEnhance
import rasterio
import numpy as np

from image_utils import (
    normalize_band, apply_rgb_composite, apply_single_band,
    apply_filter_logic
)

class BandVisualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RGB and Band Image Visualizer")
        self.resize(1000, 700)

        self.setup_ui()
        self.image_data = None
        self.current_image = None
        self.zoom_factor = 1.0

    def setup_ui(self):
        self.layout = QVBoxLayout(self)

        # Toolbar
        self.toolbar = QToolBar("Tools")
        self.toolbar.setIconSize(QSize(24, 24))
        self.layout.addWidget(self.toolbar)

        self.add_toolbar_actions()

        # Band selectors
        self.band_select_layout = QHBoxLayout()
        self.r_band_combo, self.g_band_combo, self.b_band_combo = QComboBox(), QComboBox(), QComboBox()
        self.band_select_layout.addWidget(QLabel("Red:"))
        self.band_select_layout.addWidget(self.r_band_combo)
        self.band_select_layout.addWidget(QLabel("Green:"))
        self.band_select_layout.addWidget(self.g_band_combo)
        self.band_select_layout.addWidget(QLabel("Blue:"))
        self.band_select_layout.addWidget(self.b_band_combo)
        self.layout.addLayout(self.band_select_layout)

        # Single band viewer
        self.single_band_combo = QComboBox()
        self.layout.addWidget(QLabel("View Single Band:"))
        self.layout.addWidget(self.single_band_combo)
        self.single_band_combo.currentIndexChanged.connect(self.show_single_band)

        # Filter dropdown
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "None", "Vegetation Highlight", "Natural Color", "Urban/Soil",
            "Water Bodies", "Healthy Vegetation Contrast", "NDVI Enhanced",
            "SAVI (Soil-Adjusted Vegetation Index)", "EVI (Enhanced Vegetation Index)"
        ])
        self.filter_combo.currentIndexChanged.connect(self.apply_filter)
        self.layout.addWidget(QLabel("Apply Filter:"))
        self.layout.addWidget(self.filter_combo)

        # Sliders
        self.brightness_slider = self.create_slider("Brightness")
        self.contrast_slider = self.create_slider("Contrast")
        self.sharpness_slider = self.create_slider("Sharpness")

        # Composite button
        self.show_composite_button = QPushButton("Show Composite RGB Image")
        self.show_composite_button.clicked.connect(self.show_rgb_image)
        self.layout.addWidget(self.show_composite_button)

        # Image display area
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.image_label)
        self.layout.addWidget(scroll)

    def create_slider(self, label):
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(50)
        slider.setMaximum(150)
        slider.setValue(100)
        slider.setTickInterval(10)
        slider.valueChanged.connect(self.apply_adjustments)
        self.layout.addWidget(QLabel(label))
        self.layout.addWidget(slider)
        return slider

    def add_toolbar_actions(self):
        actions = {
            "Upload Image": ("document-open", self.load_image),
            "Save Image": ("document-save", self.save_image),
            "Zoom In": ("zoom-in", self.zoom_in),
            "Zoom Out": ("zoom-out", self.zoom_out),
            "Rotate": ("object-rotate-right", self.rotate_image),
            "Crop Center": ("edit-cut", self.crop_image)
        }
        for name, (icon, method) in actions.items():
            action = QAction(QIcon.fromTheme(icon), name, self)
            action.triggered.connect(method)
            self.toolbar.addAction(action)

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.tif *.tiff *.jpg *.jpeg *.png)")
        if file_path:
            try:
                self.src = rasterio.open(file_path)
                self.band_count = self.src.count
                self.image_data = [self.src.read(i) for i in range(1, self.band_count + 1)]
                self.band_names = self.src.descriptions or [f"Band {i+1}" for i in range(self.band_count)]
                self.update_band_selectors()
                QMessageBox.information(self, "Success", f"Loaded image with {self.band_count} band(s).")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load image: {e}")

    def update_band_selectors(self):
        for combo in [self.r_band_combo, self.g_band_combo, self.b_band_combo, self.single_band_combo]:
            combo.clear()
        for i, label in enumerate(self.band_names):
            for combo in [self.r_band_combo, self.g_band_combo, self.b_band_combo, self.single_band_combo]:
                combo.addItem(label, i)

    def show_rgb_image(self):
        r_index = self.r_band_combo.currentData()
        g_index = self.g_band_combo.currentData()
        b_index = self.b_band_combo.currentData()
        self.current_image = apply_rgb_composite(self.image_data, r_index, g_index, b_index)
        self.zoom_factor = 1.0
        self.apply_adjustments()

    def show_single_band(self):
        band_index = self.single_band_combo.currentData()
        self.current_image = apply_single_band(self.image_data, band_index)
        self.zoom_factor = 1.0
        self.apply_adjustments()

    def apply_adjustments(self):
        if self.current_image is None:
            return
        img = self.current_image.copy()
        img = ImageEnhance.Brightness(img).enhance(self.brightness_slider.value() / 100.0)
        img = ImageEnhance.Contrast(img).enhance(self.contrast_slider.value() / 100.0)
        img = ImageEnhance.Sharpness(img).enhance(self.sharpness_slider.value() / 100.0)

        if self.zoom_factor != 1.0:
            w, h = img.size
            img = img.resize((int(w * self.zoom_factor), int(h * self.zoom_factor)))

        img_qt = QImage(img.tobytes(), img.width, img.height, 3 * img.width, QImage.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(img_qt))

    def apply_filter(self):
        filter_name = self.filter_combo.currentText()
        if filter_name == "None":
            self.apply_adjustments()
            return
        self.current_image = apply_filter_logic(self.image_data, self.band_names, filter_name)
        self.zoom_factor = 1.0
        self.apply_adjustments()

    def save_image(self):
        if self.current_image:
            path, _ = QFileDialog.getSaveFileName(self, "Save Image", "output.png", "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg)")
            if path:
                self.current_image.save(path)

    def zoom_in(self):
        self.zoom_factor *= 1.25
        self.apply_adjustments()

    def zoom_out(self):
        self.zoom_factor /= 1.25
        self.apply_adjustments()

    def rotate_image(self):
        if self.current_image:
            self.current_image = self.current_image.rotate(90, expand=True)
            self.apply_adjustments()

    def crop_image(self):
        if self.current_image:
            w, h = self.current_image.size
            crop_size = min(w, h) // 2
            left = (w - crop_size) // 2
            top = (h - crop_size) // 2
            self.current_image = self.current_image.crop((left, top, left + crop_size, top + crop_size))
            self.apply_adjustments()
