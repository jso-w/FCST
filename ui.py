import sys
from PySide6.QtWidgets import QApplication, QFileDialog, QMainWindow, QPushButton, QStackedWidget
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

class MainUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FCST - CCTV Scanning Tool")
        self.setGeometry(400,400,600,600)

        self.central_stack = QStackedWidget(parent = self)

        self.fs_button = QPushButton("Choose video file.", parent = self)
        self.fs_button.setGeometry(200, 200, 50, 50)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_ui = MainUI()
    main_ui.show()
    sys.exit(app.exec())