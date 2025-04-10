import sys
from PyQt5.QtWidgets import QApplication
from gui import BandVisualizer

def main():
    app = QApplication(sys.argv)
    viewer = BandVisualizer()
    viewer.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

#main.py-->	Entry point of the app	Imports BandVisualizer from gui.py
#gui.py	GUI--> setup and user interaction	Imports utility functions from image_utils.py
#image_utils.py-->Handles image processing logic	Independent (just needs NumPy and PIL)