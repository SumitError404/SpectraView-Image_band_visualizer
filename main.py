import sys
import subprocess
import numpy as np
import rasterio
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QComboBox, QFileDialog,
    QVBoxLayout, QHBoxLayout, QScrollArea, QMessageBox, QSlider, QToolBar, QAction, QDialog
)
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5.QtCore import Qt, QSize
from PIL import Image, ImageEnhance


class StartupDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Welcome to RGB and Band Image Visualizer")
        self.setFixedSize(500, 300)
        self.file_path = None

        layout = QVBoxLayout(self)

        title = QLabel("<h2>RGB and Band Image Visualizer</h2>")
        title.setAlignment(Qt.AlignCenter)

        instructions = QLabel("""
        <p>This tool lets you:</p>
        <ul>
            <li>Select bands to create RGB composites</li>
            <li>View single band images</li>
            <li>Apply vegetation and water filters</li>
            <li>Adjust brightness, contrast, and sharpness</li>
        </ul>
        <p>Please upload an image to get started.</p>
        """)
        instructions.setWordWrap(True)

        upload_button = QPushButton("Upload Image")
        upload_button.setFixedSize(150, 40)
        upload_button.clicked.connect(self.upload_image)

        layout.addWidget(title)
        layout.addWidget(instructions)
        layout.addWidget(upload_button, alignment=Qt.AlignCenter)

    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", 
                        "Image Files (*.tif *.tiff *.jp2 *.jpg *.jpeg *.png *.bmp *.gif *.img)")
        if file_path:
            self.file_path = file_path
            self.accept()


