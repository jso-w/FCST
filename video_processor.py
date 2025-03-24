
import os
import cv2
import pytesseract
from datetime import timedelta
import pandas as pd

pytesseract.pytesseract.tesseract_cmd = os.path.join(os.path.dirname(__file__), 'Tesseract-OCR', 'tesseract.exe')

class VideoProcessor:
    
    def __init__(self, video_path):
        self.video_path = video_path
        self.vid = cv2.VideoCapture(self.video_path)
        if not self.vid.isOpened():
            raise ValueError("Video could not be loaded.")
        self.frames_total = self.vid.get(cv2.CAP_PROP_FRAME_COUNT)
        self.fps = self.vid.get(cv2.CAP_PROP_FPS)
        self.first_frame = self.get_first_frame()
        self.size = os.path.getsize(self.video_path)
        self.duration = timedelta(seconds = (self.frames_total/self.fps))

        self.text_array = []

    def get_video(self):
        return self.vid

    def get_fps(self):
        return self.fps
    
    def release_video(self):
        if self.vid.isOpened():
            self.vid.release()

    def get_first_frame(self):
        self.vid.set(cv2.CAP_PROP_POS_FRAMES, 0)
        _, frame = self.vid.read()
        if not _:
            return False
        return frame
    
    def run_scan(self, frame_skip, roi, progress_callback):
        
        frame_i = 0
        while(self.vid.isOpened()):
            self.vid.set(cv2.CAP_PROP_POS_FRAMES, frame_i)
            check, frame = self.vid.read()

            if not check:
                break

            frame_roi = frame[roi]
            frame_gray = cv2.cvtColor(frame_roi, cv2.COLOR_BGR2GRAY)
            frame_resized = cv2.resize(frame_gray, None, fx = 4, fy = 4, interpolation=(cv2.INTER_LINEAR))
            _, frame_proc = cv2.threshold(frame_resized, 150, 255, cv2.THRESH_BINARY)
            frame_text = pytesseract.image_to_string(frame_proc, config="--psm 6")
            
            if progress_callback:
                progress_callback(int((frame_i / self.frames_total) * 100))

            if frame_text:
                timecode = str(timedelta(seconds = frame_i / self.fps))
                self.text_array.append((frame_text, frame_i))

            frame_i += frame_skip
        self.release_video()
    
    def get_text(self):
        return self.text_array