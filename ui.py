import sys
import cv2
from PySide6.QtWidgets import QApplication, QFileDialog
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

class MainUI:
    def __init__(self):
        self.app = QApplication(sys.argv)

    video_path = QFileDialog.getOpenFileName()

