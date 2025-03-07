import pytesseract
import cv2
import video_processor

def ocr_frame(frame_roi):
    frame_text = pytesseract.image_to_string(frame_roi, config='--psm 6')
    return frame_text

print(cv2.getBuildInformation())