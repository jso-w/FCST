import sys
import os
from PySide6.QtGui import QImage, QPixmap, QPainter, QPen
from PySide6.QtCore import Qt, QRect, QEvent, QObject, Signal
from PySide6.QtWidgets import QApplication, QFileDialog, QMainWindow, QLabel, QVBoxLayout, QPushButton, QWidget
from PySide6.QtUiTools import QUiLoader
import video_processor
from video_processor import VideoProcessor
import ocr_logger
import cv2

class MainUI:
    def __init__(self):
        self.file_path = None
        self.vp = None
        loader = QUiLoader()
        self.ui = loader.load("mainwindow.ui")

        self.ui.load_video.clicked.connect(self.open_file_browser)
        self.ui.set_roi.clicked.connect(self.set_roi)
        self.ui.full_frame.stateChanged.connect(self.update_button)

    def open_file_browser(self):
        self.file_path, _ = QFileDialog.getOpenFileName(
            self.ui,
            "Select a Video File",
            "",
            "Video Files (*.mp4 *.avi *.mkv *.mov *.flv *.wmv *.webm)"
        )
        if self.file_path:
            self.vp = VideoProcessor(self.file_path)
            self.ui.label_filename_dyn.setText(str(os.path.join(os.path.basename(os.path.dirname(self.file_path)),
                                                     os.path.basename(self.file_path))))
            self.ui.label_fps_dyn.setText(str(self.vp.fps))
            self.ui.label_size_dyn.setText(str(round(os.path.getsize(self.file_path)/(1024*1024), 2)) + " MB")
            self.ui.label_duration_dyn.setText(str(self.vp.duration)[:-4])
            self.ui.set_roi.setEnabled(True)
            self.ui.full_frame.setEnabled(True)

    def set_roi(self):
        if self.ui.full_frame.isChecked():
            self.proceed_normally()
            return

        if self.vp.first_frame is None:
            print("Error loading first frame.")
            return

        self.scale_factor = 0.75
        frame_resized = cv2.resize(
            self.vp.first_frame, None, fx=self.scale_factor, fy=self.scale_factor, interpolation=cv2.INTER_LINEAR
        )
        frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)

        height, width, channel = frame_rgb.shape
        bytes_per_line = channel * width
        q_img = QImage(frame_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)

        # Set up the ROI window
        self.roi_window = QWidget()
        self.roi_window.setWindowTitle("Select ROI")

        # Properly set up layout
        layout = QVBoxLayout(self.roi_window)  # Pass the widget to layout directly
        self.roi_window.setLayout(layout)      # Explicitly set the layout

        # Initialize QLabel with the pixmap
        self.label = QLabel()
        pixmap = QPixmap.fromImage(q_img)
        self.label.setPixmap(pixmap)
        layout.addWidget(self.label)

        # Properly initialize ROI selector and connect signals
        self.roi_selector = ROISelector(self.label, self.scale_factor)
        self.roi_selector.roi_selected.connect(self.on_roi_selected)
        self.label.installEventFilter(self.roi_selector)

        # Ensure window is correctly sized
        self.roi_window.resize(pixmap.width(), pixmap.height())
        self.roi_window.show()

    def on_roi_selected(self, roi):
        print("Final ROI received:", roi)

    def update_button(self, state):
        self.ui.set_roi.setText("Full frame scan" if state == Qt.Checked else "Set ROI")


class ROISelector(QObject):
    roi_selected = Signal(tuple)

    def __init__(self, label, scale_factor):
        super().__init__(label)
        self.label = label
        self.scale_factor = scale_factor
        self.start_point = None
        self.end_point = None
        self.drawing = False
        self.base_pixmap = self.label.pixmap().copy()
        self.temp_pixmap = self.base_pixmap.copy()

    def eventFilter(self, obj, event):
        if obj == self.label:
            if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                self.start_point = event.pos()
                self.drawing = True
                self.temp_pixmap = self.base_pixmap.copy()
                return True

            elif event.type() == QEvent.MouseMove and self.drawing:
                self.end_point = event.pos()
                self.update_rectangle()
                return True

            elif event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
                self.drawing = False
                self.end_point = event.pos()
                self.finalize_roi()
                return True
        return False

    def update_rectangle(self):
        pixmap = self.base_pixmap.copy()
        painter = QPainter(pixmap)
        pen = QPen(Qt.red, 2, Qt.SolidLine)
        painter.setPen(pen)
        rect = QRect(self.start_point, self.end_point).normalized()
        painter.drawRect(rect)
        painter.end()
        self.label.setPixmap(pixmap)

    def finalize_roi(self):
        rect = QRect(self.start_point, self.end_point).normalized()
        x1 = int(rect.left() / self.scale_factor)
        y1 = int(rect.top() / self.scale_factor)
        x2 = int(rect.right() / self.scale_factor)
        y2 = int(rect.bottom() / self.scale_factor)
        roi = (x1, y1, x2, y2)
        print(f"Selected ROI: {roi}")
        self.roi_selected.emit(roi)

app = QApplication(sys.argv)
window = MainUI()
window.ui.show()  
sys.exit(app.exec())