class BandVisualizer(QWidget):
    def __init__(self, file_path):
        super().__init__()
        self.setWindowTitle("RGB and Band Image Visualizer")
        self.resize(1200, 800)

        self.file_path = file_path
        self.image_data = None
        self.current_image = None
        self.zoom_factor = 1.0
        self.undo_stack = []
        self.redo_stack = []

        self.main_layout = QVBoxLayout(self)
        self.top_controls = QHBoxLayout()
        self.middle_layout = QHBoxLayout()
        self.bottom_controls = QHBoxLayout()

        self.init_top_toolbar()

        self.controls_layout = QVBoxLayout()
        self.image_layout = QVBoxLayout()

        self.init_band_selectors()
        self.init_filters()
        self.init_sliders()

        self.show_composite_button = QPushButton("Show Composite RGB Image")
        self.show_composite_button.clicked.connect(self.show_rgb_image)
        self.controls_layout.addWidget(self.show_composite_button)

        self.image_label = QLabel(alignment=Qt.AlignCenter)
        scroll = QScrollArea(widgetResizable=True)
        scroll.setWidget(self.image_label)
        self.image_layout.addWidget(scroll)
        self.image_layout.addLayout(self.bottom_controls)

        self.middle_layout.addLayout(self.controls_layout, 1)
        self.middle_layout.addLayout(self.image_layout, 3)

        self.main_layout.addLayout(self.top_controls)
        self.main_layout.addLayout(self.middle_layout)

        self.load_image(self.file_path)
        self.init_bottom_controls()

    def init_top_toolbar(self):
        self.toolbar = QToolBar("Top Tools")
        self.toolbar.setIconSize(QSize(24, 24))

        save_action = QAction(QIcon.fromTheme("document-save"), "Save Image", self)
        save_action.triggered.connect(self.save_image)
        self.toolbar.addAction(save_action)

        restart_action = QAction(QIcon.fromTheme("system-reboot"), "Restart App", self)
        restart_action.triggered.connect(self.restart_app)
        self.toolbar.addAction(restart_action)

        info_action = QAction(QIcon.fromTheme("help-about"), "Band Info", self)
        info_action.triggered.connect(self.show_info_popup)
        self.toolbar.addAction(info_action)

        self.top_controls.addWidget(self.toolbar)

    def show_info_popup(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Sentinel vs Landsat Band Info")
        layout = QVBoxLayout(dialog)

        image_label = QLabel()
        pixmap = QPixmap("sentinel_landsat_band_comparison.jpg")
        if pixmap.isNull():
            image_label.setText("Failed to load image.")
        else:
            image_label.setPixmap(pixmap.scaledToWidth(700, Qt.SmoothTransformation))

        layout.addWidget(image_label)
        dialog.exec_()

    def load_image(self, file_path):
        try:
            self.src = rasterio.open(file_path)
            self.image_data = [self.src.read(i) for i in range(1, self.src.count + 1)]
            self.band_names = (
                [desc if desc and desc.strip() else f"Band {i+1}" for i, desc in enumerate(self.src.descriptions)]
                if self.src.descriptions else [f"Band {i+1}" for i in range(self.src.count)]
            )
            self.update_band_selectors()
            QMessageBox.information(self, "Success", f"Loaded image with {self.src.count} band(s).")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load image: {e}")

    def init_band_selectors(self):
        self.band_select_layout = QHBoxLayout()
        self.r_band_combo, self.g_band_combo, self.b_band_combo = QComboBox(), QComboBox(), QComboBox()
        for label, combo in zip(["Red:", "Green:", "Blue:"], [self.r_band_combo, self.g_band_combo, self.b_band_combo]):
            self.band_select_layout.addWidget(QLabel(label))
            self.band_select_layout.addWidget(combo)
        self.controls_layout.addLayout(self.band_select_layout)

        self.single_band_combo = QComboBox()
        self.single_band_combo.currentIndexChanged.connect(self.show_single_band)
        self.controls_layout.addWidget(QLabel("View Single Band:"))
        self.controls_layout.addWidget(self.single_band_combo)

    def update_band_selectors(self):
        for combo in [self.r_band_combo, self.g_band_combo, self.b_band_combo, self.single_band_combo]:
            combo.clear()
        for i, name in enumerate(self.band_names):
            for combo in [self.r_band_combo, self.g_band_combo, self.b_band_combo, self.single_band_combo]:
                combo.addItem(name, i)

    def init_filters(self):
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "None", "Vegetation Highlight", "Natural Color", "Urban/Soil",
            "Water Bodies", "Healthy Vegetation Contrast", "NDVI Enhanced",
            "SAVI (Soil-Adjusted Vegetation Index)", "EVI (Enhanced Vegetation Index)"
        ])
        self.filter_combo.currentIndexChanged.connect(self.apply_filter)
        self.controls_layout.addWidget(QLabel("Apply Filter:"))
        self.controls_layout.addWidget(self.filter_combo)

    def init_sliders(self):
        self.brightness_slider = self.create_slider("Brightness", self.apply_adjustments)
        self.contrast_slider = self.create_slider("Contrast", self.apply_adjustments)
        self.sharpness_slider = self.create_slider("Sharpness", self.apply_adjustments)

    def create_slider(self, label, slot):
        self.controls_layout.addWidget(QLabel(label))
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(50)
        slider.setMaximum(150)
        slider.setValue(100)
        slider.setTickInterval(10)
        slider.valueChanged.connect(slot)
        self.controls_layout.addWidget(slider)
        return slider

    def init_bottom_controls(self):
        buttons = [
            ("zoom-in", "Zoom In", self.zoom_in),
            ("zoom-out", "Zoom Out", self.zoom_out),
            ("object-rotate-right", "Rotate", self.rotate_image),
            ("edit-undo", "Undo", self.undo),
            ("edit-redo", "Redo", self.redo),
        ]
        for icon, label, slot in buttons:
            btn = QPushButton(label)
            btn.setIcon(QIcon.fromTheme(icon))
            btn.setIconSize(QSize(24, 24))
            btn.clicked.connect(slot)
            self.bottom_controls.addWidget(btn)

    def normalize_band(self, band):
        band = band.astype(np.float32)
        return (band - band.min()) / (band.max() - band.min() + 1e-6)

    def push_undo(self):
        if self.current_image:
            self.undo_stack.append(self.current_image.copy())
            self.redo_stack.clear()

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(self.current_image.copy())
            self.current_image = self.undo_stack.pop()
            self.apply_adjustments()

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(self.current_image.copy())
            self.current_image = self.redo_stack.pop()
            self.apply_adjustments()

    def show_rgb_image(self):
        if not self.image_data:
            return
        indices = [combo.currentData() for combo in [self.r_band_combo, self.g_band_combo, self.b_band_combo]]
        rgb = np.stack([self.normalize_band(self.image_data[i]) for i in indices], axis=-1)
        self.push_undo()
        self.current_image = Image.fromarray((rgb * 255).astype(np.uint8))
        self.zoom_factor = 1.0
        self.apply_adjustments()

    def show_single_band(self):
        if not self.image_data:
            return
        band = self.normalize_band(self.image_data[self.single_band_combo.currentData()])
        self.push_undo()
        self.current_image = Image.fromarray((band * 255).astype(np.uint8)).convert('RGB')
        self.zoom_factor = 1.0
        self.apply_adjustments()

    def apply_adjustments(self):
        if not self.current_image:
            return
        img = self.current_image.copy()
        for enhancer, value in zip(
            [ImageEnhance.Brightness, ImageEnhance.Contrast, ImageEnhance.Sharpness],
            [self.brightness_slider.value(), self.contrast_slider.value(), self.sharpness_slider.value()]):
            img = enhancer(img).enhance(value / 100.0)
        if self.zoom_factor != 1.0:
            w, h = img.size
            img = img.resize((int(w * self.zoom_factor), int(h * self.zoom_factor)))
        img_qt = QImage(img.tobytes(), img.width, img.height, 3 * img.width, QImage.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(img_qt))

    def apply_filter(self):
        if not self.image_data or self.filter_combo.currentText() == "None":
            self.apply_adjustments()
            return
        if len(self.image_data) < 4:
            QMessageBox.warning(self, "Filter Warning", "At least 4 bands are needed for advanced filters.")
            return

        try:
            names = {name.lower(): i for i, name in enumerate(self.band_names)}
            red, green, blue, nir = [
                self.normalize_band(self.image_data[names.get(k, i)])
                for i, k in enumerate(["red", "green", "blue", "nir"])
            ]
            filt = self.filter_combo.currentText()
            self.push_undo()
            if filt == "Vegetation Highlight":
                self.current_image = Image.fromarray((np.stack([nir, red, green], -1) * 255).astype(np.uint8))
            elif filt == "Natural Color":
                self.current_image = Image.fromarray((np.stack([red, green, blue], -1) * 255).astype(np.uint8))
            elif filt == "Urban/Soil":
                fifth = self.normalize_band(self.image_data[4]) if len(self.image_data) > 4 else nir
                self.current_image = Image.fromarray((np.stack([fifth, red, green], -1) * 255).astype(np.uint8))
            elif filt == "Water Bodies":
                water = (blue - nir)
                self.current_image = Image.fromarray((water * 255).clip(0, 255).astype(np.uint8)).convert("RGB")
            elif filt == "Healthy Vegetation Contrast":
                contrast = (nir - red)
                self.current_image = Image.fromarray((contrast * 255).clip(0, 255).astype(np.uint8)).convert("RGB")
            elif filt == "NDVI Enhanced":
                ndvi = (nir - red) / (nir + red + 1e-6)
                ndvi_color = np.stack([ndvi, ndvi ** 2, ndvi ** 3], -1)
                self.current_image = Image.fromarray((ndvi_color * 255).clip(0, 255).astype(np.uint8))
            elif filt == "SAVI (Soil-Adjusted Vegetation Index)":
                savi = ((nir - red) / (nir + red + 0.5)) * 1.5
                self.current_image = Image.fromarray((savi * 255).clip(0, 255).astype(np.uint8)).convert("RGB")
            elif filt == "EVI (Enhanced Vegetation Index)":
                evi = 2.5 * (nir - red) / (nir + 6 * red - 7.5 * blue + 1)
                self.current_image = Image.fromarray((evi * 255).clip(0, 255).astype(np.uint8)).convert("RGB")
            self.zoom_factor = 1.0
            self.apply_adjustments()
        except Exception as e:
            QMessageBox.critical(self, "Filter Error", f"Error applying filter: {e}")

    def save_image(self):
        if self.current_image:
            path, _ = QFileDialog.getSaveFileName(self, "Save Image", "output.png", 
                            "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg)")
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
            self.push_undo()
            self.current_image = self.current_image.rotate(90, expand=True)
            self.apply_adjustments()

    def restart_app(self):
        python_exe = sys.executable
        subprocess.Popen([python_exe] + sys.argv)
        QApplication.quit()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    startup = StartupDialog()
    if startup.exec_() == QDialog.Accepted and startup.file_path:
        viewer = BandVisualizer(startup.file_path)
        viewer.show()
        sys.exit(app.exec_())
