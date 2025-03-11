import sys
import os
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QFileDialog
from PySide6.QtUiTools import QUiLoader
from video_processor import VideoProcessor
import ocr_logger

class MainUI:
    def __init__(self):
        self.file_path = None
        
        loader = QUiLoader()
        self.ui = loader.load("mainwindow.ui")  
        self.ui.load_video.clicked.connect(self.open_file_browser)
        self.ui.full_frame.checkStateChanged.connect(self.update_button)

    def open_file_browser(self):
        self.file_path, _ = QFileDialog.getOpenFileName(
            self.ui,  
            "Select a Video File", 
            "", 
            "Video Files (*.mp4 *.avi *.mkv *.mov *.flv *.wmv *.webm)"
        )
        if self.file_path:
            vp = VideoProcessor(self.file_path)
            self.ui.label_filename_dyn.setText(str(os.path.join(os.path.basename(os.path.dirname(self.file_path)),
                                                     os.path.basename(self.file_path))))
            self.ui.label_fps_dyn.setText(str(vp.fps))
            self.ui.label_size_dyn.setText(str(round(os.path.getsize(self.file_path)/(1024*1024), 2)) + " " + "MB")
            self.ui.label_duration_dyn.setText(str(vp.duration)[:-4])
            self.ui.set_roi.setEnabled(True)
            self.ui.full_frame.setEnabled(True)
    
    def update_button(self, state):
        self.ui.set_roi.setText("Full frame scan" if state == Qt.Checked else "Set ROI")



app = QApplication(sys.argv)
window = MainUI()
window.ui.show()  
sys.exit(app.exec())
