import sys
import os
from PySide6.QtGui import QImage, QPixmap, QPainter, QPen, QIcon
from PySide6.QtCore import Qt, QRect, QEvent, QObject, Signal, QThread
from PySide6.QtWidgets import QApplication, QFileDialog, QMainWindow, QLabel, QVBoxLayout, QPushButton, QWidget, QMessageBox, QHBoxLayout
from PySide6.QtUiTools import QUiLoader
from datetime import timedelta
from video_processor import VideoProcessor
import ocr_logger
import cv2

class MainUI:
    def __init__(self):
        self.selected_roi = None
        self.file_path = None
        self.vp = None
        loader = QUiLoader()
        self.ui = loader.load("mainwindow.ui")

        self.ui.load_video.clicked.connect(self.open_file_browser)
        self.ui.set_roi.clicked.connect(self.set_roi)
        self.ui.full_frame.stateChanged.connect(self.update_button)
        self.ui.start_scan.setEnabled(False)
        self.ui.start_scan.clicked.connect(self.start_scan)
        self.ui.actionHelp.triggered.connect(self.show_help_message)

    def open_file_browser(self):

        self.file_path, _ = QFileDialog.getOpenFileName(
            self.ui,
            "Select a Video File",
            "",
            "Video Files (*.mp4 *.avi *.mkv *.mov *.flv *.wmv *.webm)"
        )
        if self.file_path:
            self.vp = VideoProcessor(self.file_path)
            self.vid = cv2.VideoCapture(self.file_path)

            self.frames_total = self.vid.get(cv2.CAP_PROP_FRAME_COUNT)
            self.fps = self.vid.get(cv2.CAP_PROP_FPS)
            _, self.first_frame = self.vid.read()
            self.size = os.path.getsize(self.file_path)
            self.duration = timedelta(seconds = (self.frames_total/self.fps))

            self.ui.label_filename_dyn.setText(str(os.path.join(os.path.basename(os.path.dirname(self.file_path)),
                                                     os.path.basename(self.file_path))))
            self.ui.label_fps_dyn.setText(str(self.fps))
            self.ui.label_size_dyn.setText(str(round(os.path.getsize(self.file_path)/(1024*1024), 2)) + " MB")
            self.ui.label_duration_dyn.setText(str(self.duration)[:-4])
            self.ui.set_roi.setEnabled(True)
            self.ui.full_frame.setEnabled(True)

    def set_roi(self):
        if self.ui.full_frame.isChecked():
            return

        if self.first_frame is None:
            QMessageBox.warning(self.ui, "No frame", "Couldn't load video file.")
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
        layout = QVBoxLayout(self.roi_window)  
        self.roi_window.setLayout(layout)      

        # Initialize QLabel with the pixmap
        self.label = QLabel()
        pixmap = QPixmap.fromImage(q_img)
        self.label.setPixmap(pixmap)
        layout.addWidget(self.label)

        buttons_layout = QHBoxLayout()
        confirm_button = QPushButton("Confirm")
        cancel_button = QPushButton("Cancel")
        buttons_layout.addWidget(confirm_button)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)

        confirm_button.clicked.connect(self.confirm_roi)
        cancel_button.clicked.connect(self.cancel_roi)

        # Properly initialize ROI selector and connect signals
        self.roi_selector = ROISelector(self.label, self.scale_factor, pixmap.width(), pixmap.height())
        self.roi_selector.roi_selected.connect(self.on_roi_selected)
        self.label.installEventFilter(self.roi_selector)

        # Ensure window is correctly sized
        self.roi_window.resize(pixmap.width(), pixmap.height())
        self.roi_window.show()

    def on_roi_selected(self, roi):
        print("Final ROI received:", roi)

    def confirm_roi(self):
        roi = self.roi_selector.get_roi()
        if roi:
            self.selected_roi = roi
            QMessageBox.information(self.roi_window, "ROI Selected", f"ROI Successfully selected.")
            self.roi_window.close()
        else:
            QMessageBox.warning(self.roi_window, "No ROI", "Please select a ROI first.")
        self.update_start_button_state()

    def cancel_roi(self):
        self.selected_roi = None
        self.roi_window.close()
        self.update_start_button_state()

    def update_button(self, state):
        self.ui.set_roi.setText("Full frame scan" if state == Qt.Checked else "Set ROI")
        self.update_start_button_state()

    def update_start_button_state(self):
        can_scan = self.vp is not None and (self.selected_roi is not None or self.ui.full_frame.isChecked())
        self.ui.start_scan.setEnabled(can_scan)
    
    def start_scan(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.set_main_widgets(False)
        self.output_final = None
        frame_skip = self.ui.set_frame_skip.value()
        roi = self.selected_roi if not self.ui.full_frame.isChecked() else (slice(None), slice(None))

        self.worker = WorkerThread(self.file_path, frame_skip, roi)
        self.worker.ocr_signal.connect(self.scan_signal_handler)
        self.worker.progress_signal.connect(self.ui.scan_progress_bar.setValue)
        self.worker.start()

    def scan_signal_handler(self, ocr_list):
        self.output_final = ocr_logger.text_array_to_file(ocr_list)
        self.ui.scan_progress_bar.setValue(100)
        QMessageBox.information(self.ui, "Scan Complete", f"Scan results saved to {self.output_final}")
        self.ui.scan_progress_bar.setValue(0)
        QApplication.restoreOverrideCursor()
        self.set_main_widgets(True)

    def set_main_widgets(self, enabled: bool):
        for widget in self.ui.findChildren(QWidget):
            widget.setEnabled(enabled)
    
    def show_help_message(self):
        QMessageBox.information(
            self.ui,
            "How to Use",
            "The 'Frame Skip' setting determines how many frames the program skips between each OCR scan.\n\n"
            "- Higher values make the scan faster, but may miss content.\n"
            "- Lower values scan more thoroughly but take longer.\n\n"
            "Recommended: set it to approximately twice the video's framerate "
            "for a good balance between speed and accuracy."
        )
    
class ROISelector(QObject):
    roi_selected = Signal(tuple)

    def __init__(self, label, scale_factor, frame_width, frame_height):
        super().__init__(label)
        self.frame_width = frame_width
        self.frame_height = frame_height
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
                self.end_point.setX(min(max(self.end_point.x(), 0), self.frame_width - 1))
                self.end_point.setY(min(max(self.end_point.y(), 0), self.frame_height - 1))
                self.update_rectangle()
                return True

            elif event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
                self.drawing = False
                self.end_point = event.pos()
                self.end_point.setX(min(max(self.end_point.x(), 0), self.frame_width - 1))
                self.end_point.setY(min(max(self.end_point.y(), 0), self.frame_height - 1))
                
                self.final_roi = QRect(self.start_point, self.end_point).normalized() 
                
                self.update_rectangle()
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

    def get_roi(self):
        if hasattr(self, 'final_roi'):
            rect = self.final_roi
            x1 = int(rect.left() / self.scale_factor)
            y1 = int(rect.top() / self.scale_factor)
            x2 = int(rect.right() / self.scale_factor)
            y2 = int(rect.bottom() / self.scale_factor)
            return (slice(y1, y2), slice(x1, x2))
        return None

class WorkerThread(QThread):
    ocr_signal = Signal(list)
    progress_signal = Signal(int)

    def __init__(self, file_path, frame_skip, roi):
        super().__init__()
        self.file_path = file_path
        self.frame_skip = frame_skip
        self.roi = roi

    def run(self):
        self.vp_scan = VideoProcessor(self.file_path)
        self.vp_scan.run_scan(self.frame_skip, self.roi, self.progress_signal.emit)
        self.ocr_list = self.vp_scan.get_text()
        self.ocr_signal.emit(self.ocr_list)


app = QApplication(sys.argv)
window = MainUI()
window.ui.show()
sys.exit(app.exec())
