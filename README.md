# Video Processing Tool

A cross-platform video processing tool built with Python and PyQt5.

## Features

- Video playback and frame-by-frame navigation
- Video segmentation
- Video cropping
- Video resizing
- Playback speed control
- Export to various formats (MP4, AVI, MKV, JPG, PNG)

## Building from Source

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Windows

1. Install Python from [python.org](https://www.python.org/downloads/)
2. Open Command Prompt and run:
```bash
python build.py
```

### macOS

1. Install Python using Homebrew:
```bash
brew install python
```
2. Open Terminal and run:
```bash
python3 build.py
```

### Linux (Ubuntu/Debian)

1. Install Python and required packages:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```
2. Open Terminal and run:
```bash
python3 build.py
```

## Running the Application

After building, you can find the executable in the `dist` directory:

- Windows: `dist/VideoProcessor.exe`
- macOS: `dist/VideoProcessor.app`
- Linux: `dist/VideoProcessor`

## Dependencies

The following dependencies will be automatically installed during the build process:

- PyQt5
- OpenCV
- NumPy
- PyInstaller

## Supported Video Formats

- MP4
- AVI
- MKV
- MOV

## Notes

- On macOS, you may need to grant security permissions to run the application
- On Linux, you may need to install additional codecs:
```bash
sudo apt install ubuntu-restricted-extras
```

## Troubleshooting

If you encounter any issues:

1. Make sure all dependencies are installed correctly
2. Check if your system has the required video codecs
3. Try running the Python script directly to see any error messages:
```bash
python main.py
``` 