# Video Processing Tool

A powerful video processing tool built with Python, OpenCV, and PyQt5.

## Features

- Video playback with basic controls
- Drag and drop video file support
- Space bar for play/pause
- Time slider for navigation
- BGR to RGB color conversion
- Multiple processing modules:
  - Segment (Time-based extraction)
  - Screenshot
  - Clip Frame
  - Resize Frame
  - Speed adjustment

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python main.py
```

### Basic Controls
- Drag and drop video files into the window
- Space bar: Play/Pause
- Click and drag on the time slider to navigate
- Use the play/pause button for video control

### Processing Modules
1. Segment: Extract video segments
2. Screenshot: Save current frame
3. Clip Frame: Crop video frame
4. Resize Frame: Resize video dimensions
5. Speed: Adjust playback speed

## Requirements
- Python 3.7+
- OpenCV
- PyQt5
- NumPy 