#Processes the video file & stores data

import cv2
import pytesseract
from datetime import timedelta

class VideoProcessor:

    def __init__(self, video_path):
        self.video_path = video_path
        self.vid = cv2.VideoCapture(self.video_path)
        if not self.vid.isOpened():
            raise ValueError("Video could not be loaded.")
        self.frames_total = self.vid.get(cv2.CAP_PROP_FRAME_COUNT)
        self.fps = self.vid.get(cv2.CAP_PROP_FPS)
        self.first_frame = self.get_first_frame()

    def get_video(self):
        return self.vid

    def get_fps(self):
        return self.fps
    
    def release_video(self):
        if self.vid.isOpened():
            self.vid.release()

    def get_first_frame(self):
        ret, frame = self.vid.cv2.read()
        if not ret:
            return False
        return frame
    
    def run_scan(self, frame_skip, roi):
        frame_count = 0
        while(self.vid.isOpened()):
            check, frame = self.vid.read()
            if not check:
                break
            frame_roi = frame[roi]
            cv2.cvtColor(frame_roi)
            cv2.resize(frame_roi, None, fx = 2, fy = 2, interpolation=(cv2.INTER_LINEAR))
            cv2.threshold(frame_roi, 150, 255, cv2.THRESH_BINARY)

            frame_text = pytesseract.image_to_string(frame_roi, config="--psm 6")

            if frame_text.strip():
                timecode = str(timedelta(seconds = frame_count / self.fps))
                frame_output.append({"Time": timecode, })
