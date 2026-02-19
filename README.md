# FCST (Frank's CCTV Scanning Tool)

FCST is a video-to-text utility designed to automate text extraction from screen recordings.

---
# WORK IN PROGRESS

## Features

* **Video Ingestion:** Load standard video files for processing.
* **Area Selection:** Interactive UI to select a specific bounding box on the first frame.
* **Frame Decomposition:** Automatically breaks down the video into individual frames
* **OCR Processing:** Powered by a **bundled Tesseract-OCR binary**.
* **Data Export:** Generates a clean text file containing all detected text strings.

---

## Project Status: Work in Progress

This is a **personal project** currently under active development.

> [!IMPORTANT]
> **Usage Note:** Detailed user documentation and "Basic Usage" instructions are currently omitted

**Current Development Focus:**
* **Bundling:** Ensuring all dependencies (including the Tesseract binary) remain portable.
* **Optimization:** Improving processing speed relative to video length.
* **Accuracy:** Refining OCR performance on varying game UI font styles.

---

## Prerequisites

* **Python 3.x**
* **Self-Contained:** All major dependencies and the Tesseract engine are bundled within the project repository for a "plug-and-play" experience.

---

## Roadmap

* [ ] Multi-thread the frame decomposition for faster processing.
* [ ] Add "Batch Mode" for processing multiple clips at once.
* [ ] Implement image pre-processing (grayscale/thresholding) to improve OCR hit rates imperfect or low-res frames.

---
