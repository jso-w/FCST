import cv2

class VideoProcessor:
    def __init__(self, video_path):
        self.video_path = video_path
        self.vid = cv2.VideoCapture(self.video_path)
        if not self.vid.isOpened:
            raise ValueError("Video could not be loaded. :(")
        self.frames_total = self.vid.get(cv2.CAP_PROP_FRAME_COUNT)
        self.fps = self.vid.get(cv2.CAP_PROP_FPS)
        self.first_frame = self.get_first_frame

    def get_video(self):
        return self.vid

    def get_fps(self):
        return self.fps
    
    def release_video(self):
        if self.vid.isOpened:
            self.vid.release

    def get_first_frame(self):
        ret, frame = self.vid.cv2.read()
        if not ret:
            return False
        return frame
    
